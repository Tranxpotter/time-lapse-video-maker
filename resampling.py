"""
Video → Images (time-accurate resampling)

- Supports .mp4 and .mov (and others supported by your OpenCV/FFmpeg build)
- Reads the video's original FPS (or timestamps) and resamples to a target FPS
- Outputs images numbered sequentially so you can recreate a smooth video at the new FPS

Example:
  python extract_frames_resampled.py input.mov --fps 12 -o out_frames --prefix frame --ext jpg

Re-encode with ffmpeg (example):
  ffmpeg -r 12 -i out_frames/frame_%06d.jpg -c:v libx264 -pix_fmt yuv420p output.mp4
"""

import argparse
import os
import sys
import math
import json
from typing import Optional, Tuple, List

import cv2


def human_fps(f: float) -> str:
    return f"{f:.6g} fps"


def ensure_outdir(path: str):
    os.makedirs(path, exist_ok=True)


def detect_src_fps(cap: cv2.VideoCapture) -> float:
    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    # Some backends can report 0 for VFR or unknown. We'll still try to use timestamps.
    return float(fps)


def detect_frame_count(cap: cv2.VideoCapture) -> int:
    cnt = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    try:
        cnt_i = int(cnt)
        return cnt_i if cnt_i > 0 else -1
    except Exception:
        return -1


def iter_frames_with_time(cap: cv2.VideoCapture, src_fps: float):
    """
    Iterate frames yielding (idx, time_sec, frame_bgr).
    Prefers CAP_PROP_POS_MSEC timestamps; falls back to idx/src_fps if needed.
    """
    idx = 0
    use_pos_msec = True  # try timestamps first; fallback if they look invalid
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        pos_msec = cap.get(cv2.CAP_PROP_POS_MSEC)
        t = None
        if use_pos_msec and pos_msec and pos_msec > 0:
            t = float(pos_msec) / 1000.0

        if t is None:
            if src_fps and src_fps > 0:
                t = idx / src_fps
            else:
                # As a last resort, assume constant 1s steps (not ideal).
                t = float(idx)

        yield idx, t, frame
        idx += 1


def choose_closest(prev: Tuple[int, float, 'ndarray'], cur: Tuple[int, float, 'ndarray'], target_t: float):
    """
    Choose between prev and cur frames based on which timestamp is closer to target_t.
    prev or cur can be None (on the first step).
    Returns a tuple (chosen_idx, chosen_t, chosen_frame, chosen_from) where chosen_from in {"prev","cur"}.
    """
    if prev is None:
        idx_c, t_c, f_c = cur
        return idx_c, t_c, f_c, "cur"
    if cur is None:
        idx_p, t_p, f_p = prev
        return idx_p, t_p, f_p, "prev"

    idx_p, t_p, f_p = prev
    idx_c, t_c, f_c = cur

    # If times are the same, prefer current to keep moving forward
    if abs(t_c - target_t) <= abs(target_t - t_p):
        return idx_c, t_c, f_c, "cur"
    else:
        return idx_p, t_p, f_p, "prev"


def save_image(frame, path: str, ext: str, jpg_quality: int, png_compression: int, webp_quality: int) -> bool:
    ext_l = ext.lower()
    params = []
    if ext_l in ("jpg", "jpeg"):
        params = [cv2.IMWRITE_JPEG_QUALITY, int(jpg_quality)]
    elif ext_l == "png":
        params = [cv2.IMWRITE_PNG_COMPRESSION, int(png_compression)]
    elif ext_l == "webp":
        params = [cv2.IMWRITE_WEBP_QUALITY, int(webp_quality)]
    # others: bmp, tiff etc. can use defaults
    return bool(cv2.imwrite(path, frame, params))


def compute_pad_width(frame_count_est: Optional[int], src_fps: float, target_fps: float) -> int:
    """
    Estimate how many output frames we'll create to choose a good zero-padding width.
    """
    if frame_count_est and frame_count_est > 0 and src_fps and src_fps > 0:
        # Duration ~ (N-1)/src_fps. Output frames ~ floor(last_time*target)+1
        duration = (frame_count_est - 1) / src_fps
        n_out_est = int(math.floor(duration * target_fps + 1e-9)) + 1
        return max(4, len(str(max(1, n_out_est))))
    # Fallback width
    return 6


def valid_ext(video_path: str) -> bool:
    ext = os.path.splitext(video_path)[1].lower()
    return ext in (".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm")


def extract_frames_resampled(
    video_path: str,
    out_dir: str,
    target_fps: float,
    prefix: str = "frame",
    ext: str = "jpg",
    jpg_quality: int = 95,
    png_compression: int = 3,
    webp_quality: int = 95,
    write_manifest: bool = True
) -> int:
    """
    Core routine. Returns the number of images written.
    """
    if target_fps <= 0:
        raise ValueError("Target FPS must be > 0")

    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Input not found: {video_path}")

    if not valid_ext(video_path):
        print("Warning: Input extension is not .mp4/.mov; attempting to process anyway.", file=sys.stderr)

    ensure_outdir(out_dir)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    src_fps = detect_src_fps(cap)
    frame_count_est = detect_frame_count(cap)

    pad_width = compute_pad_width(frame_count_est, src_fps, target_fps)

    print(f"Source FPS      : {human_fps(src_fps) if src_fps > 0 else 'unknown (using timestamps if available)'}")
    print(f"Target FPS      : {human_fps(target_fps)}")
    if src_fps > 0:
        ratio = target_fps / src_fps
        if ratio < 1:
            print(f"Resampling      : downsample (~{ratio:.3f}x)")
        elif ratio > 1:
            print(f"Resampling      : upsample (~{ratio:.3f}x, frames will repeat)")
        else:
            print("Resampling      : same FPS")
    print(f"Output directory: {out_dir}")
    print(f"Filename pattern: {prefix}_%0{pad_width}d.{ext.lower()}")

    # Target timeline
    delta_out = 1.0 / target_fps
    k = 0
    next_t = 0.0

    prev_tuple = None  # (idx, t, frame)
    last_tuple = None  # last seen (idx, t, frame)

    manifest: List[dict] = []
    written = 0

    def write_out(chosen_idx: int, chosen_t: float, chosen_frame, chosen_from: str, k_out: int):
        nonlocal written
        fname = f"{prefix}_{k_out:0{pad_width}d}.{ext.lower()}"
        fpath = os.path.join(out_dir, fname)
        ok = save_image(chosen_frame, fpath, ext, jpg_quality, png_compression, webp_quality)
        if not ok:
            raise IOError(f"Failed to write image: {fpath}")
        written += 1
        if write_manifest:
            manifest.append({
                "out_index": k_out,
                "out_time": k_out / target_fps,
                "src_index": int(chosen_idx),
                "src_time": float(chosen_t),
                "chosen_from": chosen_from,
                "filename": fname,
            })

    # Iterate frames and output nearest frames to target timestamps
    for cur_idx, cur_t, cur_frame in iter_frames_with_time(cap, src_fps):
        # For all target timestamps that are <= current frame's time, decide closest
        while next_t <= cur_t + 1e-12:  # small epsilon
            chosen_idx, chosen_t, chosen_frame, chosen_from = choose_closest(prev_tuple, (cur_idx, cur_t, cur_frame), next_t)
            write_out(chosen_idx, chosen_t, chosen_frame, chosen_from, k)
            k += 1
            next_t = k * delta_out
        prev_tuple = (cur_idx, cur_t, cur_frame)
        last_tuple = prev_tuple

    cap.release()

    if last_tuple is None:
        print("No frames read. Exiting.")
        return 0

    # After reading all frames, fill any remaining outputs up to the video's last timestamp
    last_idx, last_t, last_frame = last_tuple
    # Output up to floor(last_t * target_fps) + 1 frames (from t=0 to t=last_t inclusive).
    k_target = int(math.floor(last_t * target_fps + 1e-9)) + 1

    while k < k_target:
        write_out(last_idx, last_t, last_frame, "last", k)
        k += 1
        next_t = k * delta_out

    # Write manifest JSON
    if write_manifest:
        manifest_path = os.path.join(out_dir, f"{prefix}_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump({
                "input": os.path.abspath(video_path),
                "source_fps_reported": src_fps,
                "target_fps": target_fps,
                "frames_written": written,
                "files_prefix": prefix,
                "files_extension": ext.lower(),
                "pad_width": pad_width,
                "mapping": manifest
            }, f, indent=2)
        print(f"Manifest written: {manifest_path}")

    print(f"Done. Wrote {written} images.")
    return written


def main():
    parser = argparse.ArgumentParser(
        description="Extract images from video resampled to a target FPS (time-aligned)."
    )
    parser.add_argument("input", help="Path to input video (.mp4, .mov, etc.)")
    parser.add_argument("-o", "--outdir", default="frames_out", help="Output directory for images")
    parser.add_argument("-f", "--fps", type=float, required=True, help="Target FPS for extracted images")
    parser.add_argument("--prefix", default="frame", help="Filename prefix (default: frame)")
    parser.add_argument("--ext", default="jpg", choices=["jpg", "jpeg", "png", "bmp", "webp", "tiff"],
                        help="Image format/extension (default: jpg)")
    parser.add_argument("--jpg-quality", type=int, default=95, help="JPEG quality (0-100, default 95)")
    parser.add_argument("--png-compression", type=int, default=3, help="PNG compression (0-9, default 3)")
    parser.add_argument("--webp-quality", type=int, default=95, help="WebP quality (0-100, default 95)")
    parser.add_argument("--no-manifest", action="store_true", help="Do not write the JSON manifest")

    args = parser.parse_args()

    try:
        extract_frames_resampled(
            video_path=args.input,
            out_dir=args.outdir,
            target_fps=args.fps,
            prefix=args.prefix,
            ext=args.ext,
            jpg_quality=args.jpg_quality,
            png_compression=args.png_compression,
            webp_quality=args.webp_quality,
            write_manifest=(not args.no_manifest),
        )
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
from __future__ import annotations
import pygame
import pygame_gui
from pygame_gui.core import ObjectID, UIElement
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import threading
import cv2
import numpy as np

from .scene import Scene
from .utils import scroll_to_index



from typing import TYPE_CHECKING, Dict
if TYPE_CHECKING:
    from ..app import App
    from .scene2 import Scene2


class ExportScreen(pygame_gui.elements.UIPanel):
    def __init__(self, app:App, manager:pygame_gui.UIManager, scene2:Scene2, anchor_target):
        self.app = app
        self.manager = manager
        self.scene2 = scene2
        super().__init__(relative_rect=pygame.Rect(0, 0, 1080, 650),
                         manager=self.manager, 
                         anchors={"left":"left", "right":"right", "top":"top", "top_target":anchor_target})
        
    
        self.export_video_resolution_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(30, 0, 1050, 50), 
            text=f"Video Resolution: {self.video_resolution[0]}x{self.video_resolution[1]}", 
            manager = self.manager, 
            container = self, 
            anchors = {"left":"left", "top":"top"}, 
            object_id=ObjectID(class_id="@export_info_label", object_id="#export_video_resolution_label")
        )
        
        self.export_video_fps_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(30, 0, 1050, 50), 
            text=f"Frames per Second: {self.fps}", 
            manager = self.manager, 
            container = self, 
            anchors = {"left":"left", "top":"top", "top_target":self.export_video_resolution_label}, 
            object_id=ObjectID(class_id="@export_info_label", object_id="#export_video_fps_label")
        )
        
        self.export_video_img_count_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(30, 0, 1050, 50), 
            text=f"Number of Images: {len(self.image_paths)}", 
            manager = self.manager, 
            container = self, 
            anchors = {"left":"left", "top":"top", "top_target":self.export_video_fps_label}, 
            object_id=ObjectID(class_id="@export_info_label", object_id="#export_video_img_count_label")
        )

        video_length = round(len(self.image_paths) / self.fps, 1) if self.fps != 0 else "--"
        self.export_video_length_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(30, 0, 1050, 50), 
            text=f"Video Length (in seconds): {video_length}", 
            manager = self.manager, 
            container = self, 
            anchors = {"left":"left", "top":"top", "top_target":self.export_video_img_count_label}, 
            object_id=ObjectID(class_id="@export_info_label", object_id="#export_video_length_label")
        )
        
        self.export_video_anti_flickering_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(30, 0, 1050, 50), 
            text=f"Anti-flickering: {self.anti_flickering}", 
            manager = self.manager, 
            container = self, 
            anchors = {"left":"left", "top":"top", "top_target":self.export_video_length_label}, 
            object_id=ObjectID(class_id="@export_info_label", object_id="#export_video_anti_flickering_label")
        )
        next_target = self.export_video_anti_flickering_label
        
        if self.anti_flickering == "On":
            self.export_video_anti_flickering_sample_size_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(30, 0, 1050, 50), 
                text=f"Anti-flickering Sample Size: {self.anti_flickering_sample_size}", 
                manager = self.manager, 
                container = self, 
                anchors = {"left":"left", "top":"top", "top_target":self.export_video_anti_flickering_label}, 
                object_id=ObjectID(class_id="@export_info_label", object_id="#export_video_anti_flickering_sample_size_label")
            )
            next_target = self.export_video_anti_flickering_sample_size_label

        
        self.export_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 10, 100, 50), 
            text="Export", 
            manager = self.manager, 
            container = self, 
            anchors = {"centerx":"centerx", "top":"top", "top_target":next_target}, 
            object_id=ObjectID(class_id="@button", object_id="#export_button")
        )
        
        error_msg = ""
        if not self.check_resolution_valid():
            error_msg += "Video resolution is invalid.\n"
        if self.fps == 0:
            error_msg += "Video fps is invalid.\n"
        
        if error_msg:
            self.export_error_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, 10, 1050, 200), 
                text=error_msg, 
                manager = self.manager, 
                container = self, 
                anchors = {"left":"left", "top":"top", "top_target":self.export_button}, 
                object_id=ObjectID(class_id="@button", object_id="#export_button")
            )
            self.export_button.disable()
    
    @property
    def image_fitting_rule(self):
        return self.scene2.image_fitting_rule
    
    @property
    def video_resolution(self):
        return self.scene2.video_resolution
    
    @property
    def fps(self):
        return self.scene2.fps
    
    @property
    def image_paths(self):
        return self.scene2.image_paths
    
    @property
    def anti_flickering(self):
        return self.scene2.anti_flickering
    
    @property
    def anti_flickering_sample_size(self):
        return self.scene2.anti_flickering_sample_size

    
    def check_resolution_valid(self):
        '''Check if the resolution entered is valid, returns True if valid, False otherwise'''
        if self.video_resolution[0] == 0 or self.video_resolution[1] == 0:
            return False
        return True
    
    
    
    def export_image_process(self, image, image_path, display_details):
        # topleft = display_details[image_path]["top_left"]
        relative_center = display_details[image_path]["relative_center"]
        zoom_level = display_details[image_path]["zoom_level"]
        
        image_height, image_width, channel = image.shape
        

        width_ratio = self.video_resolution[0] / image_width
        height_ratio = self.video_resolution[1] / image_height
        if self.image_fitting_rule == "Fit":
            scaling_ratio = min(width_ratio, height_ratio)
        else:
            scaling_ratio = max(width_ratio, height_ratio)
        image_base_width = round(self.video_resolution[0] / scaling_ratio)
        image_base_height = round(self.video_resolution[1] / scaling_ratio)

        if image_base_width > image_width or image_base_height > image_height:
            # Create a black background
            background = np.zeros((image_base_height, image_base_width, 3), dtype=np.uint8)

            # Choose top-left corner for placement
            x_offset, y_offset = round((image_base_width - image_width) / 2), round((image_base_height - image_height) / 2)
            # Overlay the image onto the background
            background[y_offset:y_offset+image_height, x_offset:x_offset+image_width] = image
            image = background
            image_width = image_base_width
            image_height = image_base_height
            





        
        crop_width, crop_height = self.scene2.calc_zoom_value(zoom_level, image_base_width), self.scene2.calc_zoom_value(zoom_level, image_base_height)
        
        topleft = self.scene2.get_topleft_from_relc(relative_center, image_width, image_height, crop_width, crop_height)
        cropped_image = image[topleft[1]:topleft[1]+crop_height, topleft[0]:topleft[0]+crop_width]
        resized_image = cv2.resize(cropped_image, self.video_resolution)
        return resized_image
    
    
    
    def export_video(self, filepath):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or use 'XVID' for .avi
        video = cv2.VideoWriter(filepath, fourcc, self.fps, self.video_resolution)
        display_details = self.scene2.panning_to_display_details()
        
        if self.anti_flickering == "Off":
        
            for index, image_path in enumerate(self.image_paths):
                frame = cv2.imread(image_path)
                resized_frame = self.export_image_process(frame, image_path, display_details)
                video.write(resized_frame)
                self.export_progress_display.set_text(f"Export Progress: {index+1}/{len(self.image_paths)}")
        
        
        else:
            anti_flickering_sample_size = int(self.anti_flickering_sample_size)
            first_frame_image_paths = self.image_paths[:(anti_flickering_sample_size+1)//2]
            
            frame_images = [self.export_image_process(cv2.imread(img_path), img_path, display_details) for img_path in first_frame_image_paths]

            for frame_index in range(len(self.image_paths)):
                frame = frame_images[0]
                for i in range(len(frame_images)):
                    if i == 0:
                        continue
                    beta = 1.0/(i+1)
                    
                    alpha = 1.0 - beta
                    
                    frame = cv2.addWeighted(frame, alpha, frame_images[i], beta, 0.0)
                video.write(frame)
                
                if frame_index >= (anti_flickering_sample_size + 1) // 2:
                    frame_images.pop(0)
                if frame_index <= len(self.image_paths) - anti_flickering_sample_size:
                    new_image_path = self.image_paths[frame_index + (anti_flickering_sample_size+1)//2]
                    frame_images.append(self.export_image_process(cv2.imread(new_image_path), new_image_path, display_details))
                
                

                self.export_progress_display.set_text(f"Export Progress: {frame_index+1}/{len(self.image_paths)}")
    
        
        
        
        
        
        video.release()
        self.export_progress_display.set_text(f"Export Complete.")
        
        self.export_button.enable()
        self.exporting = False
        self.scene2.on_export_done()
    
    
    
    
    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.export_button:
                filepath = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 Video", "mp4")])
                if filepath:
                    if hasattr(self, "export_progress_display"):
                        self.export_progress_display.kill()
                    self.export_button.disable()
                    self.exporting = True
                    self.scene2.on_export()
                    
                    self.export_progress = 0
                    self.export_progress_display = pygame_gui.elements.UILabel(
                        relative_rect=pygame.Rect(0, 20, 1050, 30), 
                        text=f"Export Progress: {self.export_progress}/{len(self.image_paths)}", 
                        manager=self.manager, 
                        container=self, 
                        anchors={"centerx":"centerx", "top":"top", "top_target":self.export_button}, 
                        object_id=ObjectID(class_id="@label", object_id="#export_progress_display")
                    )
                    
                    
                    self.export_process = threading.Thread(target=self.export_video, args=(filepath,))
                    self.export_process.start()
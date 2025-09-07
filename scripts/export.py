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
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface

from .scene import Scene
from .utils import scroll_to_index



from typing import TYPE_CHECKING, Dict, Sequence
if TYPE_CHECKING:
    from ..app import App
    from .scene2 import Scene2


class ExportQueueDisplay(pygame_gui.elements.UIScrollingContainer):
    '''My own table class lol, hope I remember this thing if I ever wanna make a more generalized table in pygame_gui'''
    def __init__(self, manager, container, anchors, column_spans, columns, button_columns:list[int]|None = None, tooltip_columns:list[int]|None = None):
        self.manager = manager
        
        self.width = 1000
        self.height = 300
        self.scrollable_height = 0
        self.panel_height = 35
        self.top_gap_reduce = -3
        self.left_gap_reduce = -3
        self.curr_id = 0
        
        super().__init__(relative_rect=pygame.Rect(0, 10, self.width+50, self.height), 
                         manager=manager, 
                         container=container, 
                         anchors=anchors, 
                         object_id=ObjectID(class_id="@panel", object_id="#export_queue_display"))
        
        
        self.column_spans = column_spans
        self.column_widths = [(self.width - (len(column_spans) - 1) * self.left_gap_reduce) * (span / sum(self.column_spans)) for span in self.column_spans]
        
        self.columns = columns
        self.button_columns = button_columns
        self.tooltip_columns = tooltip_columns

        self.top_target = None
        
        self.rows_panels:dict[int, list[pygame_gui.elements.UIPanel]] = {}
        self.rows_elements:dict[int, list[pygame_gui.elements.UILabel|pygame_gui.elements.UIButton]] = {}
        self.rows_values:dict[int, Sequence] = {}
        self.tool_tips:dict[tuple[int, int], str] = {}
        #Show title row
        self.add_row(columns, ignore_button=True)
    
    
    def add_row(self, values:Sequence, key:int|None = None, ignore_button:bool=False, store_values:bool=True):
        '''Adds or changes a row to the table with given values, returns the row key'''
        if len(values) != len(self.column_spans):
            raise ValueError(f"Values length does not match column count {len(values)=}")
        
        if key is None:
            id = self.curr_id
            self.curr_id += 1
        else:
            id = key
        
        row_panels = []
        row_elements = []
        panel = None
        left_target = None
        for column_index, (value, width) in enumerate(zip(values, self.column_widths)):
            anchors:dict = {"left":"left", "top":"top"}
            if left_target:
                anchors["left_target"] = left_target
                left = self.left_gap_reduce
            else:
                left = 0
            if self.top_target:
                anchors["top_target"] = self.top_target
                top = self.top_gap_reduce
            else:
                top = 0
            
            panel = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(left, top, width, self.panel_height), 
                manager=self.manager, 
                container=self, 
                anchors=anchors, 
                object_id=ObjectID(class_id="@label", object_id="#export_queue_box"), 
                margins={"top":0, "left":0, "right":0, "bottom":0}
            )
            if self.button_columns and column_index in self.button_columns and not ignore_button:
                label = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(0, 0, width, self.panel_height), 
                    manager=self.manager, 
                    text=value, 
                    container=panel, 
                    object_id=ObjectID(class_id="#export_queue_button", object_id=f"#export_queue_button/{id},{column_index}")
                )
            elif self.tooltip_columns and column_index in self.tooltip_columns:
                label = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(0, 0, width, self.panel_height), 
                    manager=self.manager, 
                    text=value, 
                    container=panel, 
                    object_id=ObjectID(class_id="@label", object_id="#export_queue_tooltip_button")
                )
            else:
                label = pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(0, 0, width, self.panel_height), 
                    manager=self.manager, 
                    text=value, 
                    container=panel, 
                    object_id=ObjectID(class_id="@label", object_id="#export_queue_label")
                )
            left_target = label
            row_panels.append(panel)
            row_elements.append(label)
        
        
        
        if panel:
            self.top_target = panel
            self.rows_panels[id] = row_panels
            self.rows_elements[id] = row_elements
            if store_values:
                self.rows_values[id] = values
            self.scrollable_height += self.panel_height
            self.set_scrollable_area_dimensions((self.width, max(self.scrollable_height, self.height)))
        
        return id
    
    def kill_all_elements(self):
        for row_panels in self.rows_panels.values():
            for panel in row_panels:
                panel.kill()
        self.top_target = None
        self.scrollable_height = 0
        self.rows_panels = {}
        self.rows_elements = {}
    
    def remove_row(self, row_key:int):
        self.rows_values.pop(row_key)
        
        #remove tooltips
        found_columns = []
        for (row, column) in self.tool_tips:
            if row == row_key:
                found_columns.append(column)
        
        for column in found_columns:
            self.tool_tips.pop((row_key, column))
        
        
        self.kill_all_elements()
        for row_key, row_values in self.rows_values.items():
            self.add_row(row_values, row_key, store_values=False, ignore_button=row_key==0)
        
        for (row, column), text in self.tool_tips.items():
            self.add_tooltip(row, column, text, store_tooltip=False)
    
    def remove_last_row(self):
        self.remove_row(self.row_count)
    
    @property
    def row_count(self):
        return len(self.rows_values)

    def get_element(self, row:int, column:int):
        return self.rows_elements[row][column]

    def add_tooltip(self, row, column, text, store_tooltip:bool=True):
        element = self.get_element(row, column)
        if isinstance(element, pygame_gui.elements.UIButton):
            element.set_tooltip(text)
            if store_tooltip:
                self.tool_tips[(row, column)] = text
        else:
            raise ValueError(f"Element at {row=} {column=} is not of type UIButton.")
            
class ExportScreen(pygame_gui.elements.UIPanel):
    def __init__(self, app:App, manager:pygame_gui.UIManager, scene2:Scene2, container):
        self.app = app
        self.manager = manager
        self.scene2 = scene2
        super().__init__(relative_rect=pygame.Rect(0, -650, 1080, 650),
                         manager=self.manager, 
                         container=container, 
                         anchors={"left":"left", "right":"right", "bottom":"bottom"})
        
        
        self.exports:dict[int, dict] = {}
        self.exporting = False
        self.exporting_key = None
        self.cancelling_export = False
        self.cancelling_export_row = None
        
        self.export_video_image_fitting_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(30, 0, 1050, 50), 
            text=f"Image Fitting Rule: {self.image_fitting_rule}", 
            manager = self.manager, 
            container = self, 
            anchors = {"left":"left", "top":"top"}, 
            object_id=ObjectID(class_id="@export_info_label", object_id="#export_video_resolution_label")
        )
    
        self.export_video_resolution_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(30, 0, 1050, 50), 
            text=f"Video Resolution: {self.video_resolution[0]}x{self.video_resolution[1]}", 
            manager = self.manager, 
            container = self, 
            anchors = {"left":"left", "top":"top", "top_target":self.export_video_image_fitting_label}, 
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
        
        column_spans = [4,2,3,2,3,3,4,4,3,2]
        columns = ["File path", "Fit/Fill", "Resolution", "fps", "img count", "Length", "Anti-Flickering", "Sample Size", "Progress", ""]
        self.export_queue_display = ExportQueueDisplay(
            manager=self.manager,
            container=self, 
            anchors={"centerx":"centerx", "top":"top", "top_target":self.export_button}, 
            column_spans=column_spans, 
            columns=columns, 
            tooltip_columns=[0], 
            button_columns=[9]
        )
        
        
        
        
        error_msg = ""
        if not self.check_resolution_valid():
            error_msg += "Video resolution is invalid.\n"
        if self.fps == 0:
            error_msg += "Video fps is invalid.\n"
        
        if error_msg:
            self.export_error_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, -70, 1050, 100), 
                text=error_msg, 
                manager = self.manager, 
                container = self, 
                anchors = {"left":"left", "bottom":"bottom", "bottom_target":self.export_button}, 
                object_id=ObjectID(class_id="@button", object_id="#export_error_label")
            )
            self.export_button.disable()
    
    def update_display(self):
        if hasattr(self, "export_error_label") and self.export_error_label is not None:
            self.export_error_label.kill()
        self.export_video_image_fitting_label.set_text(f"Image Fitting Rule: {self.image_fitting_rule}")
        self.export_video_resolution_label.set_text(f"Video Resolution: {self.video_resolution[0]}x{self.video_resolution[1]}")
        self.export_video_fps_label.set_text(f"Frames per Second: {self.fps}")
        self.export_video_img_count_label.set_text(f"Number of Images: {len(self.image_paths)}")
        video_length = round(len(self.image_paths) / self.fps, 1) if self.fps != 0 else "--"
        self.export_video_length_label.set_text(f"Video Length (in seconds): {video_length}")
        self.export_video_anti_flickering_label.set_text(f"Anti-flickering: {self.anti_flickering}")
        if self.anti_flickering == "On":
            self.export_video_anti_flickering_sample_size_label.set_text(f"Anti-flickering Sample Size: {self.anti_flickering_sample_size}")
        error_msg = ""
        if not self.check_resolution_valid():
            error_msg += "Video resolution is invalid.\n"
        if self.fps == 0:
            error_msg += "Video fps is invalid.\n"
        if error_msg:
            self.export_error_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, -70, 1050, 100), 
                text=error_msg, 
                manager = self.manager, 
                container = self, 
                anchors = {"left":"left", "bottom":"bottom", "bottom_target":self.export_button}, 
                object_id=ObjectID(class_id="@button", object_id="#export_error_label")
            )
            self.export_button.disable()
        else:
            self.export_button.enable()
    
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
    
    
    
    def export_image_process(self, image, image_path, display_details, video_resolution, image_fitting_rule):
        # topleft = display_details[image_path]["top_left"]
        relative_center = display_details[image_path]["relative_center"]
        zoom_level = display_details[image_path]["zoom_level"]
        
        image_height, image_width, channel = image.shape
        

        width_ratio = video_resolution[0] / image_width
        height_ratio = video_resolution[1] / image_height
        if image_fitting_rule == "Fit":
            scaling_ratio = min(width_ratio, height_ratio)
        else:
            scaling_ratio = max(width_ratio, height_ratio)
        image_base_width = round(video_resolution[0] / scaling_ratio)
        image_base_height = round(video_resolution[1] / scaling_ratio)

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
        resized_image = cv2.resize(cropped_image, video_resolution)
        return resized_image
    
    
    
    def export_video(self, image_fitting_rule, video_resolution, image_paths, display_details, anti_flickering, sample_size, video:cv2.VideoWriter, display_row_key:int):
        if anti_flickering == "Off":
            for index, image_path in enumerate(image_paths):
                frame = cv2.imread(image_path)
                resized_frame = self.export_image_process(frame, image_path, display_details, video_resolution, image_fitting_rule)
                video.write(resized_frame)
                
                try:
                    export_progress_display = self.export_queue_display.get_element(display_row_key, 8)
                    export_progress_display.set_text(f"{index+1}/{len(image_paths)}")
                except:
                    pass
                
                if self.exporting == False:
                    self.exporting_key = None
                    self.cancelling_export = True
                    return
        
        
        else:
            anti_flickering_sample_size = int(sample_size)
            first_frame_image_paths = image_paths[:(anti_flickering_sample_size+1)//2]
            
            frame_images = [self.export_image_process(cv2.imread(img_path), img_path, display_details, video_resolution, image_fitting_rule) for img_path in first_frame_image_paths]

            for frame_index in range(len(image_paths)):
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
                if frame_index <= len(image_paths) - anti_flickering_sample_size:
                    new_image_path = image_paths[frame_index + (anti_flickering_sample_size+1)//2]
                    frame_images.append(self.export_image_process(cv2.imread(new_image_path), new_image_path, display_details, video_resolution, image_fitting_rule))
                    
                try:
                    export_progress_display = self.export_queue_display.get_element(display_row_key, 8)
                    export_progress_display.set_text(f"{frame_index+1}/{len(image_paths)}")
                except:
                    pass
                
                if self.exporting == False:
                    self.exporting_key = None
                    self.cancelling_export = True
                    return
        
        video.release()
        export_progress_display.set_text(f"Done")
        del self.exports[display_row_key]
        self.exporting = False
        self.exporting_key = None
        self.attempt_start_export()
    
    
    def get_pending_export_filepaths(self):
        return [export["filepath"] for export in self.exports.values()]
    
    
    def add_export(self, filepath):
        
        
        filename = os.path.basename(filepath)
        video_length = round(len(self.image_paths)/self.fps, 1)
        row = self.export_queue_display.add_row([filename, 
                                           self.image_fitting_rule, 
                                           f"{self.video_resolution[0]}x{self.video_resolution[1]}", 
                                           str(self.fps), 
                                           str(len(self.image_paths)), 
                                           str(video_length), 
                                           self.anti_flickering, 
                                           self.anti_flickering_sample_size, 
                                           f"0/{len(self.image_paths)}", 
                                           "Cancel"])
        
        self.export_queue_display.add_tooltip(row, 0, filepath)
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or use 'XVID' for .avi
        video = cv2.VideoWriter(filepath, fourcc, self.fps, self.video_resolution)
        export_info = {"filepath":filepath, 
                       "image_fitting_rule":self.image_fitting_rule, 
                       "video_resolution":self.video_resolution, 
                       "fps":self.fps, 
                       "image_paths":self.image_paths.copy(), 
                       "display_details":self.scene2.panning_to_display_details(), 
                       "anti-flickering":self.anti_flickering, 
                       "sample_size":self.anti_flickering_sample_size, 
                       "video":video, 
                       "display_row_key":row
                       }
        self.exports[row] = export_info
        self.attempt_start_export()
    
    def attempt_start_export(self):
        '''Called whenever to attempt to start a new export task'''
        if len(self.exports) == 0:
            return
        if self.exporting:
            return
        
        self.exporting_key, export_info = list(self.exports.items())[0]
        args = (export_info["image_fitting_rule"], export_info["video_resolution"], export_info["image_paths"], export_info["display_details"], export_info["anti-flickering"], export_info["sample_size"], export_info["video"], export_info["display_row_key"])
        self.export_process = threading.Thread(target=self.export_video, args=args)
        self.exporting = True
        self.export_process.start()
        
        
        
    def on_export_cancel(self, row_key):
        self.export_queue_display.remove_row(row_key)
        export_info = self.exports[row_key]
        video = export_info["video"]
        video.release()
        filepath = export_info["filepath"]
        os.remove(filepath)
        del self.exports[row_key]
        self.attempt_start_export()

    
    
    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.export_button:
                while True:
                    filepath = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 Video", "mp4")])
                    if filepath in self.get_pending_export_filepaths():
                        retry = messagebox.askretrycancel("Duplicated filepath", f"You already have a pending video with the same file path, would you like to select another filename?")
                        if not retry:
                            return
                    else:
                        break
                if filepath:
                    self.add_export(filepath)
            
            if event.ui_object_id.startswith("panel.panel.#export_queue_display.#export_queue_box.#export_queue_button"):
                try:
                    _, cord = event.ui_object_id.split("/")
                    row, column = cord.split(",")
                    row = int(row)
                    column = int(column)
                except ValueError:
                    print(f"Incorrect object_id format for export queue display button: '{event.ui_object_id}'")
                    return
                
                #Check if the clicked button is the cancel button
                if column != 9:
                    return
                
                ans = messagebox.askyesno("Remove export queue item", "Are you sure you want to remove this queue item? If the export is ongoing, the export will be cancelled.")
                if ans is True:
                    if row == self.exporting_key:
                        self.exporting = False
                        self.cancelling_export_row = row
                    else:
                        self.cancelling_export = True
                        self.cancelling_export_row = row
                
    def update(self, time_delta: float):
        super().update(time_delta)
        if self.cancelling_export:
            if self.cancelling_export_row is None:
                raise RuntimeError("cancelling_export_row is unset.")
            self.on_export_cancel(self.cancelling_export_row)
            self.cancelling_export = False
            self.cancelling_export_row = None
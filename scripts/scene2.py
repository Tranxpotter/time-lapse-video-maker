from __future__ import annotations
import pygame
import pygame_gui
from pygame_gui.core import ObjectID
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import math
import cv2

from .scene import Scene
from .options import OptionsScreen
from .panning import PanningScreen
from .preview import PreviewScreen
from .export import ExportScreen



from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    from ..app import App




class Scene2(Scene):
    def __init__(self, app:App, manager:pygame_gui.UIManager, file_paths:list[str]):
        self.app = app
        self.manager = manager
        self.file_paths = file_paths
        
        self.image_paths = self.file_paths
        self.folder_path = os.path.dirname(self.image_paths[0])
        self.curr_scene = 2
        
        self.zoom_ratio_per_level = 0.02
        
        #Initialize the UI layout for scene2
        self.manager.clear_and_reset()
        
        #Navigation bar
        self.nav_bar = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, 1080, 70),
            manager=self.manager, 
            anchors={"left":"left", "top":"top", "right":"right"},
        )
        
        self.scene2_back_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 100, 50),
            text='File',
            manager=self.manager, 
            container=self.nav_bar, 
            anchors={"left":"left", "top":"top"}, 
            object_id=ObjectID(class_id="@nav_btn", object_id="#scene2_back_btn")
        )
        
        self.scene2_options_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 100, 50),
            text='Options',
            manager=self.manager, 
            container=self.nav_bar, 
            anchors={"left":"left", "left_target":self.scene2_back_btn}, 
            object_id=ObjectID(class_id="@nav_btn", object_id="#scene2_options_btn")
        )
        
        self.scene2_panning_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 100, 50),
            text='Panning',
            manager=self.manager, 
            container=self.nav_bar, 
            anchors={"left":"left", "left_target":self.scene2_options_btn}, 
            object_id=ObjectID(class_id="@nav_btn", object_id="#scene2_panning_btn")
        )
        
        self.scene2_preview_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 100, 50),
            text='Preview',
            manager=self.manager, 
            container=self.nav_bar, 
            anchors={"left":"left", "left_target":self.scene2_panning_btn}, 
            object_id=ObjectID(class_id="@nav_btn", object_id="#scene2_preview_btn")
        )
        
        self.scene2_export_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 100, 50),
            text='Export',
            manager=self.manager, 
            container=self.nav_bar, 
            anchors={"left":"left", "left_target":self.scene2_preview_btn}, 
            object_id=ObjectID(class_id="@nav_btn", object_id="#scene2_export_btn")
        )
        
        
        #Initialize variables
        #Option screen
        self.fps = 30
        first_image = self.load_image(self.image_paths[0])
        self.first_img_width, self.first_img_height = first_image.get_width(), first_image.get_height()
        self.video_resolution = (int(self.first_img_width), int(self.first_img_height))
        self.aspect_ratio = "Custom"
        self.image_fitting_rule:Literal["Fit", "Fill"] = "Fit"
        self.anti_flickering = "Off"
        self.anti_flickering_sample_size = "7"
        
        #Panning screen
        self.panning = dict() #For storing panning results
        self.curr_panning_index = 0
        
        #Preview screen
        self.curr_preview_index = 0
        
        
        #Initialize first active screen
        self.curr_active_screen = OptionsScreen(self.app, self.manager, self, self.nav_bar)
        self.curr_disabled_btn = self.scene2_options_btn
        self.scene2_options_btn.disable()
    
    

    def to_page(self, name:Literal["Options", "Panning", "Preview", "Export"]):
        if name == "Options":
            self.curr_disabled_btn.enable()
            self.curr_active_screen.kill()
            self.curr_disabled_btn = self.scene2_options_btn
            self.curr_active_screen = OptionsScreen(self.app, self.manager, self, self.nav_bar)
            self.scene2_options_btn.disable()
        
        elif name == "Panning":
            self.curr_disabled_btn.enable()
            self.curr_active_screen.kill()
            self.curr_disabled_btn = self.scene2_panning_btn
            self.curr_active_screen = PanningScreen(self.app, self.manager, self, self.nav_bar)
            self.scene2_panning_btn.disable()
        
        elif name == "Preview":
            self.curr_disabled_btn.enable()
            self.curr_active_screen.kill()
            self.curr_disabled_btn = self.scene2_preview_btn
            self.curr_active_screen = PreviewScreen(self.app, self.manager, self, self.nav_bar)
            self.scene2_preview_btn.disable()
        
        elif name == "Export":
            self.curr_disabled_btn.enable()
            self.curr_active_screen.kill()
            self.curr_disabled_btn = self.scene2_export_btn
            self.curr_active_screen = ExportScreen(self.app, self.manager, self, self.nav_bar)
            self.scene2_export_btn.disable()

        else:
            raise ValueError(f"Invalid page name {name}")
    
    def on_export(self):
        self.scene2_back_btn.disable()
        self.scene2_options_btn.disable()
        self.scene2_panning_btn.disable()
        self.scene2_preview_btn.disable()
    
    def on_export_done(self):
        self.scene2_back_btn.enable()
        self.scene2_options_btn.enable()
        self.scene2_panning_btn.enable()
        self.scene2_preview_btn.enable()
    
    def scene1(self):
        self.app.to_scene1()
    
    def load_image(self, image_path):
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        surface = pygame.surfarray.make_surface(img.swapaxes(0, 1))
        return surface
    
    def calc_zoom_value(self, zoom:int|float, val:int|float):
        zoom_ratio = math.exp(-math.log(self.zoom_ratio_per_level) / 49) * math.exp(math.log(self.zoom_ratio_per_level) / 49 * zoom)
        return int(val * zoom_ratio)
    
    def get_zoom_ratio(self, zoom):
        zoom_ratio = math.exp(-math.log(self.zoom_ratio_per_level) / 49) * math.exp(math.log(self.zoom_ratio_per_level) / 49 * zoom)
        return zoom_ratio
    
    def get_image_names(self):
        return [os.path.basename(image_path) for image_path in self.image_paths]
    
    
    def get_topleft_from_relc(self, relative_center:tuple[float, float], image_width, image_height, crop_width, crop_height):
        # Get topleft from relative_center
        center_x = relative_center[0] * image_width
        center_y = relative_center[1] * image_height
        topleft_x = int(center_x - crop_width // 2)
        topleft_y = int(center_y - crop_height // 2)
        
        
        # Move the minimum to fit image if area is out of range
        if topleft_x < 0:
            topleft_x = 0
        if topleft_y < 0:
            topleft_y = 0
        if topleft_x + crop_width >= image_width:
            topleft_x = image_width - crop_width
        if topleft_y + crop_height >= image_height:
            topleft_y = image_height - crop_height
        
        topleft = (topleft_x, topleft_y)
        return topleft
    
    def get_relc_from_topleft(self, topleft:tuple[int, int], image_width, image_height, crop_width, crop_height):
        # Calculate the center from the topleft and crop size
        center_x = topleft[0] + crop_width // 2
        center_y = topleft[1] + crop_height // 2
        # Normalize to image dimensions
        relative_center = (center_x / image_width, center_y / image_height)
        return relative_center
        
    
    def panning_to_display_details(self):
        '''Return display details of each image from panning details
        
        The cropping area calculated from display details may not be within the image size, must check for overflow and move the area by the minimum amount'''
        
        display_details = {}
        panning = dict(sorted(self.panning.items(), key=lambda x:x[0]))
        if panning:
            panning_keys = list(panning.keys())
            if not panning:
                panning[self.image_paths[-1]] = {"top_left":(0, 0), "relative_center":(0.5, 0.5), "zoom_level":1}
            elif panning_keys[-1] != self.image_paths[-1]:
                panning[self.image_paths[-1]] = panning[list(panning.keys())[-1]]
            panning_keys = list(panning.keys())
            
            next_image_path = panning_keys[0]
            panning_key_index = 0
            next_panning = panning[next_image_path]
            next_image_index = self.image_paths.index(panning_keys[0])
            final_rel_center = next_panning["relative_center"]
            final_zoom_level = next_panning["zoom_level"]
            if next_image_index == 0:
                # No next image change at first image if panning of first image is set
                start_rel_center = final_rel_center
                start_zoom_level = final_zoom_level
                curr_zoom_ratio = start_zoom_ratio = self.get_zoom_ratio(start_zoom_level)
                final_zoom_ratio = self.get_zoom_ratio(final_zoom_level)
                rel_center_x_total_change = 0
                rel_center_y_total_change = 0
                total_zoom_level_change = 0
                zoom_level_change = 0
                
                rel_center_x_change = 0
                rel_center_y_change = 0
                curr_rel_center_x_change = 0
                curr_rel_center_y_change = 0
            else:
                # Calculate changes from first image to next panning if panning of first image is not set
                # v initial conditions of first image
                start_zoom_level = 1
                start_rel_center = (0.5, 0.5)
                # v panning changes
                rel_center_x_total_change = final_rel_center[0] - start_rel_center[0]
                rel_center_y_total_change = final_rel_center[1] - start_rel_center[1]
                
                
                total_zoom_level_change = final_zoom_level - start_zoom_level
                
                curr_zoom_ratio = start_zoom_ratio = self.get_zoom_ratio(start_zoom_level)
                final_zoom_ratio = self.get_zoom_ratio(final_zoom_level)
                
                if total_zoom_level_change != 0:
                    zoom_level_change = total_zoom_level_change / next_image_index
                    
                    # v (curr zoom ratio - start zoom ratio)/(final zoom ratio - start zoom ratio) = curr rel center x change / total rel center x change
                    # zoom ratio(zoom level change * counter)
                    zoom_ratio = (curr_zoom_ratio - start_zoom_ratio)/(final_zoom_ratio - start_zoom_ratio)
                    
                    curr_rel_center_x_change = zoom_ratio * rel_center_x_total_change
                    curr_rel_center_y_change = zoom_ratio * rel_center_y_total_change
                    rel_center_x_change = rel_center_x_total_change / next_image_index
                    rel_center_y_change = rel_center_y_total_change / next_image_index
                else:
                    rel_center_x_change = rel_center_x_total_change / next_image_index
                    rel_center_y_change = rel_center_y_total_change / next_image_index
                    curr_rel_center_x_change = 0
                    curr_rel_center_y_change = 0
                    zoom_level_change = 0
                
            counter = 0
            curr_image_index = 0

            
            for image_path in self.image_paths:
                curr_zoom_level = start_zoom_level + zoom_level_change*counter

                # Calc center change from zoom ratio changes
                curr_zoom_ratio = self.get_zoom_ratio(curr_zoom_level)
                if total_zoom_level_change != 0:
                    
                    zoom_ratio = (curr_zoom_ratio - start_zoom_ratio)/(final_zoom_ratio - start_zoom_ratio)
                    
                    curr_rel_center_x_change = zoom_ratio * rel_center_x_total_change
                    curr_rel_center_y_change = zoom_ratio * rel_center_y_total_change
                else:
                    curr_rel_center_x_change = rel_center_x_change * counter
                    curr_rel_center_y_change = rel_center_y_change * counter

                display_details[image_path] = {"relative_center":(start_rel_center[0] + curr_rel_center_x_change, start_rel_center[1] + curr_rel_center_y_change), 
                                            "zoom_level":curr_zoom_level}
                
                
                if image_path == next_image_path and panning_key_index + 1 < len(panning):
                    counter = 0
                    start_rel_center = final_rel_center
                    start_zoom_level = curr_zoom_level = final_zoom_level
                    curr_image_index = next_image_index
                    panning_key_index += 1
                    next_image_path = panning_keys[panning_key_index]
                    next_panning = panning[next_image_path]
                    next_image_index = self.image_paths.index(next_image_path)
                    final_rel_center = next_panning["relative_center"]
                    final_zoom_level = next_panning["zoom_level"]
                    
                    rel_center_x_total_change = final_rel_center[0] - start_rel_center[0]
                    rel_center_y_total_change = final_rel_center[1] - start_rel_center[1]
                    
                    zoom_level_change = (final_zoom_level - start_zoom_level) / (next_image_index - curr_image_index)
                    total_zoom_level_change = final_zoom_level - start_zoom_level
                    zoom_level_change = total_zoom_level_change / (next_image_index - curr_image_index)
                    
                    curr_zoom_ratio = start_zoom_ratio = self.get_zoom_ratio(start_zoom_level)
                    final_zoom_ratio = self.get_zoom_ratio(final_zoom_level)
                    
                    rel_center_x_change = rel_center_x_total_change / next_image_index
                    rel_center_y_change = rel_center_y_total_change / next_image_index
                
                
                counter += 1
                
                
                
                
                
        else:
            for image_path in self.image_paths:
                display_details[image_path] = {"top_left":(0, 0), "relative_center":(0.5, 0.5), "zoom_level":1}
        
        return display_details
    
    
    
    
    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.scene2_back_btn:
                answer = messagebox.askyesno("Warning", "Are you sure you want change selected files? All settings will be reset.")
                if answer is True:
                    self.scene1()
            
            elif event.ui_element == self.scene2_options_btn:
                self.to_page("Options")
            
            elif event.ui_element == self.scene2_panning_btn:
                self.to_page("Panning")
            
            elif event.ui_element == self.scene2_preview_btn:
                self.to_page("Preview")
            
            elif event.ui_element == self.scene2_export_btn:
                self.to_page("Export")
        
        self.curr_active_screen.handle_event(event)
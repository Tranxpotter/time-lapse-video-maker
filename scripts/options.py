from __future__ import annotations
import pygame
import pygame_gui
from pygame_gui.core import ObjectID
import tkinter as tk
from tkinter import filedialog, messagebox
import os

from .scene import Scene



from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    from ..app import App
    from .scene2 import Scene2



class OptionsScreen(pygame_gui.elements.UIPanel):
    def __init__(self, app:App, manager:pygame_gui.UIManager, scene2:Scene2, anchor_target, container):
        self.app = app
        self.manager = manager
        self.scene2 = scene2
        super().__init__(relative_rect=pygame.Rect(0, 0, 1080, 650),
                         manager=self.manager, 
                         container=container, 
                         anchors={"left":"left", "right":"right", "top":"top", "top_target":anchor_target})

        self.scene2_options_screen_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 200, 50),
            text='Options:', 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top"},
            object_id=ObjectID(class_id="@title2", object_id="#scene2_options_screen_label")
        )
        
        #Resolution input
        resolution_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 200, 50),
            text='Resolution:', 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.scene2_options_screen_label},
            object_id=ObjectID(class_id="@title3", object_id="#resolution_label")
        )
        
        width_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            text='Width:', 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":resolution_label},
            object_id=ObjectID(class_id="@label", object_id="#width_label")
        )
        
        self.resolution_width_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":resolution_label, "left_target":width_label}, 
            object_id=ObjectID(class_id="@option_entry", object_id="#resolution_width_entry")
        )
        
        height_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            text='Height:', 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":resolution_label, "left_target":self.resolution_width_entry},
            object_id=ObjectID(class_id="@label", object_id="#height_label")
        )
        
        self.resolution_height_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":resolution_label, "left_target":height_label}, 
            object_id=ObjectID(class_id="@option_entry", object_id="#resolution_height_entry")
        )
        
        
        self.resolution_aspect_ratio_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 0, 200, 50), 
            text="Aspect Ratio:", 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":resolution_label, "left_target":self.resolution_height_entry}, 
            object_id=ObjectID(class_id="@label", object_id="#resolution_presets_label")
        )
        self.resolution_aspect_ratio_menu = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(0, 0, 100, 50), 
            starting_option="Custom" if not hasattr(self, "aspect_ratio") else self.aspect_ratio, 
            options_list=["Custom", "Original", "16:9", "1:1", "9:16", "4:3", "4:5", "21:9", "3:2"],
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":resolution_label, "left_target":self.resolution_aspect_ratio_label}, 
        )
        self.aspect_ratio_presets = {"16:9":16/9, "1:1":1, "9:16":9/16, "4:3":4/3, "4:5":4/5, "21:9":21/9, "3:2":3/2}
        
        self.image_fitting_rule_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 200, 50), 
            text="Image fitting rule:", 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":resolution_label, "left_target":self.resolution_aspect_ratio_menu}, 
            object_id=ObjectID(class_id="@label", object_id="#image_fitting_rule_label")
        )

        self.image_fitting_rule_menu = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(0, 0, 100, 50), 
            starting_option="Fit" if not hasattr(self, "image_fitting_rule") else self.image_fitting_rule, 
            options_list=["Fit", "Fill"],
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":resolution_label, "left_target":self.image_fitting_rule_label}, 
        )
        
        self.resolution_preset_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 200, 50), 
            text="Resolution Presets:", 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_aspect_ratio_menu}, 
            object_id=ObjectID(class_id="@label", object_id="#resolution_presets_label")
        )
        self.resolution_preset_first_image_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 120, 50), 
            text="First Image", 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_aspect_ratio_menu, "left_target":self.resolution_preset_label}
        )
        self.resolution_preset_360p_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 50, 50), 
            text="360", 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_aspect_ratio_menu, "left_target":self.resolution_preset_first_image_btn}
        )
        self.resolution_preset_SD_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 50, 50), 
            text="480", 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_aspect_ratio_menu, "left_target":self.resolution_preset_360p_btn}
        )
        self.resolution_preset_720p_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 50, 50), 
            text="720", 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_aspect_ratio_menu, "left_target":self.resolution_preset_SD_btn}
        )
        self.resolution_preset_FHD_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 50, 50), 
            text="1080", 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_aspect_ratio_menu, "left_target":self.resolution_preset_720p_btn}
        )
        self.resolution_preset_QHD_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 50, 50), 
            text="1440", 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_aspect_ratio_menu, "left_target":self.resolution_preset_FHD_btn}
        )
        self.resolution_preset_4K_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 50, 50), 
            text="2160", 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_aspect_ratio_menu, "left_target":self.resolution_preset_QHD_btn}
        )
        self.resolution_preset_8K_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 50, 50), 
            text="4320", 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_aspect_ratio_menu, "left_target":self.resolution_preset_4K_btn}
        )
        
        
    
        self.resolution_error_msg = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 300, 50),
            text='Please enter a valid resolution',
            manager=self.manager,
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_preset_label}, 
            object_id=ObjectID(class_id="@error_msg", object_id="#resolution_error_msg"), 
            visible=False
        )
        
        
        #FPS input
        fps_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            text='FPS:', 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_error_msg},
            object_id=ObjectID(class_id="@label", object_id="#fps_label")
        )
        
        self.fps_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_error_msg, "left_target":fps_label}, 
            object_id=ObjectID(class_id="@option_entry", object_id="#fps_entry")
        )
        self.fps_entry.set_text(str(self.fps))
        
        self.video_length_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 300, 50),
            text='Video Length:',
            manager=self.manager,
            container=self,
            anchors={"left":"left", "top":"top", "top_target":self.fps_entry},
            object_id=ObjectID(class_id="@label", object_id="#video_length_label")
        )
        
        self.fps_error_msg = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 300, 50),
            text='Please enter a valid FPS',
            manager=self.manager,
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.video_length_label}, 
            object_id=ObjectID(class_id="@error_msg", object_id="#fps_error_msg")
        )
        
        #Anti flickering stuff
        self.anti_flickering_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 150, 50),
            text='Anti-flickering:', 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.fps_error_msg},
            object_id=ObjectID(class_id="@label", object_id="#anti_flickering")
        )
        
        self.anti_flickering_selector = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(0, 0, 200, 50),
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.fps_error_msg, "left_target":self.anti_flickering_label}, 
            object_id=ObjectID(class_id="@option_entry", object_id="#anti_flickering_selector"),
            options_list=["On", "Off"], 
            starting_option=self.anti_flickering
        )
        
        self.anti_flickering_sample_size_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(50, 0, 150, 50),
            text='Sample Size:', 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.fps_error_msg, "left_target":self.anti_flickering_selector},
            object_id=ObjectID(class_id="@label", object_id="#anti_flickering")
        )
        
        self.anti_flickering_sample_size_selector = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(0, 0, 200, 50),
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.fps_error_msg, "left_target":self.anti_flickering_sample_size_label}, 
            object_id=ObjectID(class_id="@option_entry", object_id="#anti_flickering_sample_size_selector"),
            options_list=["3", "5", "7", "9", "11"], 
            starting_option=self.anti_flickering_sample_size
        )
        
        
        self.resolution_width_entry.set_text(str(self.video_resolution[0]))
        self.resolution_height_entry.set_text(str(self.video_resolution[1]))
        
        if not self.check_resolution_valid():
            self.resolution_error_msg.show()
        else:
            self.resolution_error_msg.hide()
        
        if not self.check_fps_valid():
            self.fps_error_msg.show()
        else:
            self.fps_error_msg.hide()
            video_length = round(len(self.scene2.image_paths) / self.fps, 1)
            self.video_length_label.set_text(f"Video Length: {video_length} seconds")

    
    def check_resolution_valid(self):
        '''Check if the resolution entered is valid, returns True if valid, False otherwise'''
        if self.video_resolution[0] == 0 or self.video_resolution[1] == 0:
            return False
        return True

    def check_fps_valid(self):
        '''Check if the fps entered is valid, returns True if valid, False otherwise'''
        fps = self.fps_entry.get_text()
        return fps.isdigit() and int(fps) != 0
    
    
    def _options_get_ratio(self):
        image_ratio = self.first_img_width / self.first_img_height
        aspect_ratio = self.aspect_ratio
        if aspect_ratio == "Custom":
            width, height = self.resolution_width_entry.get_text(), self.resolution_height_entry.get_text()
            if width.isdigit() and height.isdigit() and int(width) != 0 and int(height) != 0:
                ratio = int(width) / int(height)
            else:
                ratio = image_ratio
        elif aspect_ratio == "Original":
            ratio = image_ratio
        else:
            ratio:float = self.aspect_ratio_presets[aspect_ratio]
        return ratio
    
    @property
    def first_img_width(self):
        return self.scene2.first_img_width

    @first_img_width.setter
    def first_img_width(self, val:int):
        self.scene2.first_img_width = val
    
    @property
    def first_img_height(self):
        return self.scene2.first_img_height
    
    @first_img_height.setter
    def first_img_height(self, val:int):
        self.scene2.first_img_height = val
    
    @property
    def aspect_ratio(self):
        return self.scene2.aspect_ratio

    @aspect_ratio.setter
    def aspect_ratio(self, val:str):
        self.scene2.aspect_ratio = val
    
    @property
    def image_fitting_rule(self):
        return self.scene2.image_fitting_rule
    
    @image_fitting_rule.setter
    def image_fitting_rule(self, val:Literal["Fit", "Fill"]):
        self.scene2.image_fitting_rule = val

    @property
    def video_resolution(self):
        return self.scene2.video_resolution
    
    @video_resolution.setter
    def video_resolution(self, val:tuple[int, int]):
        self.scene2.video_resolution = val
    
    @property
    def fps(self):
        return self.scene2.fps
    
    @fps.setter
    def fps(self, val:int):
        self.scene2.fps = val
    
    @property
    def anti_flickering(self):
        return self.scene2.anti_flickering
    
    @anti_flickering.setter
    def anti_flickering(self, val:str):
        self.scene2.anti_flickering = val
    
    @property
    def anti_flickering_sample_size(self):
        return self.scene2.anti_flickering_sample_size
    
    @anti_flickering_sample_size.setter
    def anti_flickering_sample_size(self, val:str):
        self.scene2.anti_flickering_sample_size = val
    
    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.resolution_preset_first_image_btn:
                image_ratio = self.first_img_width / self.first_img_height
                aspect_ratio = self.aspect_ratio
                if aspect_ratio == "Custom" or aspect_ratio == "Original":
                    self.resolution_width_entry.set_text(str(self.first_img_width))
                    self.resolution_height_entry.set_text(str(self.first_img_height))
                else:
                    ratio = self.aspect_ratio_presets[aspect_ratio]
                    if ratio >= image_ratio:
                        width = self.first_img_width
                        self.resolution_width_entry.set_text(str(width))
                        self.resolution_height_entry.set_text(str(round(width/ratio)))
                    else:
                        height = self.first_img_height
                        self.resolution_height_entry.set_text(str(height))
                        self.resolution_width_entry.set_text(str(round(height*ratio)))
                
                self.video_resolution = (int(self.resolution_width_entry.get_text()), int(self.resolution_height_entry.get_text()))
                if not self.check_resolution_valid():
                    self.resolution_error_msg.show()
                else:
                    self.resolution_error_msg.hide()
            
            
            elif event.ui_element == self.resolution_preset_360p_btn:
                value = 360
                ratio = self._options_get_ratio()
                if ratio < 1:
                    width = value
                    height = round(value/ratio)
                else:
                    height = value
                    width = round(value*ratio)
                
                self.resolution_width_entry.set_text(str(width))
                self.resolution_height_entry.set_text(str(height))
                self.video_resolution = (width, height)
                if not self.check_resolution_valid():
                    self.resolution_error_msg.show()
                else:
                    self.resolution_error_msg.hide()
            
            elif event.ui_element == self.resolution_preset_SD_btn:
                value = 480
                ratio = self._options_get_ratio()
                if ratio < 1:
                    width = value
                    height = round(value/ratio)
                else:
                    height = value
                    width = round(value*ratio)
                
                self.resolution_width_entry.set_text(str(width))
                self.resolution_height_entry.set_text(str(height))
                self.video_resolution = (width, height)
                if not self.check_resolution_valid():
                    self.resolution_error_msg.show()
                else:
                    self.resolution_error_msg.hide()
            
            elif event.ui_element == self.resolution_preset_720p_btn:
                value = 720
                ratio = self._options_get_ratio()
                if ratio < 1:
                    width = value
                    height = round(value/ratio)
                else:
                    height = value
                    width = round(value*ratio)
                
                self.resolution_width_entry.set_text(str(width))
                self.resolution_height_entry.set_text(str(height))
                self.video_resolution = (width, height)
                if not self.check_resolution_valid():
                    self.resolution_error_msg.show()
                else:
                    self.resolution_error_msg.hide()
            
            elif event.ui_element == self.resolution_preset_FHD_btn:
                value = 1080
                ratio = self._options_get_ratio()
                if ratio < 1:
                    width = value
                    height = round(value/ratio)
                else:
                    height = value
                    width = round(value*ratio)
                
                self.resolution_width_entry.set_text(str(width))
                self.resolution_height_entry.set_text(str(height))
                self.video_resolution = (width, height)
                if not self.check_resolution_valid():
                    self.resolution_error_msg.show()
                else:
                    self.resolution_error_msg.hide()
            
            elif event.ui_element == self.resolution_preset_QHD_btn:
                value = 1440
                ratio = self._options_get_ratio()
                if ratio < 1:
                    width = value
                    height = round(value/ratio)
                else:
                    height = value
                    width = round(value*ratio)
                
                self.resolution_width_entry.set_text(str(width))
                self.resolution_height_entry.set_text(str(height))
                self.video_resolution = (width, height)
                if not self.check_resolution_valid():
                    self.resolution_error_msg.show()
                else:
                    self.resolution_error_msg.hide()
            
            elif event.ui_element == self.resolution_preset_4K_btn:
                value = 2160
                ratio = self._options_get_ratio()
                if ratio < 1:
                    width = value
                    height = round(value/ratio)
                else:
                    height = value
                    width = round(value*ratio)
                
                self.resolution_width_entry.set_text(str(width))
                self.resolution_height_entry.set_text(str(height))
                self.video_resolution = (width, height)
                if not self.check_resolution_valid():
                    self.resolution_error_msg.show()
                else:
                    self.resolution_error_msg.hide()
            
            elif event.ui_element == self.resolution_preset_8K_btn:
                value = 4320
                ratio = self._options_get_ratio()
                if ratio < 1:
                    width = value
                    height = round(value/ratio)
                else:
                    height = value
                    width = round(value*ratio)
                
                self.resolution_width_entry.set_text(str(width))
                self.resolution_height_entry.set_text(str(height))
                self.video_resolution = (width, height)
                if not self.check_resolution_valid():
                    self.resolution_error_msg.show()
                else:
                    self.resolution_error_msg.hide()





        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            #Options screen event
            if event.ui_element == self.resolution_width_entry:
                width = self.resolution_width_entry.get_text()
                aspect_ratio = self.aspect_ratio
                if not width.isdigit():
                    self.resolution_error_msg.show()
                elif aspect_ratio == "Custom":
                    height = self.resolution_height_entry.get_text()
                    if not height.isdigit():
                        self.resolution_error_msg.show()
                    else:
                        self.video_resolution = (int(width), int(height))
                        if not self.check_resolution_valid():
                            self.resolution_error_msg.show()
                        else:
                            self.resolution_error_msg.hide()
                
                else:
                    if aspect_ratio == "Original":
                        ratio = self.first_img_width/self.first_img_height
                    else:
                        ratio = self.aspect_ratio_presets[aspect_ratio]
                    height = int(width) / ratio
                    self.resolution_height_entry.set_text(str(int(height)))
                    self.video_resolution = (int(width), int(height))
                    if not self.check_resolution_valid():
                        self.resolution_error_msg.show()
                    else:
                        self.resolution_error_msg.hide()
            
            
            
            elif event.ui_element == self.resolution_height_entry:
                height = self.resolution_height_entry.get_text()
                aspect_ratio = self.aspect_ratio
                if not height.isdigit():
                    self.resolution_error_msg.show()
                elif aspect_ratio == "Custom":
                    width = self.resolution_width_entry.get_text()
                    if not width.isdigit():
                        self.resolution_error_msg.show()
                    else:
                        self.video_resolution = (int(width), int(height))
                        if not self.check_resolution_valid():
                            self.resolution_error_msg.show()
                        else:
                            self.resolution_error_msg.hide()
                
                else:
                    if aspect_ratio == "Original":
                        ratio = self.first_img_width/self.first_img_height
                    else:
                        ratio = self.aspect_ratio_presets[aspect_ratio]
                    width = int(height) * ratio
                    self.resolution_width_entry.set_text(str(int(width)))
                    self.video_resolution = (int(width), int(height))
                    if not self.check_resolution_valid():
                        self.resolution_error_msg.show()
                    else:
                        self.resolution_error_msg.hide()
            
            
            
            
            
            elif event.ui_element == self.fps_entry:
                fps = self.fps_entry.get_text()
                if not fps.isdigit() or int(fps) == 0:
                    self.fps_error_msg.show()
                    self.video_length_label.set_text(f"Video Length: -- seconds")
                else:
                    self.fps_error_msg.hide()
                    self.fps = int(fps)
                    video_length = round(len(self.scene2.image_paths) / int(fps), 1)
                    self.video_length_label.set_text(f"Video Length: {video_length} seconds")
        
        
        
        
        
        
        #Drop down menu events
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.resolution_aspect_ratio_menu:
                self.aspect_ratio = event.text
                
                if self.aspect_ratio != "Custom":
                    if self.aspect_ratio == "Original":
                        ratio = self.first_img_width / self.first_img_height
                    else:
                        ratio = self.aspect_ratio_presets[self.aspect_ratio]
                    
                    width_text = self.resolution_width_entry.get_text()
                    height_text = self.resolution_height_entry.get_text()
                    
                    image_ratio = self.first_img_width / self.first_img_height
                    
                    if ratio >= image_ratio:
                        if width_text.isdigit() and int(width_text) != 0:
                            self.resolution_height_entry.set_text(str(round(int(self.resolution_width_entry.get_text()) / ratio)))
                        elif height_text.isdigit() and int(height_text) != 0:
                            self.resolution_width_entry.set_text(str(round(int(self.resolution_height_entry.get_text()) * ratio)))
                        else:
                            if self.aspect_ratio == "Original":
                                self.resolution_width_entry.set_text(str(self.first_img_width))
                                self.resolution_height_entry.set_text(str(self.first_img_height))
                            else:
                                width = self.first_img_width
                                self.resolution_width_entry.set_text(str(width))
                                self.resolution_height_entry.set_text(str(round(width/ratio)))
                    else:
                        if height_text.isdigit() and int(height_text) != 0:
                            self.resolution_width_entry.set_text(str(round(int(self.resolution_height_entry.get_text()) * ratio)))
                        elif width_text.isdigit() and int(width_text) != 0:
                            self.resolution_height_entry.set_text(str(round(int(self.resolution_width_entry.get_text()) / ratio)))
                        else:
                            if self.aspect_ratio == "Original":
                                self.resolution_width_entry.set_text(str(self.first_img_width))
                                self.resolution_height_entry.set_text(str(self.first_img_height))
                            else:
                                height = self.first_img_height
                                self.resolution_width_entry.set_text(str(round(height*ratio)))
                                self.resolution_height_entry.set_text(str(height))
                                

                
                    self.video_resolution = (int(self.resolution_width_entry.get_text()), int(self.resolution_height_entry.get_text()))
                    if not self.check_resolution_valid():
                        self.resolution_error_msg.show()
                    else:
                        self.resolution_error_msg.hide()
            
            if event.ui_element == self.image_fitting_rule_menu:
                selected = self.image_fitting_rule_menu.selected_option[0]
                if selected == "Fit" or selected == "Fill":
                    self.image_fitting_rule = selected

            
            elif event.ui_element == self.anti_flickering_selector:
                self.anti_flickering = self.anti_flickering_selector.selected_option[0]
            
            elif event.ui_element == self.anti_flickering_sample_size_selector:
                self.anti_flickering_sample_size = self.anti_flickering_sample_size_selector.selected_option[0]
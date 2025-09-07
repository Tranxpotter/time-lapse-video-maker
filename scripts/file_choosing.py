from __future__ import annotations
import pygame
import pygame_gui
from pygame_gui.core import ObjectID
import tkinter as tk
from tkinter import filedialog
import os

from .scene import Scene

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..app import App



VALID_FILE_TYPES = {"jpg", "jpeg", "png", "bmp", "tiff", "tif", "JPG", "JPEG", "PNG", "BMP", "TIFF", "TIF"}

class FileChoosing(Scene):
    def __init__(self, app:App, manager:pygame_gui.UIManager):
        self.app = app
        self.manager = manager
        
        self.container = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, 1080, 720), 
            manager=self.manager
        )
        
        title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 1080, 100),
            text='Time Lapse Video Maker', 
            manager=self.manager,
            container=self.container,  
            anchors={"left":"left", "top":"top", "right":"right"}, 
            object_id=ObjectID(class_id="@title", object_id="#title_screen_title")
        )
        
        input_frame = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, -620, 1080, 620),
            manager=self.manager, 
            container=self.container, 
            anchors={"left":"left", "right":"right", "bottom":"bottom"},
        )
        
        label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 0, 200, 50),
            text='Chosen File Path:', 
            manager=self.manager, 
            container=input_frame, 
            anchors={"left":"left", "top":"top"},
            object_id=ObjectID(class_id="@label", object_id="#scene1_label")
        )
        
        self.file_path_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(-100, 0, 400, 50),
            text="", 
            manager=self.manager, 
            container=input_frame, 
            anchors={"centerx":"centerx", "top":"top"}, 
            object_id=ObjectID(class_id="@label", object_id="#file_path_label")
        )
        
        self.file_choosing_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 100, 50),
            text='Choose files',
            manager=self.manager, 
            anchors={"left":"left", "left_target":self.file_path_label}, 
            container=input_frame, 
            object_id=ObjectID(class_id="@file_choosing_btn", object_id="#file_choosing_btn")
        )
        
        self.confirm_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 100, 50),
            text='Confirm',
            manager=self.manager, 
            container=input_frame,
            anchors={"left":"left", "left_target":self.file_choosing_btn}, 
            object_id=ObjectID(class_id="@confirm_btn", object_id="#scene1_confirm_btn")
        )
        
        self.scene1_error_msg = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 1080, 50),
            text='Please choose a valid file path',
            manager=self.manager,
            container=input_frame, 
            anchors={"left":"left", "top":"top", "top_target":self.file_path_label}, 
            object_id=ObjectID(class_id="@error_msg", object_id="#scene1_error_msg")
        )
        self.scene1_error_msg.hide()
        
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 1080, 50),
            text='Select all images to include into the video',
            manager=self.manager,
            container=input_frame, 
            anchors={"left":"left", "top":"top", "top_target":self.scene1_error_msg}, 
            object_id=ObjectID(class_id="@label", object_id="#scene1_instructions")
        )
    
    def reset(self):
        self.file_path_label.set_text("")
        self.scene1_error_msg.hide()

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            #Scene 1 button events
            if event.ui_element == self.file_choosing_btn:
                self.scene1_error_msg.hide()
                filetypes = [("Image files", " ".join([f"*.{ext}" for ext in VALID_FILE_TYPES]))]
                # file_path = filedialog.askopenfilename(filetypes=filetypes)
                file_paths = filedialog.askopenfilenames(filetypes=filetypes)
                if file_paths:
                    file_path = file_paths[0]
                    self.file_paths = list(file_paths)
                else:
                    self.file_paths = []
                    file_path = ""
                    
                self.file_path_label.set_text(file_path)
            
            elif event.ui_element == self.confirm_btn:
                if not self.check_file_path_exists():
                    self.scene1_error_msg.show()
                elif not self.check_valid_file_types():
                    self.scene1_error_msg.show()
                else:
                    self.scene2()



    def check_file_path_exists(self):
        if not self.file_paths:
            return False
        for file_path in self.file_paths:
            if not os.path.exists(file_path):
                return False
        return True
    
    def check_valid_file_types(self):
        for file_path in self.file_paths:
            if not file_path.split(".")[-1] in VALID_FILE_TYPES:
                return False
        return True

    def scene2(self):
        self.app.to_scene2(self.file_paths)
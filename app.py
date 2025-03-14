import tkinter as tk
from tkinter import filedialog
import os

import pygame
pygame.init()
import pygame_gui
from pygame_gui.core import ObjectID
from pygame._sdl2 import Window

WINDOW_SIZE = (1080, 720)
VALID_FILE_TYPES = ["jpg", "jpeg", "png", "bmp", "tiff", "tif", "cr2"]



class App:
    def __init__(self):
        #Tkinter basic setups
        tk.Tk().withdraw()
        
        #Pygame basic setups
        self.window = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Time Lapse Video Maker")
        
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.running = True
        
        #Pygame GUI basic setups
        self.manager = pygame_gui.UIManager(WINDOW_SIZE, theme_path="themes/theme.json")

        
        self.scene1()
    
    def scene1(self):
        self.manager.clear_and_reset()
        
        
        title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 1080, 100),
            text='Time Lapse Video Maker', 
            manager=self.manager, 
            anchors={"left":"left", "top":"top", "right":"right"}, 
            object_id=ObjectID(class_id="@title", object_id="#title_screen_title")
        )
        
        input_frame = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, -620, 1080, 620),
            manager=self.manager, 
            anchors={"left":"left", "right":"right", "bottom":"bottom"},
        )
        
        label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 0, 200, 50),
            text='Enter the path:', 
            manager=self.manager, 
            container=input_frame, 
            anchors={"left":"left", "top":"top"},
            object_id=ObjectID(class_id="@label", object_id="#scene1_label")
        )
        
        self.file_path_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(-100, 0, 400, 50),
            manager=self.manager, 
            container=input_frame, 
            anchors={"centerx":"centerx", "top":"top"}, 
            object_id=ObjectID(class_id="@text_entry", object_id="#file_path_entry")
        )
        
        self.file_choosing_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 100, 50),
            text='Choose files',
            manager=self.manager, 
            anchors={"left":"left", "left_target":self.file_path_entry}, 
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
            anchors={"left":"left", "top":"top", "top_target":self.file_path_entry}, 
            object_id=ObjectID(class_id="@error_msg", object_id="#scene1_error_msg")
        )
        self.scene1_error_msg.hide()
    
    
    def scene2(self):
        #Load all image paths from the same file path
        self.file_path = self.file_path_entry.get_text()
        self.image_paths = []
        self.folder_path = os.path.dirname(self.file_path)
        
        for file in os.listdir(self.folder_path):
            if file.split(".")[-1] in VALID_FILE_TYPES:
                self.image_paths.append(os.path.join(self.folder_path, file))
        
        print(self.image_paths)
        
        #Initialize the UI layout for scene2
        self.manager.clear_and_reset()
        
        #Navigation bar
        nav_bar = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, 1080, 70),
            manager=self.manager, 
            anchors={"left":"left", "top":"top", "right":"right"},
        )
        
        self.scene2_back_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 100, 50),
            text='Back',
            manager=self.manager, 
            container=nav_bar, 
            anchors={"left":"left", "top":"top"}, 
            object_id=ObjectID(class_id="@nav_btn", object_id="#scene2_back_btn")
        )
        
        self.scene2_options_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 100, 50),
            text='Options',
            manager=self.manager, 
            container=nav_bar, 
            anchors={"left":"left", "left_target":self.scene2_back_btn}, 
            object_id=ObjectID(class_id="@nav_btn", object_id="#scene2_options_btn")
        )
        
        self.scene2_panning_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 100, 50),
            text='Panning',
            manager=self.manager, 
            container=nav_bar, 
            anchors={"left":"left", "left_target":self.scene2_options_btn}, 
            object_id=ObjectID(class_id="@nav_btn", object_id="#scene2_panning_btn")
        )
        
        self.scene2_preview_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 100, 50),
            text='Preview',
            manager=self.manager, 
            container=nav_bar, 
            anchors={"left":"left", "left_target":self.scene2_panning_btn}, 
            object_id=ObjectID(class_id="@nav_btn", object_id="#scene2_preview_btn")
        )
        
        self.scene2_export_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 100, 50),
            text='Export',
            manager=self.manager, 
            container=nav_bar, 
            anchors={"left":"left", "left_target":self.scene2_preview_btn}, 
            object_id=ObjectID(class_id="@nav_btn", object_id="#scene2_export_btn")
        )
        
        
        #Options screen
        self.scene2_options_screen = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, 1080, 650),
            manager=self.manager, 
            anchors={"left":"left", "top":"top", "right":"right", "bottom":"bottom"},
        )
        
        self.curr_active_screen = self.scene2_options_screen
        
        
        
        
    
    
    def check_file_path_exists(self):
        file_path = self.file_path_entry.get_text()
        return os.path.exists(file_path)
    
    def check_valid_file_types(self):
        file_path = self.file_path_entry.get_text()
        return file_path.split(".")[-1] in VALID_FILE_TYPES
    
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.file_choosing_btn:
                    self.scene1_error_msg.hide()
                    filetypes = [("Image files", " ".join([f"*.{ext}" for ext in VALID_FILE_TYPES]))]
                    file_path = filedialog.askopenfilename(filetypes=filetypes)
                    self.file_path_entry.set_text(file_path)
                
                elif event.ui_element == self.confirm_btn:
                    if not self.check_file_path_exists():
                        self.scene1_error_msg.show()
                    elif not self.check_valid_file_types():
                        self.scene1_error_msg.show()
                    else:
                        self.scene2()
                
                elif event.ui_element == self.scene2_back_btn:
                    self.scene1()
                
                elif event.ui_element == self.scene2_options_btn:
                    self.curr_active_screen.hide()
                    self.scene2_options_screen.show()
            
            
            
            
            self.manager.process_events(event)
            
    
    def update(self):
        self.manager.update(self.dt)
    
    def draw(self):
        self.window.fill((0, 0, 0))
        self.manager.draw_ui(self.window)
        pygame.display.update()
    
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            
            self.dt = self.clock.tick(60) / 1000
            











if __name__ == "__main__":
    app = App()
    app.run()
    pygame.quit()

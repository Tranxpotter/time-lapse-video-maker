import tkinter as tk
from tkinter import filedialog
import os
import json

import pygame
import pygame_gui.core.object_id
pygame.init()
import pygame_gui
from pygame_gui.core import ObjectID
from pygame._sdl2 import Window

import cv2

WINDOW_SIZE = (1080, 720)
VALID_FILE_TYPES = ["jpg", "jpeg", "png", "bmp", "tiff", "tif", "cr2", "JPG", "JPEG", "PNG", "BMP", "TIFF", "TIF", "CR2"]



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
        
        #Reset changing theme
        with open(f"themes/changing_theme.json", "w") as f:
            json.dump({}, f, indent=2)
        self.manager.get_theme().load_theme("themes/changing_theme.json")

        
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
        
        
        
        for file in sorted(os.listdir(self.folder_path)):
            if file.split(".")[-1] in VALID_FILE_TYPES:
                self.image_paths.append(os.path.join(self.folder_path, file))
        

        
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
            text='Back',
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
        self.video_resolution = (0, 0)
        self.fps = 30
        
        #Panning screen
        self.panning = dict() #For storing panning results
        self.panning_active = False #For checking if panning function should be active
        
        
        
        
        #Initialize first active screen
        self.initialize_options_screen()
        self.curr_active_screen = self.scene2_options_screen
        self.curr_disabled_btn = self.scene2_options_btn
        self.scene2_options_btn.disable()
        
    
    
    def initialize_options_screen(self):
        self.scene2_options_screen = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, 1080, 650),
            manager=self.manager, 
            anchors={"left":"left", "right":"right", "top":"top", "top_target":self.nav_bar},
        )
        
        self.scene2_options_screen_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 200, 50),
            text='Options:', 
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top"},
            object_id=ObjectID(class_id="@title2", object_id="#scene2_options_screen_label")
        )
        
        #Resolution input
        resolution_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 200, 50),
            text='Resolution:', 
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.scene2_options_screen_label},
            object_id=ObjectID(class_id="@title3", object_id="#resolution_label")
        )
        
        width_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            text='Width:', 
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":resolution_label},
            object_id=ObjectID(class_id="@label", object_id="#width_label")
        )
        
        self.resolution_width_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":resolution_label, "left_target":width_label}, 
            object_id=ObjectID(class_id="@option_entry", object_id="#resolution_width_entry")
        )
        
        height_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            text='Height:', 
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":resolution_label, "left_target":self.resolution_width_entry},
            object_id=ObjectID(class_id="@label", object_id="#height_label")
        )
        
        self.resolution_height_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":resolution_label, "left_target":height_label}, 
            object_id=ObjectID(class_id="@option_entry", object_id="#resolution_height_entry")
        )
        
        self.resolution_set_to_first_image_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, 300, 50),
            text='Set resolution to first image',
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":resolution_label, "left_target":self.resolution_height_entry}, 
            object_id=ObjectID(class_id="@option_btn", object_id="#resolution_set_to_first_image_btn")
        )
        
        self.resolution_error_msg = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 300, 50),
            text='Please enter a valid resolution',
            manager=self.manager,
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_height_entry}, 
            object_id=ObjectID(class_id="@error_msg", object_id="#resolution_error_msg"), 
            visible=False
        )
        
        
        #FPS input
        fps_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            text='FPS:', 
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_error_msg},
            object_id=ObjectID(class_id="@label", object_id="#fps_label")
        )
        
        self.fps_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_error_msg, "left_target":fps_label}, 
            object_id=ObjectID(class_id="@option_entry", object_id="#fps_entry")
        )
        self.fps_entry.set_text(str(self.fps))
        
        self.video_length_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 300, 50),
            text='Video Length:',
            manager=self.manager,
            container=self.scene2_options_screen,
            anchors={"left":"left", "top":"top", "top_target":self.fps_entry},
            object_id=ObjectID(class_id="@label", object_id="#video_length_label")
        )
        
        self.fps_error_msg = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 300, 50),
            text='Please enter a valid FPS',
            manager=self.manager,
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.video_length_label}, 
            object_id=ObjectID(class_id="@error_msg", object_id="#fps_error_msg")
        )

        self.smoothing_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 150, 50),
            text='Smoothing:', 
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.fps_error_msg},
            object_id=ObjectID(class_id="@label", object_id="#smoothing_label")
        )
        
        self.smoothing_selector = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(0, 0, 200, 50),
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.fps_error_msg, "left_target":self.smoothing_label}, 
            object_id=ObjectID(class_id="@option_entry", object_id="#smoothing_selector"),
            options_list=["On", "Off"], 
            starting_option="Off"
        )
        
        first_image = pygame.image.load(self.image_paths[0])
        width, height = first_image.get_width(), first_image.get_height()
        self.resolution_width_entry.set_text(str(width))
        self.resolution_height_entry.set_text(str(height))
        self.video_resolution = (int(width), int(height))
        if not self.check_resolution_valid():
            self.resolution_error_msg.show()
        else:
            self.resolution_error_msg.hide()
        
        if not self.check_fps_valid():
            self.fps_error_msg.show()
        else:
            self.fps_error_msg.hide()
        
    
    def check_resolution_valid(self):
        '''Check if the resolution entered is valid, returns True if valid, False otherwise'''
        if self.video_resolution[0] == 0 or self.video_resolution[1] == 0:
            return False
        return True

    def check_fps_valid(self):
        '''Check if the fps entered is valid, returns True if valid, False otherwise'''
        fps = self.fps_entry.get_text()
        return fps.isdigit() and int(fps) != 0
    
    
    
    def initialize_panning_screen(self):
        #Initialize the UI layout for panning screen
        self.scene2_panning_screen = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, 1080, 650),
            manager=self.manager, 
            anchors={"left":"left", "right":"right", "top":"top", "top_target":self.nav_bar},
        )
        
        self.panning_image_select = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(-380, 0, 380, 650),
            item_list=[(name, f"#Select_{name}_btn") for name in self.get_image_names()],
            manager=self.manager, 
            container=self.scene2_panning_screen, 
            anchors={"right":"right", "top":"top"}, 
            object_id=ObjectID(class_id="@selection_list", object_id="#image_select"), 
            default_selection=(self.get_image_names()[0], f"#Select_{self.get_image_names()[0]}_btn")
        )
        
        
        self.panning_image_display_size = self.panning_image_display_width, self.panning_image_display_height = (700, 500)
        
        self.panning_image_display_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), self.panning_image_display_size),
            manager=self.manager, 
            container=self.scene2_panning_screen, 
            anchors={"left":"left", "top":"top"}, 
            object_id=ObjectID(class_id="@panel", object_id="#image_display")
        )

        self.initialize_image_display(self.image_paths[0])
        
        #Panning screen option buttons
        self.zoom_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            text='Zoom:', 
            manager=self.manager, 
            container=self.scene2_panning_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.panning_image_display_panel},
            object_id=ObjectID(class_id="@label", object_id="#panning_zoom_label")
        )
        self.zoom_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(0, 0, 400, 30), 
            start_value=0.0, 
            value_range=(0.0, 1.0), 
            manager=self.manager, 
            container=self.scene2_panning_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.panning_image_display_panel, "left_target":self.zoom_label}, 
            object_id=ObjectID(class_id="@slider", object_id="#panning_zoom_slider")
        )
        self.zoom_slider.set_current_value(self.panning_zoom_level)
        
        self.zoom_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            manager=self.manager, 
            container=self.scene2_panning_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.panning_image_display_panel, "left_target":self.zoom_slider}, 
            object_id=ObjectID(class_id="@option_entry", object_id="#panning_zoom_entry")
        )
        self.zoom_entry.set_text(str(self.panning_zoom_level))
        
        self.panning_reset_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 20, 100, 50),
            text='Reset',
            manager=self.manager, 
            container=self.scene2_panning_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.zoom_slider}, 
            object_id=ObjectID(class_id="@button", object_id="#panning_reset_btn")
        )
        
        self.panning_save_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 20, 100, 50),
            text='Save',
            manager=self.manager, 
            container=self.scene2_panning_screen, 
            anchors={"left":"left", "top":"top", "left_target":self.panning_reset_btn, "top_target":self.zoom_slider}, 
            object_id=ObjectID(class_id="@button", object_id="#panning_save_btn")
        )
        
        self.panning_delete_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 20, 100, 50),
            text='Delete',
            manager=self.manager, 
            container=self.scene2_panning_screen, 
            anchors={"left":"left", "top":"top", "left_target":self.panning_save_btn, "top_target":self.zoom_slider}, 
            object_id=ObjectID(class_id="@button", object_id="#panning_delete_btn")
        )
        if self.panning_image_path not in self.panning:
            self.panning_delete_btn.disable()
        
        
        self.panning_exclude_image_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 20, 200, 50),
            text='Exclude Image',
            manager=self.manager, 
            container=self.scene2_panning_screen, 
            anchors={"left":"left", "top":"top", "left_target":self.panning_delete_btn, "top_target":self.zoom_slider}, 
            object_id=ObjectID(class_id="@button", object_id="#panning_exclude_image_btn")
        )
        
        

    
    def initialize_image_display(self, image_path):
        # Initialize viewing variables
        self.panning_view_top_left = (0, 0)
        self.panning_view_width = self.panning_image_display_width
        self.panning_view_height = self.panning_image_display_height
        
        # 0. Get the panning information for the image
        if image_path not in self.panning:
            self.panning_image_top_left = (0, 0)
            self.panning_image_width = self.video_resolution[0]
            self.panning_image_height = self.video_resolution[1]
            self.panning_zoom_level = 0
        else:
            self.panning_image_top_left = self.panning[image_path]["top_left"]
            self.panning_image_width = self.panning[image_path]["width"]
            self.panning_image_height = self.panning[image_path]["height"]
            self.panning_zoom_level = self.panning[image_path]["zoom_level"]
        
        self.panning_image_path = image_path
        self.panning_image = pygame.image.load(image_path)
        self.update_image_display()
    
    
    
    def update_image_display(self):
        #Reset the panning image display
        if hasattr(self, "panning_image_display"):
            self.panning_image_display.kill()
        
        # 1. Create the panning selector
        selector = pygame.Surface((self.panning_image_width, self.panning_image_height)).convert_alpha()
        selector.fill((0, 0, 0, 50))
        
        # 2. Initialize image
        panning_curr_image = self.panning_image.copy()
        # 3. Put selector on the image
        panning_curr_image.blit(selector, self.panning_image_top_left)
        
        # 4. Crop image according to view pos and size
        # cropped_surface = pygame.Surface((self.panning_view_width, self.panning_view_height)).convert_alpha()
        # cropped_surface.fill((0, 0, 0, 0))
        # cropped_surface.blit(panning_curr_image, (0, 0), pygame.Rect(self.panning_view_top_left, (self.panning_view_width, self.panning_view_height)))
        # panning_curr_image = cropped_surface
        panning_curr_image = panning_curr_image.subsurface(pygame.Rect(self.panning_view_top_left, (self.panning_image_width, self.panning_image_height)))
        # print(panning_curr_image.get_size())
        
        # 5. Calculate scaling ratio for display
        scaling_ratio = max(panning_curr_image.get_width() / self.panning_image_display_width, panning_curr_image.get_height() / self.panning_image_display_height)
        scaled_width = panning_curr_image.get_width() / scaling_ratio
        scaled_height = panning_curr_image.get_height() / scaling_ratio
        
        # 6. Scale the image
        panning_curr_image = pygame.transform.scale(panning_curr_image, (int(scaled_width), int(scaled_height)))
        
        # And now the preview image is ready to be displayed
        self.panning_image_display = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(0, 0, self.panning_image_display_width, self.panning_image_display_height),
            image_surface=panning_curr_image,
            manager=self.manager,
            container=self.panning_image_display_panel,
            anchors={"left":"left", "top":"top"},
            object_id=ObjectID(class_id="@image", object_id="#image_display")
        )
    
    
    
    
    
    
    
        
    def get_image_names(self):
        return [os.path.basename(image_path) for image_path in self.image_paths]
    
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
                
            #Button pressed events
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                #Scene 1 button events
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
                
                #Scene 2 button events
                elif event.ui_element == self.scene2_back_btn:
                    self.scene1()
                
                elif event.ui_element == self.scene2_options_btn:
                    self.curr_disabled_btn.enable()
                    self.curr_active_screen.kill()
                    self.curr_disabled_btn = self.scene2_options_btn
                    self.initialize_options_screen()
                    self.curr_active_screen = self.scene2_options_screen
                    self.scene2_options_btn.disable()
                    self.panning_active = False
                
                elif event.ui_element == self.scene2_panning_btn:
                    self.curr_disabled_btn.enable()
                    self.curr_active_screen.kill()
                    self.curr_disabled_btn = self.scene2_panning_btn
                    self.initialize_panning_screen()
                    self.curr_active_screen = self.scene2_panning_screen
                    self.scene2_panning_btn.disable()
                    self.panning_active = True
                
                elif event.ui_element == self.scene2_preview_btn:
                    self.panning_active = False
                
                
                
                #Option screen button events
                elif event.ui_element == self.resolution_set_to_first_image_btn:
                    first_image = pygame.image.load(self.image_paths[0])
                    width, height = first_image.get_width(), first_image.get_height()
                    self.resolution_width_entry.set_text(str(width))
                    self.resolution_height_entry.set_text(str(height))
                    self.video_resolution = (int(width), int(height))
                    if not self.check_resolution_valid():
                        self.resolution_error_msg.show()
                    else:
                        self.resolution_error_msg.hide()
                
                
                
            
            
            #Text entry changed events
            elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                if event.ui_element == self.file_path_entry:
                    self.scene1_error_msg.hide()
                
                elif event.ui_element == self.resolution_width_entry or event.ui_element == self.resolution_height_entry:
                    width = self.resolution_width_entry.get_text()
                    height = self.resolution_height_entry.get_text()
                    if not (width.isdigit() and height.isdigit()):
                        self.resolution_error_msg.show()
                    else:
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
                        video_length = round(len(self.image_paths) / int(fps), 1)
                        self.video_length_label.set_text(f"Video Length: {video_length} seconds")
                
                
            #Selection list events
            elif event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                if event.ui_element == self.panning_image_select:
                    image_name = event.text
                    image_path = os.path.join(self.folder_path, image_name)
                    self.initialize_image_display(image_path)
                    
                    # with open(f"themes/changing_theme.json", "r") as f:
                    #     theme = json.load(f)
                    # theme[f"#Select_{image_name}_btn"] = {"colours" : {"selected_bg":"rgb(0, 0, 255)", "normal_border":"rgb(255, 0, 0)"}}
                    # with open(f"themes/changing_theme.json", "w") as f:
                    #     json.dump(theme, f, indent=2)
            
            
            
            
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

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import threading
import sys

import pygame
pygame.init()
import pygame_gui
from pygame_gui.core import ObjectID

import cv2



WINDOW_SIZE = (1080, 720)
VALID_FILE_TYPES = ["jpg", "jpeg", "png", "bmp", "tiff", "tif", "JPG", "JPEG", "PNG", "BMP", "TIFF", "TIF"]



class App:
    def __init__(self):
        #Get program base path
        if getattr(sys, 'frozen', False):
            self.application_path = sys._MEIPASS
        else:
            self.application_path = os.path.dirname(os.path.abspath(__file__))
        
        # with open(os.path.join(self.application_path, "data/themes/theme.json"), "r") as f:
        #     theme = json.load(f)
        # theme["label"]["font"]
        
        #Tkinter basic setups
        tk.Tk().withdraw()
        
        #Pygame basic setups
        self.window = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Time Lapse Video Maker")
        
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.running = True
        
        self.panning_active = False
        self.dragging = False
        self.preview_playing = False
        self.zoom_ratio_per_level = 0.02
        self.exporting = False
        
        
        #fonts path setup
        with open(os.path.join(self.application_path, "data/themes/paths.json"), "r") as f:
            paths = json.load(f)
        
        for k in paths:
            paths[k] = self.application_path + "/" + paths[k]
        
        with open(os.path.join(self.application_path, "data/themes/fonts.json"), "r") as f:
            data = json.load(f)
        
        data["label"]["font"] |= paths
        with open(os.path.join(self.application_path, "data/themes/fonts.json"), "w") as f:
            json.dump(data, f, indent=2)
        
        
        #Pygame GUI basic setups
        self.manager = pygame_gui.UIManager(WINDOW_SIZE, theme_path=os.path.join(self.application_path, "data/themes/fonts.json"))
        self.manager.get_theme().load_theme(os.path.join(self.application_path, "data/themes/theme.json"))
        #Reset changing theme
        with open(os.path.join(self.application_path, "data/themes/changing_theme.json"), "w") as f:
            json.dump({}, f, indent=2)
        self.manager.get_theme().load_theme(os.path.join(self.application_path, "data/themes/changing_theme.json"))

        
        
        self.scene1()
    
    def load_image(self, image_path):
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        surface = pygame.surfarray.make_surface(img.swapaxes(0, 1))
        return surface
    
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
        
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 1080, 50),
            text='Choose a file within a folder, the rest of the images in the folder will be automatically included.',
            manager=self.manager,
            container=input_frame, 
            anchors={"left":"left", "top":"top", "top_target":self.scene1_error_msg}, 
            object_id=ObjectID(class_id="@label", object_id="#scene1_instructions")
        )
    
    
    def scene2(self):
        #Load all image paths from the same file path
        self.file_path = self.file_path_entry.get_text()
        self.image_paths = []
        self.folder_path = os.path.dirname(self.file_path)
        
        
        
        for file in sorted(os.listdir(self.folder_path)):
            ext = file.split(".")[-1]
            if ext in VALID_FILE_TYPES:
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
        self.fps = 30
        first_image = self.load_image(self.image_paths[0])
        self.first_img_width, self.first_img_height = first_image.get_width(), first_image.get_height()
        self.video_resolution = (int(self.first_img_width), int(self.first_img_height))
        self.aspect_ratio = "Custom"
        self.anti_flickering = "Off"
        self.anti_flickering_sample_size = "7"
        
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
        
        
        self.resolution_aspect_ratio_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 0, 200, 50), 
            text="Aspect Ratio:", 
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":resolution_label, "left_target":self.resolution_height_entry}, 
            object_id=ObjectID(class_id="@label", object_id="#resolution_presets_label")
        )
        self.resolution_aspect_ratio_menu = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(0, 0, 100, 50), 
            starting_option="Custom" if not hasattr(self, "aspect_ratio") else self.aspect_ratio, 
            options_list=["Custom", "Original", "16:9", "1:1", "9:16", "4:3", "4:5", "21:9", "3:2"],
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":resolution_label, "left_target":self.resolution_aspect_ratio_label}, 
        )
        self.aspect_ratio_presets = {"16:9":16/9, "1:1":1, "9:16":9/16, "4:3":4/3, "4:5":4/5, "21:9":21/9, "3:2":3/2}
        
        
        self.resolution_preset_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 200, 50), 
            text="Resolution Presets:", 
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_aspect_ratio_menu}, 
            object_id=ObjectID(class_id="@label", object_id="#resolution_presets_label")
        )
        self.resolution_preset_first_image_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 120, 50), 
            text="First Image", 
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_aspect_ratio_menu, "left_target":self.resolution_preset_label}
        )
        self.resolution_preset_360p_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 50, 50), 
            text="360", 
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_aspect_ratio_menu, "left_target":self.resolution_preset_first_image_btn}
        )
        self.resolution_preset_SD_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 50, 50), 
            text="480", 
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_aspect_ratio_menu, "left_target":self.resolution_preset_360p_btn}
        )
        self.resolution_preset_720p_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 50, 50), 
            text="720", 
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_aspect_ratio_menu, "left_target":self.resolution_preset_SD_btn}
        )
        self.resolution_preset_FHD_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 50, 50), 
            text="1080", 
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_aspect_ratio_menu, "left_target":self.resolution_preset_720p_btn}
        )
        self.resolution_preset_QHD_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 50, 50), 
            text="1440", 
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_aspect_ratio_menu, "left_target":self.resolution_preset_FHD_btn}
        )
        self.resolution_preset_4K_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 50, 50), 
            text="2160", 
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_aspect_ratio_menu, "left_target":self.resolution_preset_QHD_btn}
        )
        self.resolution_preset_8K_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 0, 50, 50), 
            text="4320", 
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_aspect_ratio_menu, "left_target":self.resolution_preset_4K_btn}
        )
        
        
    
        self.resolution_error_msg = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 300, 50),
            text='Please enter a valid resolution',
            manager=self.manager,
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.resolution_preset_label}, 
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
        
        #Anti flickering stuff
        self.anti_flickering_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 150, 50),
            text='Anti-flickering:', 
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.fps_error_msg},
            object_id=ObjectID(class_id="@label", object_id="#anti_flickering")
        )
        
        self.anti_flickering_selector = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(0, 0, 200, 50),
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.fps_error_msg, "left_target":self.anti_flickering_label}, 
            object_id=ObjectID(class_id="@option_entry", object_id="#anti_flickering_selector"),
            options_list=["On", "Off"], 
            starting_option=self.anti_flickering
        )
        
        self.anti_flickering_sample_size_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(50, 0, 150, 50),
            text='Sample Size:', 
            manager=self.manager, 
            container=self.scene2_options_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.fps_error_msg, "left_target":self.anti_flickering_selector},
            object_id=ObjectID(class_id="@label", object_id="#anti_flickering")
        )
        
        self.anti_flickering_sample_size_selector = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(0, 0, 200, 50),
            manager=self.manager, 
            container=self.scene2_options_screen, 
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
            video_length = round(len(self.image_paths) / self.fps, 1)
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
    
    
    
    def initialize_panning_screen(self):
        #Initialize the UI layout for panning screen
        self.scene2_panning_screen = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, 1080, 650),
            manager=self.manager, 
            anchors={"left":"left", "right":"right", "top":"top", "top_target":self.nav_bar},
        )
        
        self.panning_image_select = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(-370, 0, 370, 650),
            item_list=[(name, f"#Select_{name}_btn") for name in self.get_image_names()],
            manager=self.manager, 
            container=self.scene2_panning_screen, 
            anchors={"right":"right", "top":"top"}, 
            object_id=ObjectID(class_id="@selection_list", object_id="#image_select"), 
            default_selection=(self.get_image_names()[0], f"#Select_{self.get_image_names()[0]}_btn")
        )
        
        
        self.panning_image_display_size = self.panning_image_display_width, self.panning_image_display_height = (700, 500)
        
        self.panning_image_display_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (self.panning_image_display_width+3, self.panning_image_display_height+3)),
            manager=self.manager, 
            container=self.scene2_panning_screen, 
            anchors={"left":"left", "top":"top"}, 
            object_id=ObjectID(class_id="@panel", object_id="#image_display")
        )

        
        
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
            relative_rect=pygame.Rect(0, 10, 400, 30), 
            start_value=1, 
            value_range=(1, 50), 
            manager=self.manager, 
            container=self.scene2_panning_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.panning_image_display_panel, "left_target":self.zoom_label}, 
            object_id=ObjectID(class_id="@slider", object_id="#panning_zoom_slider")
        )
        
        self.zoom_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            manager=self.manager, 
            container=self.scene2_panning_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.panning_image_display_panel, "left_target":self.zoom_slider}, 
            object_id=ObjectID(class_id="@option_entry", object_id="#panning_zoom_entry")
        )
        
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
        
        
        self.panning_exclude_image_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 20, 200, 50),
            text='Exclude Image',
            manager=self.manager, 
            container=self.scene2_panning_screen, 
            anchors={"left":"left", "top":"top", "left_target":self.panning_delete_btn, "top_target":self.zoom_slider}, 
            object_id=ObjectID(class_id="@button", object_id="#panning_exclude_image_btn")
        )
        if len(self.image_paths) == 1:
            self.panning_exclude_image_btn.disable()
        elif len(self.image_paths) == 0:
            raise Exception("Hey there's no image paths in the list, what's going on??")
        
        
        self.panning_save_msg = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            text='Saved', 
            manager=self.manager, 
            container=self.scene2_panning_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.panning_exclude_image_btn},
            object_id=ObjectID(class_id="@label", object_id="#panning_zoom_label")
        )
        self.panning_save_msg.hide()
        
        self.panning_initialize_image_display(self.image_paths[0])
    
    
    
    
    def panning_initialize_image_display(self, image_path):
        # Load image
        self.panning_image_path = image_path
        self.panning_image = self.load_image(image_path)
        
        width_ratio = self.video_resolution[0] / self.panning_image.get_width()
        height_ratio = self.video_resolution[1] / self.panning_image.get_height()
        scaling_ratio = max(width_ratio, height_ratio)
        self.base_panning_selected_width = int(self.video_resolution[0] / scaling_ratio)
        self.base_panning_selected_height = int(self.video_resolution[1] / scaling_ratio)
        
        # 0. Get the panning information for the image
        if image_path not in self.panning:
            self.panning_selected_top_left = (0, 0)
            # print(self.panning_selected_width, self.panning_selected_height)
            self.panning_zoom_level = 1
            self.panning_delete_btn.disable()
        else:
            self.panning_selected_top_left = self.panning[image_path]["top_left"]
            self.panning_zoom_level = self.panning[image_path]["zoom_level"]
            self.panning_delete_btn.enable()
        
        self.zoom_entry.set_text(str(self.panning_zoom_level))
        self.zoom_slider.set_current_value(self.panning_zoom_level)
        
        
        self.panning_update_image_display()
    
    
    def calc_zoom_value(self, zoom:int, val:int|float):
        zoom_ratio = 1 - (zoom-1) * self.zoom_ratio_per_level
        return int(val * zoom_ratio)
    
    
    def panning_update_image_display(self):
        self.panning_save_msg.hide()
        #Reset the panning image display
        if hasattr(self, "panning_image_display"):
            self.panning_image_display.kill()
        
        # 2. Initialize image
        panning_curr_image = self.panning_image
        
        # 3. Calculate width and height from zoom level
        self.panning_selected_width, self.panning_selected_height = self.calc_zoom_value(self.panning_zoom_level, self.base_panning_selected_width), self.calc_zoom_value(self.panning_zoom_level, self.base_panning_selected_height)
        
        # 4. Move selecteed topleft if selected area is out of range
        self.panning_selected_top_left = (min(self.panning_image.get_width() - self.panning_selected_width, self.panning_selected_top_left[0]), min(self.panning_image.get_height() - self.panning_selected_height, self.panning_selected_top_left[1]))
        # print(self.panning_selected_top_left)
        
        # 4. Crop image according to selected pos and size
        panning_curr_image = panning_curr_image.subsurface(pygame.Rect(self.panning_selected_top_left, (self.panning_selected_width, self.panning_selected_height)))
        
        panning_curr_image = pygame.transform.scale(panning_curr_image, self.video_resolution)
        
        # 5. Calculate scaling ratio for display
        scaling_ratio = max(panning_curr_image.get_width() / self.panning_image_display_width, panning_curr_image.get_height() / self.panning_image_display_height)
        self.panning_scaled_width = int(panning_curr_image.get_width() / scaling_ratio)
        self.panning_scaled_height = int(panning_curr_image.get_height() / scaling_ratio)
        
        
        
        # 6. Scale the image
        panning_curr_image = pygame.transform.scale(panning_curr_image, (self.panning_scaled_width, self.panning_scaled_height))
        
        # And now the preview image is ready to be displayed
        self.panning_image_display = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(0, 0, self.panning_scaled_width, self.panning_scaled_height),
            image_surface=panning_curr_image,
            manager=self.manager,
            container=self.panning_image_display_panel,
            anchors={"center":"center"},
            object_id=ObjectID(class_id="@image", object_id="#image_display")
        )
    
    
    
    
    
    def initialize_preview_screen(self):
        self.scene2_preview_screen = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, 1080, 650),
            manager=self.manager, 
            anchors={"left":"left", "right":"right", "top":"top", "top_target":self.nav_bar},
        )
        
        self.preview_image_select = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(-370, 0, 370, 650),
            item_list=[(name, f"#Preview_{name}_btn") for name in self.get_image_names()],
            manager=self.manager, 
            container=self.scene2_preview_screen, 
            anchors={"right":"right", "top":"top"}, 
            object_id=ObjectID(class_id="@selection_list", object_id="#image_select"), 
            default_selection=(self.get_image_names()[0], f"#Preview_{self.get_image_names()[0]}_btn")
        )
        
        
        self.preview_image_display_size = self.preview_image_display_width, self.preview_image_display_height = (700, 500)
        
        self.preview_image_display_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (self.preview_image_display_width+3, self.preview_image_display_height+3)),
            manager=self.manager, 
            container=self.scene2_preview_screen, 
            anchors={"left":"left", "top":"top"}, 
            object_id=ObjectID(class_id="@panel", object_id="#image_display")
        )
        
        
        
        self.preview_video_first_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            text='1', 
            manager=self.manager, 
            container=self.scene2_preview_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.preview_image_display_panel},
            object_id=ObjectID(class_id="@label", object_id="#panning_zoom_label")
        )
        self.preview_video_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(0, 10, 400, 30), 
            start_value=1, 
            value_range=(1, len(self.image_paths)), 
            manager=self.manager, 
            container=self.scene2_preview_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.preview_image_display_panel, "left_target":self.preview_video_first_label}, 
            object_id=ObjectID(class_id="@slider", object_id="#panning_zoom_slider")
        )
        self.preview_video_last_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            text=str(len(self.image_paths)), 
            manager=self.manager, 
            container=self.scene2_preview_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.preview_image_display_panel, "left_target":self.preview_video_slider},
            object_id=ObjectID(class_id="@label", object_id="#panning_zoom_label")
        )
        
        self.preview_video_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            manager=self.manager, 
            container=self.scene2_preview_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.preview_image_display_panel, "left_target":self.preview_video_last_label}, 
            object_id=ObjectID(class_id="@option_entry", object_id="#panning_zoom_entry")
        )
        
        self.preview_skip_amount = len(self.image_paths) // 10
        
        self.preview_skip_back_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50), 
            text="<<", 
            manager=self.manager, 
            container=self.scene2_preview_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.preview_video_entry}, 
            object_id=ObjectID(class_id="@video_control_btn", object_id="#preview_skip_back_btn")
        )
        
        self.preview_back_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50), 
            text="<", 
            manager=self.manager, 
            container=self.scene2_preview_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.preview_video_entry, "left_target":self.preview_skip_back_btn}, 
            object_id=ObjectID(class_id="@video_control_btn", object_id="#preview_back_btn")
        )
        
        self.preview_play_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, 100, 50), 
            text="Play", 
            manager=self.manager, 
            container=self.scene2_preview_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.preview_video_entry, "left_target":self.preview_back_btn}, 
            object_id=ObjectID(class_id="@video_control_btn", object_id="#preview_play_btn")
        )
        
        self.preview_forward_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50), 
            text=">", 
            manager=self.manager, 
            container=self.scene2_preview_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.preview_video_entry, "left_target":self.preview_play_btn}, 
            object_id=ObjectID(class_id="@video_control_btn", object_id="#preview_forward_btn")
        )
        
        self.preview_skip_forward_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50), 
            text=">>", 
            manager=self.manager, 
            container=self.scene2_preview_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.preview_video_entry, "left_target":self.preview_forward_btn}, 
            object_id=ObjectID(class_id="@video_control_btn", object_id="#preview_skip_forward_btn")
        )
        
        # todo: Add fast play? like show only 1 in 10 photos type speed up
        
        self.preview_image_name_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 300, 50), 
            text="", 
            manager=self.manager, 
            container=self.scene2_preview_screen, 
            anchors={"left":"left", "top":"top", "top_target":self.preview_video_entry, "left_target":self.preview_skip_forward_btn}, 
            object_id=ObjectID(class_id="@label", object_id="#preview_image_name_label")
        )
        
        
        self.preview_display_details = self.panning_to_display_details()
        self.preview_show_image(self.image_paths[0])
        
        
        
    def preview_show_image(self, image_path):
        with open(os.path.join(self.application_path, "data/themes/changing_theme.json"), "r") as f:
            theme = json.load(f)
        if hasattr(self, "preview_showing_image_path"):
            if f"#Preview_{os.path.basename(self.preview_showing_image_path)}_btn" in theme:
                theme[f"#Preview_{os.path.basename(self.preview_showing_image_path)}_btn"] = {"colours":{"normal_bg":"rgb(76, 80, 82)", "hovered_bg":"rgb(99, 104, 107)", "selected_bg":"rgb(54, 88, 128)", "active_bg":"rgb(54, 88, 128)"}}
        theme[f"#Preview_{os.path.basename(image_path)}_btn"] = {"colours":{"normal_bg":"rgb(255, 0, 0)", "hovered_bg":"rgb(255, 0, 0)", "selected_bg":"rgb(255, 0, 0)", "active_bg":"rgb(255, 0, 0)"}}
        with open(os.path.join(self.application_path, "data/themes/changing_theme.json"), "w") as f:
            json.dump(theme, f, indent=2)
        
        self.preview_image_select.rebuild_from_changed_theme_data()
        
        
        self.preview_showing_image_path = image_path
        if hasattr(self, "preview_image_display"):
            self.preview_image_display.kill()
        preview_image = self.load_image(image_path)
        width_ratio = self.video_resolution[0] / preview_image.get_width()
        height_ratio = self.video_resolution[1] / preview_image.get_height()
        scaling_ratio = max(width_ratio, height_ratio)
        image_base_width = int(self.video_resolution[0] / scaling_ratio)
        image_base_height = int(self.video_resolution[1] / scaling_ratio)
        
        display_details = self.preview_display_details[image_path]
        topleft = display_details["top_left"]
        zoom_level = display_details["zoom_level"]
        
        crop_width, crop_height = self.calc_zoom_value(zoom_level, image_base_width), self.calc_zoom_value(zoom_level, image_base_height)
        # print(topleft, crop_width, crop_height, image_base_width, image_base_height)
        preview_image = preview_image.subsurface(pygame.Rect((topleft), (crop_width, crop_height)))
        preview_image = pygame.transform.scale(preview_image, self.video_resolution)
        
        # 5. Calculate scaling ratio for display
        scaling_ratio = max(preview_image.get_width() / self.preview_image_display_width, preview_image.get_height() / self.preview_image_display_height)
        scaled_width = int(preview_image.get_width() / scaling_ratio)
        scaled_height = int(preview_image.get_height() / scaling_ratio)
        
        # 6. Scale the image
        preview_image = pygame.transform.scale(preview_image, (scaled_width, scaled_height))
        
        self.preview_image_display = pygame_gui.elements.UIImage(relative_rect=pygame.Rect(0, 0, scaled_width, scaled_height),
            image_surface=preview_image,
            manager=self.manager,
            container=self.preview_image_display_panel,
            anchors={"center":"center"},
            object_id=ObjectID(class_id="@image", object_id="#image_display")
        )
        
        #Update preview screen ui
        image_index = self.image_paths.index(image_path)+1
        self.preview_video_slider.set_current_value(image_index)
        self.preview_video_entry.set_text(str(image_index))
        self.preview_image_name_label.set_text("Showing: " + str(os.path.basename(image_path)))
        
        
    
    
    def initialize_export_screen(self):
        self.scene2_export_screen = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, 1080, 650),
            manager=self.manager, 
            anchors={"left":"left", "right":"right", "top":"top", "top_target":self.nav_bar},
        )
        
        
        self.export_video_resolution_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(30, 0, 1050, 50), 
            text=f"Video Resolution: {self.video_resolution[0]}x{self.video_resolution[1]}", 
            manager = self.manager, 
            container = self.scene2_export_screen, 
            anchors = {"left":"left", "top":"top"}, 
            object_id=ObjectID(class_id="@export_info_label", object_id="#export_video_resolution_label")
        )
        
        self.export_video_fps_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(30, 0, 1050, 50), 
            text=f"Frames per Second: {self.fps}", 
            manager = self.manager, 
            container = self.scene2_export_screen, 
            anchors = {"left":"left", "top":"top", "top_target":self.export_video_resolution_label}, 
            object_id=ObjectID(class_id="@export_info_label", object_id="#export_video_fps_label")
        )
        
        self.export_video_img_count_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(30, 0, 1050, 50), 
            text=f"Number of Images: {len(self.image_paths)}", 
            manager = self.manager, 
            container = self.scene2_export_screen, 
            anchors = {"left":"left", "top":"top", "top_target":self.export_video_fps_label}, 
            object_id=ObjectID(class_id="@export_info_label", object_id="#export_video_img_count_label")
        )

        video_length = round(len(self.image_paths) / self.fps, 1) if self.fps != 0 else "--"
        self.export_video_length_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(30, 0, 1050, 50), 
            text=f"Video Length (in seconds): {video_length}", 
            manager = self.manager, 
            container = self.scene2_export_screen, 
            anchors = {"left":"left", "top":"top", "top_target":self.export_video_img_count_label}, 
            object_id=ObjectID(class_id="@export_info_label", object_id="#export_video_length_label")
        )
        
        self.export_video_anti_flickering_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(30, 0, 1050, 50), 
            text=f"Anti-flickering: {self.anti_flickering}", 
            manager = self.manager, 
            container = self.scene2_export_screen, 
            anchors = {"left":"left", "top":"top", "top_target":self.export_video_length_label}, 
            object_id=ObjectID(class_id="@export_info_label", object_id="#export_video_anti_flickering_label")
        )
        next_target = self.export_video_anti_flickering_label
        
        if self.anti_flickering_selector.selected_option[0] == "On":
            self.export_video_anti_flickering_sample_size_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(30, 0, 1050, 50), 
                text=f"Anti-flickering Sample Size: {self.anti_flickering_sample_size}", 
                manager = self.manager, 
                container = self.scene2_export_screen, 
                anchors = {"left":"left", "top":"top", "top_target":self.export_video_anti_flickering_label}, 
                object_id=ObjectID(class_id="@export_info_label", object_id="#export_video_anti_flickering_sample_size_label")
            )
            next_target = self.export_video_anti_flickering_sample_size_label

        
        self.export_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 10, 100, 50), 
            text="Export", 
            manager = self.manager, 
            container = self.scene2_export_screen, 
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
                container = self.scene2_export_screen, 
                anchors = {"left":"left", "top":"top", "top_target":self.export_button}, 
                object_id=ObjectID(class_id="@button", object_id="#export_button")
            )
            self.export_button.disable()
        
    
    def export_image_process(self, image, image_path, display_details):
        topleft = display_details[image_path]["top_left"]
        zoom_level = display_details[image_path]["zoom_level"]
        
        image_height, image_width, channel = image.shape
        

        width_ratio = self.video_resolution[0] / image_width
        height_ratio = self.video_resolution[1] / image_height
        scaling_ratio = max(width_ratio, height_ratio)
        image_base_width = int(self.video_resolution[0] / scaling_ratio)
        image_base_height = int(self.video_resolution[1] / scaling_ratio)
        
        crop_width, crop_height = self.calc_zoom_value(zoom_level, image_base_width), self.calc_zoom_value(zoom_level, image_base_height)
        
        cropped_image = image[topleft[1]:topleft[1]+crop_height, topleft[0]:topleft[0]+crop_width]
        resized_image = cv2.resize(cropped_image, self.video_resolution)
        return resized_image
        
    
    
    def export_video(self, filepath):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or use 'XVID' for .avi
        video = cv2.VideoWriter(filepath, fourcc, self.fps, self.video_resolution)
        display_details = self.panning_to_display_details()
        # print(display_details)
        
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
        self.scene2_back_btn.enable()
        self.scene2_options_btn.enable()
        self.scene2_panning_btn.enable()
        self.scene2_preview_btn.enable()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    def panning_to_display_details(self):
        '''Return display details of each image from panning details'''
        
        display_details = {}
        panning = dict(sorted(self.panning.items(), key=lambda x:x[0]))
        if panning:
            panning_keys = list(panning.keys())
            if not panning:
                panning[self.image_paths[-1]] = {"top_left":(0, 0), "zoom_level":1}
            elif panning_keys[-1] != self.image_paths[-1]:
                panning[self.image_paths[-1]] = panning[list(panning.keys())[-1]]
            panning_keys = list(panning.keys())
            
            next_image_path = panning_keys[0]
            panning_key_index = 0
            next_panning = panning[next_image_path]
            next_image_index = self.image_paths.index(panning_keys[0])
            next_topleft = next_panning["top_left"]
            next_zoom_level = next_panning["zoom_level"]
            if next_image_index == 0:
                curr_topleft = next_topleft
                curr_zoom_level = next_zoom_level
                topleft_x_change = 0
                topleft_y_change = 0
                zoom_level_change = 0
            else:
                curr_topleft = (0, 0)
                curr_zoom_level = 1
                topleft_x_change = (next_topleft[0] - curr_topleft[0]) / next_image_index
                topleft_y_change = (next_topleft[1] - curr_topleft[1]) / next_image_index
                zoom_level_change = (next_zoom_level - curr_zoom_level) / next_image_index
            counter = 0
            curr_image_index = 0

            
            for image_path in self.image_paths:
                display_details[image_path] = {"top_left":(round(curr_topleft[0] + topleft_x_change*counter), round(curr_topleft[1] + topleft_y_change*counter)), 
                                            "zoom_level":(curr_zoom_level + zoom_level_change*counter)}
                
                if image_path == next_image_path and panning_key_index + 1 < len(panning):
                    counter = 0
                    curr_topleft = next_topleft
                    curr_zoom_level = next_zoom_level
                    curr_image_index = next_image_index
                    panning_key_index += 1
                    next_image_path = panning_keys[panning_key_index]
                    next_panning = panning[next_image_path]
                    next_image_index = self.image_paths.index(next_image_path)
                    next_topleft = next_panning["top_left"]
                    next_zoom_level = next_panning["zoom_level"]
                    topleft_x_change = (next_topleft[0] - curr_topleft[0]) / (next_image_index - curr_image_index)
                    topleft_y_change = (next_topleft[1] - curr_topleft[1]) / (next_image_index - curr_image_index)
                    zoom_level_change = (next_zoom_level - curr_zoom_level) / (next_image_index - curr_image_index)
                
                else:
                    counter += 1
        else:
            for image_path in self.image_paths:
                display_details[image_path] = {"top_left":(0, 0), "zoom_level":1}
        
        return display_details
            


    
    
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
                if hasattr(self, "file_choosing_btn") and event.ui_element == self.file_choosing_btn:
                    self.scene1_error_msg.hide()
                    filetypes = [("Image files", " ".join([f"*.{ext}" for ext in VALID_FILE_TYPES]))]
                    file_path = filedialog.askopenfilename(filetypes=filetypes)
                    self.file_path_entry.set_text(file_path)
                
                elif hasattr(self, "confirm_btn") and event.ui_element == self.confirm_btn:
                    if not self.check_file_path_exists():
                        self.scene1_error_msg.show()
                    elif not self.check_valid_file_types():
                        self.scene1_error_msg.show()
                    else:
                        self.scene2()
                
                #Scene 2 button events
                elif hasattr(self, "scene2_back_btn") and event.ui_element == self.scene2_back_btn:
                    self.scene1()
                
                elif hasattr(self, "scene2_options_btn") and event.ui_element == self.scene2_options_btn:
                    self.curr_disabled_btn.enable()
                    self.curr_active_screen.kill()
                    self.curr_disabled_btn = self.scene2_options_btn
                    self.initialize_options_screen()
                    self.curr_active_screen = self.scene2_options_screen
                    self.scene2_options_btn.disable()
                    self.panning_active = False
                
                elif hasattr(self, "scene2_panning_btn") and event.ui_element == self.scene2_panning_btn:
                    self.curr_disabled_btn.enable()
                    self.curr_active_screen.kill()
                    self.curr_disabled_btn = self.scene2_panning_btn
                    self.initialize_panning_screen()
                    self.curr_active_screen = self.scene2_panning_screen
                    self.scene2_panning_btn.disable()
                    self.panning_active = True
                
                elif hasattr(self, "scene2_preview_btn") and event.ui_element == self.scene2_preview_btn:
                    self.curr_disabled_btn.enable()
                    self.curr_active_screen.kill()
                    self.curr_disabled_btn = self.scene2_preview_btn
                    self.initialize_preview_screen()
                    self.curr_active_screen = self.scene2_preview_screen
                    self.scene2_preview_btn.disable()
                    self.panning_active = False
                
                elif hasattr(self, "scene2_export_btn") and event.ui_element == self.scene2_export_btn:
                    self.curr_disabled_btn.enable()
                    self.curr_active_screen.kill()
                    self.curr_disabled_btn = self.scene2_export_btn
                    self.initialize_export_screen()
                    self.curr_active_screen = self.scene2_export_screen
                    self.scene2_export_btn.disable()
                    self.panning_active = False
                
                
                #Option screen button events
                elif hasattr(self, "resolution_preset_first_image_btn") and event.ui_element == self.resolution_preset_first_image_btn:
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
                
                
                elif hasattr(self, "resolution_preset_360p_btn") and event.ui_element == self.resolution_preset_360p_btn:
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
                
                elif hasattr(self, "resolution_preset_SD_btn") and event.ui_element == self.resolution_preset_SD_btn:
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
                
                elif hasattr(self, "resolution_preset_720p_btn") and event.ui_element == self.resolution_preset_720p_btn:
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
                
                elif hasattr(self, "resolution_preset_FHD_btn") and event.ui_element == self.resolution_preset_FHD_btn:
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
                
                elif hasattr(self, "resolution_preset_QHD_btn") and event.ui_element == self.resolution_preset_QHD_btn:
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
                
                elif hasattr(self, "resolution_preset_4K_btn") and event.ui_element == self.resolution_preset_4K_btn:
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
                
                elif hasattr(self, "resolution_preset_8K_btn") and event.ui_element == self.resolution_preset_8K_btn:
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
                
                    
                
                
                #Panning screen button events
                elif hasattr(self, "panning_reset_btn") and event.ui_element == self.panning_reset_btn:
                    self.panning_selected_top_left = (0, 0)
                    self.panning_zoom_level = 1
                    self.zoom_entry.set_text(str(self.panning_zoom_level))
                    self.zoom_slider.set_current_value(self.panning_zoom_level)
                    
                    self.panning_save_msg.hide()
                    self.panning_update_image_display()
                
                
                elif hasattr(self, "panning_save_btn") and event.ui_element == self.panning_save_btn:
                    self.panning[self.panning_image_path] = {"top_left":self.panning_selected_top_left, 
                                                             "zoom_level":self.panning_zoom_level}
                    self.panning_delete_btn.enable()
                    
                    with open(os.path.join(self.application_path, "data/themes/changing_theme.json"), "r") as f:
                        theme = json.load(f)
                    theme[f"#Select_{os.path.basename(self.panning_image_path)}_btn"] = {"colours" : {"normal_bg":"rgb(255, 0, 0)"}}
                    with open(os.path.join(self.application_path, "data/themes/changing_theme.json"), "w") as f:
                        json.dump(theme, f, indent=2)
                    
                    self.panning_save_msg.show()
                
                
                elif hasattr(self, "panning_delete_btn") and event.ui_element == self.panning_delete_btn:
                    answer = messagebox.askyesno("Delete Image Panning Settings", "Are you sure you want to remove the panning settings for this image?")
                    if answer is True:
                        if self.panning_image_path in self.panning:
                            del self.panning[self.panning_image_path]
                        self.panning_delete_btn.disable()
                    
                        with open(os.path.join(self.application_path, "data/themes/changing_theme.json"), "r") as f:
                            theme = json.load(f)
                        theme[f"#Select_{os.path.basename(self.panning_image_path)}_btn"] = {"colours":{"normal_bg":"rgb(76, 80, 82)", "hovered_bg":"rgb(99, 104, 107)", "selected_bg":"rgb(54, 88, 128)", "active_bg":"rgb(54, 88, 128)"}}
                        with open(os.path.join(self.application_path, "data/themes/changing_theme.json"), "w") as f:
                            json.dump(theme, f, indent=2)
                        
                        # with open(f"themes/changing_theme.json", "r") as f:
                        #     theme = json.load(f)
                        # del theme[f"#Select_{os.path.basename(self.panning_image_path)}_btn"]
                        # with open(f"themes/changing_theme.json", "w") as f:
                        #     json.dump(theme, f, indent=2)
                        # self.panning_image_select.rebuild_from_changed_theme_data()
                        
                        self.panning_save_msg.hide()
                    
                
                elif hasattr(self, "panning_exclude_image_btn") and event.ui_element == self.panning_exclude_image_btn:
                    answer = messagebox.askyesno("Exclude Image", "Are you sure you want to remove this image from the video? This action cannot be undone.")
                    if answer is True:
                        if self.panning_image_path in self.panning:
                            del self.panning[self.panning_image_path]
                        self.image_paths.remove(self.panning_image_path)
                        self.curr_active_screen.kill()
                        self.initialize_panning_screen()
                        self.curr_active_screen = self.scene2_panning_screen
                        
                
                #Preview screen button events
                elif hasattr(self, "preview_skip_back_btn") and event.ui_element == self.preview_skip_back_btn:
                    self.preview_playing = False
                    self.preview_play_btn.set_text("Play")
                    if hasattr(self, "preview_showing_image_path"):
                        index = self.image_paths.index(self.preview_showing_image_path)
                    else:
                        index = 0
                    index = max(0, index - self.preview_skip_amount)
                    image_path = self.image_paths[index]
                    self.preview_show_image(image_path)
                
                elif hasattr(self, "preview_back_btn") and event.ui_element == self.preview_back_btn:
                    self.preview_playing = False
                    self.preview_play_btn.set_text("Play")
                    if hasattr(self, "preview_showing_image_path"):
                        index = self.image_paths.index(self.preview_showing_image_path)
                    else:
                        index = 0
                    index = max(0, index - 1)
                    image_path = self.image_paths[index]
                    self.preview_show_image(image_path)
                
                elif hasattr(self, "preview_play_btn") and event.ui_element == self.preview_play_btn:
                    if not self.preview_playing:
                        self.preview_playing = True
                        self.preview_play_btn.set_text("Pause")
                    else:
                        self.preview_playing = False
                        self.preview_play_btn.set_text("Play")
                
                elif hasattr(self, "preview_forward_btn") and event.ui_element == self.preview_forward_btn:
                    self.preview_playing = False
                    self.preview_play_btn.set_text("Play")
                    if hasattr(self, "preview_showing_image_path"):
                        index = self.image_paths.index(self.preview_showing_image_path)
                    else:
                        index = 0
                    index = min(len(self.image_paths)-1, index + 1)
                    image_path = self.image_paths[index]
                    self.preview_show_image(image_path)
                
                elif hasattr(self, "preview_skip_forward_btn") and event.ui_element == self.preview_skip_forward_btn:
                    self.preview_playing = False
                    self.preview_play_btn.set_text("Play")
                    if hasattr(self, "preview_showing_image_path"):
                        index = self.image_paths.index(self.preview_showing_image_path)
                    else:
                        index = 0
                    index = min(len(self.image_paths)-1, index + self.preview_skip_amount)
                    image_path = self.image_paths[index]
                    self.preview_show_image(image_path)
                
                
                
                #Export screen button events
                elif hasattr(self, "export_button") and event.ui_element == self.export_button:
                    filepath = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 Video", "mp4")])
                    if filepath:
                        if hasattr(self, "export_progress_display"):
                            self.export_progress_display.kill()
                        self.export_button.disable()
                        self.exporting = True
                        self.scene2_back_btn.disable()
                        self.scene2_options_btn.disable()
                        self.scene2_panning_btn.disable()
                        self.scene2_preview_btn.disable()
                        
                        self.export_progress = 0
                        self.export_progress_display = pygame_gui.elements.UILabel(
                            relative_rect=pygame.Rect(0, 20, 1050, 30), 
                            text=f"Export Progress: {self.export_progress}/{len(self.image_paths)}", 
                            manager=self.manager, 
                            container=self.scene2_export_screen, 
                            anchors={"centerx":"centerx", "top":"top", "top_target":self.export_button}, 
                            object_id=ObjectID(class_id="@label", object_id="#export_progress_display")
                        )
                        
                        
                        self.export_process = threading.Thread(target=self.export_video, args=(filepath,))
                        self.export_process.start()
                
                
                
                
            
            
            #Text entry changed events
            elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                if hasattr(self, "file_path_entry") and event.ui_element == self.file_path_entry:
                    self.scene1_error_msg.hide()
                
                #Options screen event
                elif hasattr(self, "resolution_width_entry") and event.ui_element == self.resolution_width_entry:
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
                
                
                
                elif hasattr(self, "resolution_height_entry") and event.ui_element == self.resolution_height_entry:
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
                
                
                
                
                
                elif hasattr(self, "fps_entry") and event.ui_element == self.fps_entry:
                    fps = self.fps_entry.get_text()
                    if not fps.isdigit() or int(fps) == 0:
                        self.fps_error_msg.show()
                        self.video_length_label.set_text(f"Video Length: -- seconds")
                    else:
                        self.fps_error_msg.hide()
                        self.fps = int(fps)
                        video_length = round(len(self.image_paths) / int(fps), 1)
                        self.video_length_label.set_text(f"Video Length: {video_length} seconds")
                
                
                #Panning screen event
                elif hasattr(self, "zoom_entry") and event.ui_element == self.zoom_entry:
                    zoom = self.zoom_entry.get_text()
                    if zoom.isdigit():
                        zoom = min(int(zoom), 50)
                        zoom = max(zoom, 1)
                        self.panning_zoom_level = zoom
                        self.zoom_slider.set_current_value(self.panning_zoom_level)
                        self.panning_update_image_display()
                
                
                #Preview screen event
                elif hasattr(self, "preview_video_entry") and event.ui_element == self.preview_video_entry:
                    self.preview_playing = False
                    self.preview_play_btn.set_text("Play")
                    text = self.preview_video_entry.get_text()
                    if text.isdigit():
                        frame = int(text)
                        index = frame - 1
                        index = max(0, min(index, len(self.image_paths)-1))
                        image_path = self.image_paths[index]
                        self.preview_show_image(image_path)
                
            
            #Horizontal slider event
            elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if hasattr(self, "zoom_slider") and event.ui_element == self.zoom_slider:
                    self.panning_zoom_level = int(self.zoom_slider.get_current_value())
                    self.zoom_entry.set_text(str(self.panning_zoom_level))
                    self.panning_update_image_display()
            
            
                if hasattr(self, "preview_video_slider") and event.ui_element == self.preview_video_slider:
                    self.preview_playing = False
                    self.preview_play_btn.set_text("Play")
                    frame = int(self.preview_video_slider.get_current_value())
                    index = frame-1
                    index = max(0, min(index, len(self.image_paths)-1))
                    image_path = self.image_paths[index]
                    self.preview_show_image(image_path)
                
                
            #Selection list events
            elif event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                if hasattr(self, "panning_image_select") and event.ui_element == self.panning_image_select:
                    image_name = event.text
                    image_path = os.path.join(self.folder_path, image_name)
                    self.panning_initialize_image_display(image_path)
                    self.dragging = False
            
            
                elif hasattr(self, "preview_image_select") and event.ui_element == self.preview_image_select:
                    image_name = event.text
                    image_path = os.path.join(self.folder_path, image_name)
                    self.preview_show_image(image_path)
                    self.preview_playing = False
                    self.preview_play_btn.set_text("Play")
                    
                    
                    
            #Drop down menu events
            elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if hasattr(self, "resolution_aspect_ratio_menu") and event.ui_element == self.resolution_aspect_ratio_menu:
                    self.aspect_ratio:str = event.text
                    
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

                
                elif hasattr(self, "anti_flickering_selector") and event.ui_element == self.anti_flickering_selector:
                    self.anti_flickering = self.anti_flickering_selector.selected_option[0]
                
                elif hasattr(self, "anti_flickering_sample_size_selector") and event.ui_element == self.anti_flickering_sample_size_selector:
                    self.anti_flickering_sample_size = self.anti_flickering_sample_size_selector.selected_option[0]
                    
            
            
            #Mouse click events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.panning_active and event.button == pygame.BUTTON_LEFT:
                    pos = event.pos
                    # print(pos)
                    rect = self.panning_image_display.get_abs_rect()
                    # print(rect.topleft, rect.topright, rect.bottomleft, rect.bottomright, rect.width, rect.height)
                    if rect.collidepoint(pos):
                        self.dragging = True
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == pygame.BUTTON_LEFT:
                    self.dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.panning_active and self.dragging:
                    move_x, move_y = event.rel
                    
                    
                    selected_x, selected_y = self.panning_selected_top_left
                    selected_w, selected_h = self.panning_selected_width, self.panning_selected_height
                    
                    image_w, image_h = self.panning_image.get_width(), self.panning_image.get_height()
                    
                    display_w, display_h = self.panning_scaled_width, self.panning_scaled_height
                    
                    move_x_ratio, move_y_ratio = selected_w / display_w, selected_h / display_h
                    
                    move_x = int(move_x * move_x_ratio)
                    move_y = int(move_y * move_y_ratio)
                    
                    selected_x -= move_x
                    selected_y -= move_y
                    selected_x = max(0, min((image_w - selected_w), selected_x))
                    selected_y = max(0, min((image_h - selected_h), selected_y))
                    # print(selected_x, selected_y)
                    
                    self.panning_selected_top_left = (selected_x, selected_y)
                    self.panning_update_image_display()
            
                    
                    
                    
                    
                    
                    
            
            
            
            self.manager.process_events(event)
            
    
    def update(self):
        if self.preview_playing:
            if hasattr(self, "preview_showing_image_path"):
                curr_index = self.image_paths.index(self.preview_showing_image_path)
                if curr_index == len(self.image_paths)-1:
                    self.preview_playing = False
                    self.preview_play_btn.set_text("Play")
                else:
                    curr_index += 1
                    self.preview_show_image(self.image_paths[curr_index])
                
        
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

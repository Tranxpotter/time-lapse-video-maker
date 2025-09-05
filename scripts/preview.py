from __future__ import annotations
import pygame
import pygame_gui
from pygame_gui.core import ObjectID, UIElement
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json

from .scene import Scene
from .utils import scroll_to_index



from typing import TYPE_CHECKING, Dict
if TYPE_CHECKING:
    from ..app import App
    from .scene2 import Scene2


class PreviewScreen(pygame_gui.elements.UIPanel):
    def __init__(self, app:App, manager:pygame_gui.UIManager, scene2:Scene2, anchor_target):
        self.app = app
        self.manager = manager
        self.scene2 = scene2
        super().__init__(relative_rect=pygame.Rect(0, 0, 1080, 650),
                         manager=self.manager, 
                         anchors={"left":"left", "right":"right", "top":"top", "top_target":anchor_target})
        self.preview_playing = False

        self.preview_image_select = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(-370, 0, 370, 650),
            item_list=[(name, f"#Preview_{name}_btn") for name in self.get_image_names()],
            manager=self.manager, 
            container=self, 
            anchors={"right":"right", "top":"top"}, 
            object_id=ObjectID(class_id="@selection_list", object_id="#image_select"), 
            default_selection=(self.get_image_names()[self.curr_preview_index], f"#Preview_{self.get_image_names()[self.curr_preview_index]}_btn")
        )
        scroll_to_index(self.preview_image_select, self.curr_preview_index)
        
        
        self.preview_image_display_size = self.preview_image_display_width, self.preview_image_display_height = (700, 500)
        
        self.preview_image_display_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (self.preview_image_display_width+3, self.preview_image_display_height+3)),
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top"}, 
            object_id=ObjectID(class_id="@panel", object_id="#image_display")
        )
        
        
        
        self.preview_video_first_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            text='1', 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.preview_image_display_panel},
            object_id=ObjectID(class_id="@label", object_id="#panning_zoom_label")
        )
        self.preview_video_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(0, 10, 400, 30), 
            start_value=1, 
            value_range=(1, len(self.image_paths)), 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.preview_image_display_panel, "left_target":self.preview_video_first_label}, 
            object_id=ObjectID(class_id="@slider", object_id="#panning_zoom_slider")
        )
        self.preview_video_last_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            text=str(len(self.image_paths)), 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.preview_image_display_panel, "left_target":self.preview_video_slider},
            object_id=ObjectID(class_id="@label", object_id="#panning_zoom_label")
        )
        
        self.preview_video_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.preview_image_display_panel, "left_target":self.preview_video_last_label}, 
            object_id=ObjectID(class_id="@option_entry", object_id="#panning_zoom_entry")
        )
        
        self.preview_skip_amount = len(self.image_paths) // 10
        
        self.preview_skip_back_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50), 
            text="<<", 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.preview_video_entry}, 
            object_id=ObjectID(class_id="@video_control_btn", object_id="#preview_skip_back_btn")
        )
        
        self.preview_back_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50), 
            text="<", 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.preview_video_entry, "left_target":self.preview_skip_back_btn}, 
            object_id=ObjectID(class_id="@video_control_btn", object_id="#preview_back_btn")
        )
        
        self.preview_play_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, 100, 50), 
            text="Play", 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.preview_video_entry, "left_target":self.preview_back_btn}, 
            object_id=ObjectID(class_id="@video_control_btn", object_id="#preview_play_btn")
        )
        
        self.preview_forward_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50), 
            text=">", 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.preview_video_entry, "left_target":self.preview_play_btn}, 
            object_id=ObjectID(class_id="@video_control_btn", object_id="#preview_forward_btn")
        )
        
        self.preview_skip_forward_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, 50, 50), 
            text=">>", 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.preview_video_entry, "left_target":self.preview_forward_btn}, 
            object_id=ObjectID(class_id="@video_control_btn", object_id="#preview_skip_forward_btn")
        )
        
        # todo: Add fast play? like show only 1 in 10 photos type speed up
        
        self.preview_image_name_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 300, 50), 
            text="", 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.preview_video_entry, "left_target":self.preview_skip_forward_btn}, 
            object_id=ObjectID(class_id="@label", object_id="#preview_image_name_label")
        )
        
        
        self.preview_display_details = self.scene2.panning_to_display_details()
        self.preview_show_image(self.image_paths[self.curr_preview_index])
    
    def get_image_names(self):
        return self.scene2.get_image_names()
    
    @property
    def curr_preview_index(self):
        return self.scene2.curr_preview_index
    
    @curr_preview_index.setter
    def curr_preview_index(self, val:int):
        self.scene2.curr_preview_index = val
    
    @property
    def image_paths(self):
        return self.scene2.image_paths
    
    @property
    def video_resolution(self):
        return self.scene2.video_resolution
    
    def preview_show_image(self, image_path):
        with open(os.path.join(self.app.application_path, "data/themes/changing_theme.json"), "r") as f:
            theme = json.load(f)
        if hasattr(self, "preview_showing_image_path"):
            if f"#Preview_{os.path.basename(self.preview_showing_image_path)}_btn" in theme:
                theme[f"#Preview_{os.path.basename(self.preview_showing_image_path)}_btn"] = {"colours":{"normal_bg":"rgb(76, 80, 82)", "hovered_bg":"rgb(99, 104, 107)", "selected_bg":"rgb(54, 88, 128)", "active_bg":"rgb(54, 88, 128)"}}
        theme[f"#Preview_{os.path.basename(image_path)}_btn"] = {"colours":{"normal_bg":"rgb(255, 0, 0)", "hovered_bg":"rgb(255, 0, 0)", "selected_bg":"rgb(255, 0, 0)", "active_bg":"rgb(255, 0, 0)"}}
        with open(os.path.join(self.app.application_path, "data/themes/changing_theme.json"), "w") as f:
            json.dump(theme, f, indent=2)
        
        self.preview_image_select.rebuild_from_changed_theme_data()
        
        
        self.preview_showing_image_path = image_path
        if hasattr(self, "preview_image_display"):
            self.preview_image_display.kill()
        preview_image = self.scene2.load_image(image_path)
        width_ratio = self.video_resolution[0] / preview_image.get_width()
        height_ratio = self.video_resolution[1] / preview_image.get_height()
        scaling_ratio = max(width_ratio, height_ratio) #Set min for fit, max for fill
        image_base_width = int(self.video_resolution[0] / scaling_ratio)
        image_base_height = int(self.video_resolution[1] / scaling_ratio)
        
        display_details = self.preview_display_details[image_path]
        # topleft = display_details["top_left"]
        relative_center = display_details["relative_center"]
        
        
        zoom_level = display_details["zoom_level"]
        crop_width, crop_height = self.scene2.calc_zoom_value(zoom_level, image_base_width), self.scene2.calc_zoom_value(zoom_level, image_base_height)
        
        topleft = self.scene2.get_topleft_from_relc(relative_center, preview_image.get_width(), preview_image.get_height(), image_base_width, image_base_height, crop_width, crop_height)
        
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
    
    
    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.preview_skip_back_btn:
                self.preview_playing = False
                self.preview_play_btn.set_text("Play")
                if hasattr(self, "preview_showing_image_path"):
                    index = self.image_paths.index(self.preview_showing_image_path)
                else:
                    index = 0
                index = max(0, index - self.preview_skip_amount)
                self.curr_preview_index = index
                image_path = self.image_paths[index]
                self.preview_show_image(image_path)
            
            elif event.ui_element == self.preview_back_btn:
                self.preview_playing = False
                self.preview_play_btn.set_text("Play")
                if hasattr(self, "preview_showing_image_path"):
                    index = self.image_paths.index(self.preview_showing_image_path)
                else:
                    index = 0
                index = max(0, index - 1)
                self.curr_preview_index = index
                image_path = self.image_paths[index]
                self.preview_show_image(image_path)
            
            elif event.ui_element == self.preview_play_btn:
                if not self.preview_playing:
                    self.preview_playing = True
                    self.preview_play_btn.set_text("Pause")
                else:
                    self.preview_playing = False
                    self.preview_play_btn.set_text("Play")
            
            elif event.ui_element == self.preview_forward_btn:
                self.preview_playing = False
                self.preview_play_btn.set_text("Play")
                if hasattr(self, "preview_showing_image_path"):
                    index = self.image_paths.index(self.preview_showing_image_path)
                else:
                    index = 0
                index = min(len(self.image_paths)-1, index + 1)
                self.curr_preview_index = index
                image_path = self.image_paths[index]
                self.preview_show_image(image_path)
            
            elif event.ui_element == self.preview_skip_forward_btn:
                self.preview_playing = False
                self.preview_play_btn.set_text("Play")
                if hasattr(self, "preview_showing_image_path"):
                    index = self.image_paths.index(self.preview_showing_image_path)
                else:
                    index = 0
                index = min(len(self.image_paths)-1, index + self.preview_skip_amount)
                self.curr_preview_index = index
                image_path = self.image_paths[index]
                self.preview_show_image(image_path)
        
        
        
        
        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            if event.ui_element == self.preview_video_entry:
                self.preview_playing = False
                self.preview_play_btn.set_text("Play")
                text = self.preview_video_entry.get_text()
                if text.isdigit():
                    frame = int(text)
                    index = frame - 1
                    index = max(0, min(index, len(self.image_paths)-1))
                    self.curr_preview_index = index
                    image_path = self.image_paths[index]
                    self.preview_show_image(image_path)
        
        
        
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.preview_video_slider:
                self.preview_playing = False
                self.preview_play_btn.set_text("Play")
                frame = int(self.preview_video_slider.get_current_value())
                index = frame-1
                index = max(0, min(index, len(self.image_paths)-1))
                self.curr_preview_index = index
                image_path = self.image_paths[index]
                self.preview_show_image(image_path)
        
        
        
        
        elif event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if event.ui_element == self.preview_image_select:
                image_name = event.text
                image_path = self.scene2.folder_path + "/" + image_name
                image_index = self.image_paths.index(image_path)
                self.curr_preview_index = image_index
                self.preview_show_image(image_path)
                self.preview_playing = False
                self.preview_play_btn.set_text("Play")
    
    
    
    
    
    def update(self, time_delta):
        super().update(time_delta)
        if self.preview_playing:
            curr_index = self.image_paths.index(self.preview_showing_image_path)
            if curr_index == len(self.image_paths)-1:
                self.preview_playing = False
                self.preview_play_btn.set_text("Play")
            else:
                curr_index += 1
                self.preview_show_image(self.image_paths[curr_index])
                
        
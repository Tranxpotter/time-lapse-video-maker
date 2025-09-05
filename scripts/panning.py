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


class PanningScreen(pygame_gui.elements.UIPanel):
    def __init__(self, app:App, manager:pygame_gui.UIManager, scene2:Scene2, anchor_target):
        self.app = app
        self.manager = manager
        self.scene2 = scene2
        super().__init__(relative_rect=pygame.Rect(0, 0, 1080, 650),
                         manager=self.manager, 
                         anchors={"left":"left", "right":"right", "top":"top", "top_target":anchor_target})
    

        self.dragging = False
        
        
        self.panning_image_select = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(-370, 0, 370, 650),
            item_list=[(name, f"#Select_{name}_btn") for name in self.get_image_names()],
            manager=self.manager, 
            container=self, 
            anchors={"right":"right", "top":"top"}, 
            object_id=ObjectID(class_id="@selection_list", object_id="#image_select"), 
            default_selection=(self.get_image_names()[self.curr_panning_index], f"#Select_{self.get_image_names()[self.curr_panning_index]}_btn")
        )
        scroll_to_index(self.panning_image_select, self.curr_panning_index)
        
        
        self.panning_image_display_size = self.panning_image_display_width, self.panning_image_display_height = (700, 500)
        
        self.panning_image_display_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (self.panning_image_display_width+3, self.panning_image_display_height+3)),
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top"}, 
            object_id=ObjectID(class_id="@panel", object_id="#image_display")
        )

        
        
        #Panning screen option buttons
        self.zoom_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            text='Zoom:', 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.panning_image_display_panel},
            object_id=ObjectID(class_id="@label", object_id="#panning_zoom_label")
        )
        self.zoom_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(0, 10, 400, 30), 
            start_value=1, 
            value_range=(1, 50), 
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.panning_image_display_panel, "left_target":self.zoom_label}, 
            object_id=ObjectID(class_id="@slider", object_id="#panning_zoom_slider")
        )
        
        self.zoom_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.panning_image_display_panel, "left_target":self.zoom_slider}, 
            object_id=ObjectID(class_id="@option_entry", object_id="#panning_zoom_entry")
        )
        
        
        self.panning_save_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 20, 100, 50),
            text='Save',
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.zoom_slider}, 
            object_id=ObjectID(class_id="@button", object_id="#panning_save_btn")
        )
        
        self.panning_delete_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 20, 100, 50),
            text='Delete',
            manager=self.manager, 
            container=self, 
            anchors={"left":"left", "top":"top", "left_target":self.panning_save_btn, "top_target":self.zoom_slider}, 
            object_id=ObjectID(class_id="@button", object_id="#panning_delete_btn")
        )
        
        
        self.panning_exclude_image_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 20, 200, 50),
            text='Exclude Image',
            manager=self.manager, 
            container=self, 
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
            container=self, 
            anchors={"left":"left", "top":"top", "top_target":self.panning_exclude_image_btn},
            object_id=ObjectID(class_id="@label", object_id="#panning_zoom_label")
        )
        self.panning_save_msg.hide()
        
        self.panning_initialize_image_display(self.image_paths[self.curr_panning_index])
    
    
    @property
    def curr_panning_index(self):
        return self.scene2.curr_panning_index
    
    @curr_panning_index.setter
    def curr_panning_index(self, val:int):
        self.scene2.curr_panning_index = val
    
    @property
    def panning(self):
        return self.scene2.panning
    
    @property
    def image_paths(self):
        return self.scene2.image_paths
    
    def get_image_names(self):
        return self.scene2.get_image_names()
    
    @property
    def video_resolution(self):
        return self.scene2.video_resolution
    
    @property
    def image_fitting_rule(self):
        return self.scene2.image_fitting_rule
    
    
    def save_panning(self):
        center = (self.panning_selected_top_left[0] + self.panning_selected_width//2, self.panning_selected_top_left[1] + self.panning_selected_height//2)
        relative_center = (center[0] / self.base_panning_selected_width, center[1] / self.base_panning_selected_height)
        is_update = self.panning_image_path in self.panning
        self.panning[self.panning_image_path] = {
                                                    # "top_left":self.panning_selected_top_left, 
                                                #  "center":center, 
                                                    "relative_center":self.panning_selected_relc,
                                                    "zoom_level":self.panning_zoom_level}
        self.panning_delete_btn.enable()
        
        if not is_update:
            with open(os.path.join(self.app.application_path, "data/themes/changing_theme.json"), "r") as f:
                theme = json.load(f)
            theme[f"#Select_{os.path.basename(self.panning_image_path)}_btn"] = {"colours" : {"normal_bg":"rgb(255, 0, 0)"}}
            with open(os.path.join(self.app.application_path, "data/themes/changing_theme.json"), "w") as f:
                json.dump(theme, f, indent=2)
        
        self.panning_save_msg.show()
    
    @property
    def panning_selected_top_left(self):
        crop_width = self.scene2.calc_zoom_value(self.panning_zoom_level, self.base_panning_selected_width)
        crop_height = self.scene2.calc_zoom_value(self.panning_zoom_level, self.base_panning_selected_height)
        return self.scene2.get_topleft_from_relc(self.panning_selected_relc, self.panning_image.get_width(), self.panning_image.get_height(), crop_width, crop_height)
    
    @panning_selected_top_left.setter
    def panning_selected_top_left(self, val:tuple[int, int]):
        crop_width = self.scene2.calc_zoom_value(self.panning_zoom_level, self.base_panning_selected_width)
        crop_height = self.scene2.calc_zoom_value(self.panning_zoom_level, self.base_panning_selected_height)
        self.panning_selected_relc = self.scene2.get_relc_from_topleft(val, self.panning_image.get_width(), self.panning_image.get_height(), crop_width, crop_height)
    
    def panning_initialize_image_display(self, image_path):
        # Load image
        self.panning_image_path = image_path
        self.panning_image = self.scene2.load_image(image_path)
        image_width, image_height = self.panning_image.get_width(), self.panning_image.get_height()
        
        width_ratio = self.video_resolution[0] / self.panning_image.get_width()
        height_ratio = self.video_resolution[1] / self.panning_image.get_height()
        if self.image_fitting_rule == "Fit":
            scaling_ratio = min(width_ratio, height_ratio)
        else:
            scaling_ratio = max(width_ratio, height_ratio)
        self.base_panning_selected_width = round(self.video_resolution[0] / scaling_ratio)
        self.base_panning_selected_height = round(self.video_resolution[1] / scaling_ratio)
        
        # Fill in the background for "fit" image fitting rule
        if self.base_panning_selected_width > image_width or self.base_panning_selected_height > image_height:
            background = pygame.Surface((self.base_panning_selected_width, self.base_panning_selected_height))
            background.blit(self.panning_image, (round((self.base_panning_selected_width-image_width)/2), round((self.base_panning_selected_height-image_height)/2)))
            self.panning_image = background

        # 0. Get the panning information for the image
        if image_path not in self.panning:
            self.panning_selected_relc = (0.5, 0.5)
            # self.panning_selected_top_left = (0, 0)
            self.change_curr_zoom(1)
            self.panning_delete_btn.disable()
        else:
            self.panning_selected_relc = self.panning[image_path]["relative_center"]
            # self.panning_selected_top_left = self.panning[image_path]["top_left"]
            self.change_curr_zoom(self.panning[image_path]["zoom_level"])
            self.panning_delete_btn.enable()
        
        
        
        self.panning_update_image_display()
    
    
    def panning_mouse_move_to_image_move(self, move_x, move_y):
        selected_w, selected_h = self.panning_selected_width, self.panning_selected_height
        
        display_w, display_h = self.panning_scaled_width, self.panning_scaled_height
        
        move_x_ratio, move_y_ratio = selected_w / display_w, selected_h / display_h
        
        move_x = int(move_x * move_x_ratio)
        move_y = int(move_y * move_y_ratio)
        
        return (move_x, move_y)
    
    
    
    def move_panning_selected_topleft(self, move_x, move_y):
        '''Moves panning_selected_top_left by move_x and move_y amount, returns if the topleft coordinate changed
        
        Note that this does not update display image and save panning information'''
        selected_x, selected_y = self.panning_selected_top_left
        selected_w, selected_h = self.panning_selected_width, self.panning_selected_height
        
        image_w, image_h = self.panning_image.get_width(), self.panning_image.get_height()
        
        
        selected_x -= move_x
        selected_y -= move_y
        selected_x = max(0, min((image_w - selected_w), selected_x))
        selected_y = max(0, min((image_h - selected_h), selected_y))
        
        moved = not self.panning_selected_top_left == (selected_x, selected_y)
        
        self.panning_selected_top_left = (selected_x, selected_y)
        
        return moved
    
    
    def change_curr_zoom(self, zoom_val:int, update_slider:bool = True, relc_x:float|None = None, relc_y:float|None = None):
        '''Only changes the values and labels related to zoom and handle out of range, returns if zoom value changed. 
        
        Also changes panning_selected_topleft if relc_x or relc_y is given to zoom in into a center point \n
        (relc_x relc_y should be the relative center point withreference to the display panel instead of the image)
        
        Does not update image display and does not save panning information'''
        zoom_val = min(50, zoom_val)
        zoom_val = max(1, zoom_val)
        if hasattr(self, "panning_zoom_level"):
            changed = not self.panning_zoom_level == zoom_val
        else:
            changed = True
            
        # Change topleft to zoom in at a point
        if relc_x:
            old_zoom = self.panning_zoom_level
            new_zoom = zoom_val
            
            old_width = self.scene2.calc_zoom_value(old_zoom, self.base_panning_selected_width)
            new_width = self.scene2.calc_zoom_value(new_zoom, self.base_panning_selected_width)
            move_x = -(old_width - new_width) * relc_x
        else:
            move_x = 0
        
        if relc_y:
            old_zoom = self.panning_zoom_level
            new_zoom = zoom_val
            
            old_height = self.scene2.calc_zoom_value(old_zoom, self.base_panning_selected_height)
            new_height = self.scene2.calc_zoom_value(new_zoom, self.base_panning_selected_height)
            move_y = -(old_height - new_height) * relc_y
        else:
            move_y = 0
            
        
        self.panning_zoom_level = zoom_val
        if update_slider:
            self.zoom_slider.set_current_value(zoom_val)
        
        self.zoom_entry.set_text(str(self.panning_zoom_level))
        
        if move_x or move_y:
            self.panning_selected_width, self.panning_selected_height = self.scene2.calc_zoom_value(self.panning_zoom_level, self.base_panning_selected_width), self.scene2.calc_zoom_value(self.panning_zoom_level, self.base_panning_selected_height)
            self.move_panning_selected_topleft(move_x, move_y)
        
        return changed
    
    
    def panning_update_image_display(self):
        self.panning_save_msg.hide()
        #Reset the panning image display
        if hasattr(self, "panning_image_display"):
            self.panning_image_display.kill()
        
        # 2. Initialize image
        panning_curr_image = self.panning_image
        
        # 3. Calculate width and height from zoom level
        self.panning_selected_width, self.panning_selected_height = self.scene2.calc_zoom_value(self.panning_zoom_level, self.base_panning_selected_width), self.scene2.calc_zoom_value(self.panning_zoom_level, self.base_panning_selected_height)
        
        # 4. Move selecteed topleft if selected area is out of range
        self.panning_selected_top_left = (min(self.panning_image.get_width() - self.panning_selected_width, self.panning_selected_top_left[0]), min(self.panning_image.get_height() - self.panning_selected_height, self.panning_selected_top_left[1]))
        
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
    
    
    
    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            #Panning screen button events
            if event.ui_element == self.panning_save_btn:
                self.save_panning()
            
            
            elif event.ui_element == self.panning_delete_btn:
                answer = messagebox.askyesno("Delete Image Panning Settings", "Are you sure you want to remove the panning settings for this image?")
                if answer is True:
                    if self.panning_image_path in self.panning:
                        del self.panning[self.panning_image_path]
                    self.panning_delete_btn.disable()
                
                    with open(os.path.join(self.app.application_path, "data/themes/changing_theme.json"), "r") as f:
                        theme = json.load(f)
                    theme[f"#Select_{os.path.basename(self.panning_image_path)}_btn"] = {"colours":{"normal_bg":"rgb(76, 80, 82)", "hovered_bg":"rgb(99, 104, 107)", "selected_bg":"rgb(54, 88, 128)", "active_bg":"rgb(54, 88, 128)"}}
                    with open(os.path.join(self.app.application_path, "data/themes/changing_theme.json"), "w") as f:
                        json.dump(theme, f, indent=2)
                    
                    #Reset panning
                    # self.panning_selected_top_left = (0, 0)
                    self.panning_selected_relc = (0.5, 0.5)
                    self.panning_zoom_level = 1
                    self.zoom_entry.set_text(str(self.panning_zoom_level))
                    self.zoom_slider.set_current_value(self.panning_zoom_level)
                    
                    self.panning_save_msg.hide()
                    self.panning_update_image_display()
                    
                
        
            elif event.ui_element == self.panning_exclude_image_btn:
                answer = messagebox.askyesno("Exclude Image", "Are you sure you want to remove this image from the video? This action cannot be undone.")
                if answer is True:
                    if self.panning_image_path in self.panning:
                        del self.panning[self.panning_image_path]
                    self.image_paths.remove(self.panning_image_path)
                    self.curr_panning_index -= 1
                    self.scene2.to_page("Panning")
        
        
        
        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            #Panning screen event
            if event.ui_element == self.zoom_entry:
                zoom = self.zoom_entry.get_text()
                if zoom.isdigit():
                    changed = self.change_curr_zoom(int(zoom), relc_x=0.5, relc_y=0.5)
                    if changed:
                        self.panning_update_image_display()
                        self.save_panning()
        
        
        
        
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.zoom_slider:
                changed = self.change_curr_zoom(int(self.zoom_slider.get_current_value()), update_slider=False, relc_x=0.5, relc_y=0.5)
                if changed:
                    self.panning_update_image_display()
                    self.save_panning()
        
        
        #Selection list events
        elif event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if event.ui_element == self.panning_image_select:
                image_name = event.text
                image_path = self.scene2.folder_path + "/" + image_name
                image_index = self.image_paths.index(image_path)
                self.curr_panning_index = image_index
                self.panning_initialize_image_display(image_path)
                self.dragging = False
        
        
        
        
        #Mouse click events
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                pos = event.pos
                rect = self.panning_image_display.get_abs_rect()
                if rect.collidepoint(pos):
                    self.dragging = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == pygame.BUTTON_LEFT:
                self.dragging = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                move_x, move_y = event.rel
                move_x, move_y = self.panning_mouse_move_to_image_move(move_x, move_y)
                moved = self.move_panning_selected_topleft(move_x, move_y)
                if moved:
                    self.panning_update_image_display()
                    self.save_panning()
        
        elif event.type == pygame.MOUSEWHEEL:
            pos = pygame.mouse.get_pos()
            mouse_x, mouse_y = pos
            rect = self.panning_image_display.get_abs_rect()
            if rect.collidepoint(pos):
                #Check if zoom in/out action
                if event.y != 0 and event.y == event.precise_y:
                    curr_zoom = self.panning_zoom_level
                    new_zoom = curr_zoom + event.y
                    
                    topleft_x, topleft_y = rect.topleft
                    display_width, display_height = rect.width, rect.height
                    relc_x, relc_y = (mouse_x - topleft_x) / display_width, (mouse_y - topleft_y) / display_height
                    
                    changed = self.change_curr_zoom(new_zoom, relc_x=relc_x, relc_y=relc_y)
                    if changed:
                        self.panning_update_image_display()
                        self.save_panning()
                        
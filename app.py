import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import threading
import sys
import math

import pygame
pygame.init()
import pygame_gui
from pygame_gui.core import ObjectID

from scripts.file_choosing import FileChoosing
from scripts.scene2 import Scene2





WINDOW_SIZE = (1080, 720)




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
        
        self.curr_scene = 1
        
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

        
        
        
        self.curr_scene_instance = FileChoosing(self, self.manager)
    
    
    def to_scene1(self):
        self.curr_scene = 1
        self.curr_scene_instance = FileChoosing(self, self.manager)
    
    def to_scene2(self, file_paths:list[str]):
        self.curr_scene = 2
        self.curr_scene_instance = Scene2(self, self.manager, file_paths)
    
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.curr_scene == 2:
                    answer = messagebox.askyesno("Warning", "Are you sure you want to quit? All changes will be lost.")
                    if answer is True:
                        self.running = False
                else:
                    self.running = False
                    
            
            
            self.curr_scene_instance.handle_event(event)
            self.manager.process_events(event)
            
    
    def update(self):
        self.curr_scene_instance.update()
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

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
        
        
        
        #Pygame basic setups
        self.window = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Time Lapse Video Maker")
        
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.running = True
        
        
        
        #Pygame GUI basic setups
        self.manager = pygame_gui.UIManager(WINDOW_SIZE, theme_path=os.path.join(self.application_path, "data/themes/fonts.json"))
        self.manager.get_theme().load_theme(os.path.join(self.application_path, "data/themes/theme.json"))


        
        
    
    
    def handle_events(self):
        for event in pygame.event.get():
            ...
            
    
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

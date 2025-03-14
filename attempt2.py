import pygame
import pygame_gui
from pygame.locals import RESIZABLE, FULLSCREEN
from tkinter import Tk, filedialog

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600), RESIZABLE | FULLSCREEN)
        pygame.display.set_caption('Time Lapse Video Maker')
        self.manager = pygame_gui.UIManager((800, 600))
        self.clock = pygame.time.Clock()
        self.running = True
        self.source_path = None

        self.choose_file_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((350, 275), (100, 50)),
            text='Choose File',
            manager=self.manager
        )

    def run(self):
        while self.running:
            time_delta = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        if event.ui_element == self.choose_file_button:
                            self.open_file_dialog()

                self.manager.process_events(event)

            self.manager.update(time_delta)
            self.screen.fill((0, 0, 0))
            self.manager.draw_ui(self.screen)
            pygame.display.update()

    def open_file_dialog(self):
        root = Tk()
        root.withdraw()
        self.source_path = filedialog.askopenfilename()
        root.destroy()

if __name__ == '__main__':
    app = App()
    app.run()
    pygame.quit()
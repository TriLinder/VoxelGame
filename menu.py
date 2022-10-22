from turtle import width
import pygame as pg
import pygame_menu as pgm
import math

class Menu :
    def __init__(self, ui) -> None :
        self.ui = ui
        
        self.visible = True
        self.showInMenu = True
        self.isDebugElement = False
        
        self.pgmTheme = pgm.themes.THEME_DARK

        self.screens = {"main": MainMenu(self, ui), "settings": SettingsMenu(self, ui)}
        self.currentScreen = "main"

        self.resize()

    def tick(self) :
        self.visible = not self.ui.app.inGame

        if self.visible :
            self.ui.redrawNextFrame = True
    
    def resize(self) :
        for screen in self.screens.values() :
            screen.resize()
    
    def render(self) :
        overlayColor = (0, 0, 0, 255) #RGBA
        pg.draw.rect(self.ui.surface, overlayColor, [0, 0, self.ui.res[0], self.ui.res[1]]) #Overlay

        self.screens[self.currentScreen].tick()
        self.screens[self.currentScreen].draw()

# ------------------ #

class MainMenu :
    def __init__(self, menu, ui) -> None :
        self.ui = ui
        self.menu = menu

        self.pgm = pgm.Menu(width=self.ui.res[0], height=self.ui.res[1], theme=menu.pgmTheme, title='Main menu')
        
        self.pgm.add.button("PLAY", self.playButton)
        self.pgm.add.button("SETTINGS", self.settingsButton)
        self.pgm.add.button("QUIT", self.quitButton)

    def playButton(self) :
        self.ui.app.gamePaused = False
        self.ui.app.inGame = True
        self.ui.showDebugElements = False
    
    def settingsButton(self) :
        self.menu.currentScreen = "settings"
    
    def quitButton(self) :
        self.ui.app.quit()
    
    def resize(self) :
        width, height = self.ui.surface.get_size()
        self.pgm.resize(width, height, screen_dimension=(width, height))

    def tick(self) :
        self.pgm.update(self.ui.app.pgEvents)
    
    def draw(self) :
        self.pgm.draw(self.ui.surface)
    
class SettingsMenu :
    def __init__(self, menu, ui) -> None :
        self.ui = ui
        self.menu = menu
        self.config = self.ui.app.config

        self.pgm = pgm.Menu(width=self.ui.res[0], height=self.ui.res[1], theme=menu.pgmTheme, title='Settings')
        
        self.pgm.add.range_slider("Render distance:", default=self.config.renderDistance, range_values=(1, 8), increment=1, onchange=self.renderDistanceSlider, value_format=lambda x: str(round(x)))
        self.pgm.add.range_slider("FPS Limit:", default=self.config.fpsLimit, range_values=(15, 120), increment=1, onchange=self.fpsLimitSlider, value_format=lambda x: str(round(x)))
        self.pgm.add.button("GO BACK", self.goBackButton)

    def renderDistanceSlider(self, value) :
        value = round(value)
        self.config.renderDistance = value
    
    def fpsLimitSlider(self, value) :
        value = round(value)
        self.config.fpsLimit = value

    def goBackButton(self) :
        self.menu.currentScreen = "main"
        self.config.writeToFile()
    
    def resize(self) :
        width, height = self.ui.surface.get_size()
        self.pgm.resize(width, height, screen_dimension=(width, height))

    def tick(self) :
        self.pgm.update(self.ui.app.pgEvents)
    
    def draw(self) :
        self.pgm.draw(self.ui.surface)
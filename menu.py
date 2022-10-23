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

        self.screens = {"main": MainMenu(self, ui), "settings": SettingsMenu(self, ui), "keybinds": Keybinds(self, ui)}
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
        self.pgm.add.range_slider("Mouse sensitivity:", default=self.config.mouseSensitivity, range_values=(1, 100), increment=1, onchange=self.mouseSensitivitySlider, value_format=lambda x: str(round(x)))
        self.pgm.add.range_slider("FPS Limit:", default=self.config.fpsLimit, range_values=(15, 120), increment=1, onchange=self.fpsLimitSlider, value_format=lambda x: str(round(x)))
        self.pgm.add.range_slider("FOV:", default=self.config.fov, range_values=(15, 120), increment=1, onchange=self.fovSlider, value_format=lambda x: str(round(x)))
        self.pgm.add.button("KEYBINDS", self.keybindsButton)
        self.pgm.add.button("GO BACK", self.goBackButton)

    def renderDistanceSlider(self, value) :
        value = round(value)
        self.config.renderDistance = value
    
    def fpsLimitSlider(self, value) :
        value = round(value)
        self.config.fpsLimit = value
    
    def mouseSensitivitySlider(self, value) :
        value = round(value)
        self.config.mouseSensitivity = value
    
    def fovSlider(self, value) :
        value = round(value)
        self.config.fov = value

    def keybindsButton(self) :
        self.menu.currentScreen = "keybinds"

    def goBackButton(self) :
        self.menu.currentScreen = "main"
        self.ui.app.camera.updateProjM() #Update camera FOV
        self.config.writeToFile()
    
    def resize(self) :
        width, height = self.ui.surface.get_size()
        self.pgm.resize(width, height, screen_dimension=(width, height))

    def tick(self) :
        self.pgm.update(self.ui.app.pgEvents)
    
    def draw(self) :
        self.pgm.draw(self.ui.surface)

class Keybinds :
    def __init__(self, menu, ui) -> None :
        self.ui = ui
        self.menu = menu
        self.config = self.ui.app.config

        self.keybinds = [{"label": "Forward", "id": "forward"}, {"label": "Left", "id": "left"},
                        {"label": "Backwards", "id": "backwards"}, {"label": "Right", "id": "right"},
                        {"label": "Jump", "id": "jump"}, {"label": "Break block", "id": "blockBreak"},
                        {"label": "Place block", "id": "blockPlace"}, {"label": "Pick block", "id": "blockPick"},
                        {"label": "Wireframe", "id": "wireframe"}, {"label": "Debug info", "id": "debugInfo"}]

        self.selectedButton = None
        self.waitingForInput = None
        self.buttonCooldowns = {}

        self.pgm = pgm.Menu(width=self.ui.res[0], height=self.ui.res[1], columns=2, rows=len(self.keybinds)+2, theme=menu.pgmTheme, title='Keybinds')

        for button in self.keybinds : #Button labels
            self.pgm.add.label(button["label"])
        
        self.pgm.add.label("")
        self.pgm.add.button("GO BACK", self.goBackButton)
        
        for button in self.keybinds : #Buttons
            name = self.keycodeToName(self.config.keybinds[button["id"]])
            self.pgm.add.button(name, self.keybindButtonPress, button_id=button["id"], onselect=self.keybindButtonSelect)
            self.buttonCooldowns[button["id"]] = -1

        self.pgm.add.label("")
        self.pgm.add.label("")
    
    def keycodeToName(self, keycode) :
        if keycode == None :
            return "NONE"

        custom = {0: "Left MB", 1: "Middle MB", 2: "Right MB", 3: "MB4", 4: "MB5", 5:"MB6"}

        if keycode in custom :
            return custom[keycode]

        name = pg.key.name(keycode - 5) #First five indexes are the mouse buttons

        if not name :
            return "???"

        return name.upper()

    def keybindButtonSelect(self, selected, widget, menu) :
        self.selectedButton = widget

    def keybindButtonPress(self) :
        widget = self.selectedButton
        
        if not widget : #No button selected
            return
        
        buttonId = widget.get_id()

        if self.buttonCooldowns[buttonId] > self.ui.app.time : #Button on cooldown 
            return

        if self.waitingForInput : #Set previously selected button's text back
            name = self.keycodeToName(self.config.keybinds[buttonId])
            self.waitingForInput.set_title(name)
        
        self.waitingForInput = widget
        widget.set_title("...")

    def goBackButton(self) :
        self.menu.currentScreen = "settings"

    def checkForInput(self) :
        keys = self.ui.getPressed()

        if True in keys : #If any key is pressed
            for keyCode in range(len(keys)) :
                if keys[keyCode] :
                    widget = self.selectedButton
                    buttonId = widget.get_id()

                    self.config.keybinds[buttonId] = keyCode

                    name = self.keycodeToName(keyCode)
                    widget.set_title(name)

                    self.waitingForInput = None
                    
                    self.buttonCooldowns[buttonId] = self.ui.app.time + 0.25 #Prevent from cliking on the keybind button again on accident

    def resize(self) :
        width, height = self.ui.surface.get_size()
        self.pgm.resize(width, height, screen_dimension=(width, height))

    def tick(self) :
        self.pgm.update(self.ui.app.pgEvents)

        if self.waitingForInput :
            self.checkForInput()

    def draw(self) :
        self.pgm.draw(self.ui.surface)
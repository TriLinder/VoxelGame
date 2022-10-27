import pygame as pg
import pygame_menu as pgm

class Menu :
    def __init__(self, ui) -> None :
        self.ui = ui
        self.config = ui.app.config
        
        self.visible = True
        self.showInMenu = True
        self.isDebugElement = False
        
        self.pgmTheme = self.ui.pgmTheme

        self.screens = {"pause": PauseMenu(self, ui), "main": MainMenu(self, ui), "worldList": WorldListMenu(self, ui),
                        "createWorld": CreateWorldMenu(self, ui), "settings": SettingsMenu(self, ui), "keybinds": Keybinds(self, ui)}
        self.currentScreen = "main"

        self.resize()

    def tick(self) :
        if (not self.visible) and self.ui.app.gamePaused and self.ui.app.inGame :
            self.currentScreen = "pause"
        
        if self.visible and self.ui.app.inGame and (not self.ui.app.gamePaused) :
            if self.currentScreen == "settings" :
                self.screens["settings"].goBackButton()
            
            self.currentScreen = None

        self.visible = bool(self.currentScreen)
        if self.visible :
            self.ui.redrawNextFrame = True

            if self.currentScreen :
                try :
                    self.screens[self.currentScreen].tick()
                except AssertionError : #pygame_menu weirdness while resizing the window
                    pass
    
    def resize(self) :
        for screen in self.screens.values() :
            screen.resize()
    
    def render(self) :
        if not self.ui.app.inGame :
            overlayColor = (42, 42, 42, 255) #RGBA
        else :
            overlayColor = (0, 0, 0, 150) #RGBA

        pg.draw.rect(self.ui.surface, overlayColor, [0, 0, self.ui.res[0], self.ui.res[1]]) #Overlay

        if self.currentScreen :
            self.screens[self.currentScreen].draw()

# ------------------ #

class PauseMenu :
    def __init__(self, menu, ui) -> None :
        self.ui = ui
        self.menu = menu
        
        self.pgm = pgm.Menu(width=self.ui.res[0], height=self.ui.res[1], theme=self.ui.pgmTheme, title='Paused')

        self.pgm.add.button("CONTINUE PLAYING", self.resumeButton)
        self.pgm.add.button("SETTINGS", self.settingsButton)
        self.pgm.add.button("MAIN MENU", self.mainMenuButton)

        self.resize()
    
    def resumeButton(self) :
        self.ui.app.gamePaused = False
        self.ui.redrawInTicks = 2

    def settingsButton(self) :
        self.menu.currentScreen = "settings"
    
    def mainMenuButton(self) :
        self.ui.app.scene.destroy()
        self.ui.app.inGame = False
        self.ui.app.gamePaused = True
        
        self.ui.redrawInTicks = 2

        self.menu.currentScreen = "main"
        self.menu.screens["worldList"].reloadList()

    def tick(self) :
        self.pgm.update(self.ui.app.pgEvents)
    
    def resize(self) :
        width, height = self.ui.surface.get_size()
        self.pgm.resize(width, height, screen_dimension=(width, height))

    def draw(self) :
        self.pgm.draw(self.ui.surface)

class MainMenu :
    def __init__(self, menu, ui) -> None :
        self.ui = ui
        self.menu = menu

        self.pgm = pgm.Menu(width=self.ui.res[0], height=self.ui.res[1], theme=menu.pgmTheme, title='Main menu')
        
        self.pgm.add.button("PLAY", self.playButton)
        self.pgm.add.button("SETTINGS", self.settingsButton)
        self.pgm.add.button("QUIT", self.quitButton)

    def playButton(self) :
        self.menu.currentScreen = "worldList"

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

class WorldListMenu :
    def __init__(self, menu, ui) -> None :
        self.ui = ui
        self.menu = menu
        self.saveMan = ui.app.saveMan
        self.config = self.ui.app.config

        self.pgmListTheme = menu.pgmTheme.copy()
        self.pgmListTheme.title_bar_style = 1004

        self.pgmOuter = pgm.Menu(width=self.ui.res[0], height=self.ui.res[1], theme=menu.pgmTheme, title='Load a world')
        
        self.outerButtonFrame = self.pgmOuter.add.frame_h(border_color=(255, 255, 255, 0), border_width=0, width=400, height=200)
        goBackButton = self.pgmOuter.add.button("GO BACK", self.goBackButton)
        newWorldButton = self.pgmOuter.add.button("NEW WORLD", self.newWorldButton)
        self.outerButtonFrame._relax = True
        self.outerButtonFrame.set_float(True)
        self.outerButtonFrame.pack(goBackButton)
        self.outerButtonFrame.pack(newWorldButton)

        self.selectedButton = None
        self.mouseOverSave = None
        
        self.reloadList()
        self.resize()
    
    def reloadList(self) :
        self.pgmList = pgm.Menu(width=self.ui.res[0], height=self.ui.res[1], theme=self.pgmListTheme, title='', position=(50, 50))
        
        self.saves = self.saveMan.getSaves()

        if len(self.saves) == 0 :
            self.pgmList.add.label("There currently aren't any worlds.")
            self.pgmList.add.label("Try creating one.")

        for world in self.saves :
            worldFrame = self.pgmList.add.frame_v(border_color=(255, 255, 255), background_color=(42, 42, 42), border_width=1, width=800, height=155, frame_id=f"frame_{world.worldId}")
            
            nameElement = self.pgmList.add.label(world.worldName, align=pgm.locals.ALIGN_LEFT, label_id=f"name_{world.worldId}")
            lastPlayedElement = self.pgmList.add.label(f"Last played: {world.getLastPlayed()}", align=pgm.locals.ALIGN_LEFT, label_id=f"lastPlayed_{world.worldId}")
            
            buttonFrame = self.pgmList.add.frame_h(border_color=(255, 255, 255, 0), border_width=0, width=400, height=50, padding=(0,0,0,0), frame_id=f"buttonFrame_{world.worldId}")
            
            playButton = self.pgmList.add.button("PLAY", self.playButtonPress, align=pgm.locals.ALIGN_RIGHT, button_id=f"play_{world.worldId}", onselect=self.worldButtonSelect)
            deleteButton = self.pgmList.add.button("DELETE", self.deleteButtonPress, align=pgm.locals.ALIGN_RIGHT, button_id=f"delete_{world.worldId}", onselect=self.worldButtonSelect)

            buttonFrame._relax = True
            buttonFrame.pack(playButton)
            buttonFrame.pack(deleteButton)

            worldFrame._relax = True
            worldFrame.pack(nameElement)
            worldFrame.pack(lastPlayedElement)
            worldFrame.pack(buttonFrame)

        self.resize()

    def worldButtonSelect(self, selected, widget, menu) :
        self.selectedButton = widget.get_id()

    def playButtonPress(self) :
        if not self.selectedButton :
            return
        
        if self.selectedButton.startswith("play_") :
            worldId = self.selectedButton[5:]

            self.ui.app.scene.loadFromFile(worldId)

            self.ui.app.gamePaused = False
            self.ui.app.inGame = True
            self.menu.currentScreen = None
            self.ui.redrawInTicks = 2

    def deleteButtonPress(self) :
        if not self.selectedButton :
            return
        
        if self.selectedButton.startswith("delete_") :
            worldId = self.selectedButton[7:]
        
            self.saveMan.deleteSave(worldId)
            self.reloadList()
    
    def newWorldButton(self) :
        self.menu.currentScreen = "createWorld"

    def goBackButton(self) :
        self.menu.currentScreen = "main"
    
    def drawSaveScreenshot(self, worldId) :
        for save in self.saves :
            if save.worldId == worldId :
                break
        
        img = save.screenshot

        img = pg.transform.smoothscale(img, self.ui.res)
        img.set_alpha(150)
        pg.draw.rect(self.ui.surface, (0,0,0), [0, 0, self.ui.res[0], self.ui.res[1]])
        self.ui.surface.blit(img, img.get_rect())

    def resize(self) :
        width, height = self.ui.surface.get_size()
        self.pgmList.resize(width, height*0.75, screen_dimension=(width, height))
        self.pgmOuter.resize(width, height, screen_dimension=(width, height))
        self.outerButtonFrame.translate(0, (height * 0.95) / 2)

    def tick(self) :
        try :
            self.pgmList.update(self.ui.app.pgEvents)
            self.pgmOuter.update(self.ui.app.pgEvents)
        except RecursionError : #Fix pygame_menu crash when pressing the up arrow
            pass

        mouseOverWidget = self.pgmList.get_mouseover_widget()

        if mouseOverWidget :
            widgetID = mouseOverWidget.get_id()
            
            if "_" in widgetID :
                self.mouseOverSave = widgetID.split("_")[1]
        else :
            self.mouseOverSave = None

    def draw(self) :
        if self.mouseOverSave :
            self.drawSaveScreenshot(self.mouseOverSave)

        self.pgmList.draw(self.ui.surface)
        self.pgmOuter.draw(self.ui.surface)

class CreateWorldMenu :
    def __init__(self, menu, ui) -> None :
        self.ui = ui
        self.menu = menu
        self.saveMan = ui.app.saveMan
        
        self.pgm = pgm.Menu(width=self.ui.res[0], height=self.ui.res[1], theme=menu.pgmTheme, title='Create a world')

        self.nameInput = self.pgm.add.text_input("Name: ", maxchar=20)
        self.seedInputPlaceholderReplaced = False
        self.seedInput = self.pgm.add.text_input("Seed: ", default="RANDOM", onselect=self.seedInputSelect, maxchar=20)
        
        self.buttonFrame = self.pgm.add.frame_h(border_color=(255, 255, 255, 0), border_width=0, width=400, height=200)
        goBackButton = self.pgm.add.button("GO BACK", self.goBackButton)
        createWorldButton = self.pgm.add.button("NEW WORLD", self.createWorldButton)
        self.buttonFrame._relax = True
        self.buttonFrame.set_float(True)
        self.buttonFrame.pack(goBackButton)
        self.buttonFrame.pack(createWorldButton)

        self.reset()

    def reset(self) :
        self.nameInput.set_value("")
        self.seedInput.set_value("RANDOM")
        self.seedInputPlaceholderReplaced = False

        self.resize()

    def seedInputSelect(self, selected, widget, menu) :
        if not self.seedInputPlaceholderReplaced and self.ui.app.time > 0.25 :
            widget.set_value("")

            self.seedInputPlaceholderReplaced = True

    def createWorldButton(self) :
        worldName = self.nameInput.get_value().strip()
        seedString = self.seedInput.get_value().strip()

        if not len(worldName) > 0 :
            return

        if len(seedString) == 0 or (not self.seedInputPlaceholderReplaced) :
            seedString = None
        
        self.saveMan.newWorld(name=worldName, seed=seedString)
        self.menu.currentScreen = None
        self.reset()

    def goBackButton(self) :
        self.menu.currentScreen = "worldList"
        self.reset();

    def resize(self) :
        width, height = self.ui.surface.get_size()
        self.pgm.resize(width, height, screen_dimension=(width, height))

        self.buttonFrame.translate(0, (height * 0.90) / 2)

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
        
        self.fullscreenSwitchElement = self.pgm.add.toggle_switch("Fullscreen: ", default=self.config.fullscreen, state_text=("OFF", "ON"), onchange=self.fullscreenSwitchChange)
        self.pgm.add.range_slider("Render distance:", default=self.config.renderDistance, range_values=(1, 8), increment=1, onchange=self.renderDistanceSlider, value_format=lambda x: str(round(x)))
        self.pgm.add.range_slider("Mouse sensitivity:", default=self.config.mouseSensitivity, range_values=(1, 100), increment=5, onchange=self.mouseSensitivitySlider, value_format=lambda x: str(round(x)))
        self.pgm.add.range_slider("FPS Limit:", default=self.config.fpsLimit, range_values=(15, 120), increment=5, onchange=self.fpsLimitSlider, value_format=lambda x: str(round(x)))
        self.pgm.add.range_slider("FOV:", default=self.config.fov, range_values=(15, 120), increment=10, onchange=self.fovSlider, value_format=lambda x: str(round(x)))
        self.pgm.add.button("KEYBINDS", self.keybindsButton)
        self.pgm.add.button("GO BACK", self.goBackButton)

    def fullscreenSwitchChange(self, value) :
        self.config.fullscreen = value
        self.ui.redrawInTicks = 2
        pg.display.toggle_fullscreen()

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

        self.ui.app.camera.updateProjM() #Update camera FOV
        self.ui.app.shaderMan.updateCamera()

    def keybindsButton(self) :
        self.menu.currentScreen = "keybinds"

    def goBackButton(self) :
        self.config.writeToFile()

        if not self.ui.app.inGame :
            self.menu.currentScreen = "main"
        else :
            self.menu.currentScreen = "pause"
    
    def resize(self) :
        width, height = self.ui.surface.get_size()
        self.pgm.resize(width, height, screen_dimension=(width, height))

    def tick(self) :
        self.pgm.update(self.ui.app.pgEvents)

        self.fullscreenSwitchElement.set_value(self.config.fullscreen)
    
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
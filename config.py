import pygame as pg
import json
import os

defaultConfig = {"renderDistance": 1, "fpsLimit": 60, "keybinds": {"forward": pg.K_w + 5, "backwards": pg.K_s + 5, "left": pg.K_a + 5, "right": pg.K_d + 5,
                "jump": pg.K_SPACE + 5, "blockPlace": 2, "blockPick": 1, "blockBreak": 0, "wireframe": pg.K_g + 5, "debugInfo": pg.K_h + 5},
                "mouseSensitivity": 10, "fov": 70, "fullscreen": False}

class Config :
    def __init__(self, app) -> None :
        self.app = app

        if not os.path.isfile("settings.json") :
            with open("settings.json", "w") as f :
                f.write(json.dumps(defaultConfig, indent=4))
        
        self.loadConfig()
    
    def loadConfig(self) :
        with open("settings.json", "r") as f :
            self.config = json.loads(f.read())
        
        self.renderDistance = self.config["renderDistance"]
        self.fpsLimit = self.config["fpsLimit"]
        self.keybinds = self.config["keybinds"]
        self.mouseSensitivity = self.config["mouseSensitivity"]
        self.fov = self.config["fov"]
        self.fullscreen = self.config["fullscreen"]

    def updateDict(self) :
        self.config["renderDistance"] = self.renderDistance
        self.config["fpsLimit"] = self.fpsLimit
        self.config["keybinds"] = self.keybinds
        self.config["mouseSensitivity"] = self.mouseSensitivity
        self.config["fov"] = self.fov
        self.config["fullscreen"] = self.fullscreen

    def writeToFile(self) :
        self.updateDict()

        with open("settings.json", "w") as f :
            f.write(json.dumps(self.config, indent=4))
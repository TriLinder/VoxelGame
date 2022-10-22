import json
import os

defaultConfig = {"renderDistance": 1, "fpsLimit": 60, "keybinds": {"forward": 119, "backwards": 115, "left": 97, "right": 100, "jump": 32, "wireframe": 103, "debugInfo": 104},
                "mouseSensitivity": 10, "fov": 70}

class Config :
    def __init__(self, app) -> None :
        self.app = app

        if not os.path.isfile("settings.json") :
            with open("settings.json", "w") as f :
                f.write(json.dumps(defaultConfig))
        
        self.loadConfig()
    
    def loadConfig(self) :
        with open("settings.json", "r") as f :
            self.config = json.loads(f.read())
        
        self.renderDistance = self.config["renderDistance"]
        self.fpsLimit = self.config["fpsLimit"]
        self.keybinds = self.config["keybinds"]
        self.mouseSensitivity = self.config["mouseSensitivity"]
        self.fov = self.config["fov"]

    def updateDict(self) :
        self.config["renderDistance"] = self.renderDistance
        self.config["fpsLimit"] = self.fpsLimit
        self.config["keybinds"] = self.keybinds
        self.config["mouseSensitivity"] = self.mouseSensitivity
        self.config["fov"] = self.fov

    def writeToFile(self) :
        self.updateDict()

        with open("settings.json", "w") as f :
            f.write(json.dumps(self.config))
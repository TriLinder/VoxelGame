import json
import os

defaultConfig = {"renderDistance": 1, "fpsLimit": 60, "keybinds": {"forward": 119, "backwards": 115, "left": 97, "right": 100, "jump": 32, "wireframe": 103, "debugInfo": 104}}

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
    
    def updateDict(self) :
        self.config["renderDistance"] = self.renderDistance
        self.config["fpsLimit"] = self.fpsLimit
        self.config["keybinds"] = self.keybinds

    def writeToFile(self) :
        self.updateDict()

        with open("settings.json", "w") as f :
            f.write(json.dumps(self.config))
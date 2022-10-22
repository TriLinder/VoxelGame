import json
import os

defaultConfig = {"renderDistance": 1, "fpsLimit": 60}

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
    
    def updateDict(self) :
        self.config["renderDistance"] = self.renderDistance
        self.config["fpsLimit"] = self.fpsLimit

    def writeToFile(self) :
        self.updateDict()

        with open("settings.json", "w") as f :
            f.write(json.dumps(self.config))
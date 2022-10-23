import json
import os
import time
import shutil

class SaveManager :
    def __init__(self, app) -> None :
        self.app = app
    
    def getSaves(self) :
        if not os.path.isdir("saves") :
            return []
        
        saves = []

        for dir in os.listdir("saves") :
            dir = os.path.join("saves", dir)

            infoFile = os.path.join(dir, "info.json")

            if not os.path.isfile(infoFile) :
                continue

            with open(infoFile, "r") as f :
                info = json.loads(f.read())
        
            save = Save(worldName=info["worldName"], worldId=info["worldId"], seed=info["seed"], lastPlayed=info["lastPlayed"], playerInfo=info["player"])
            saves.append(save)
        
        saves.sort(key=lambda save: save.lastPlayed)

        return saves

    def deleteSave(self, worldId) :
        directory = os.path.join("saves", worldId)

        if not os.path.isdir(directory) :
            return
        
        shutil.rmtree(directory)

class Save :
    def __init__(self, worldName=None, worldId=None, seed=None, lastPlayed=None, playerInfo=None) -> None :
        self.worldName = worldName
        self.worldId = worldId
        self.seed = None
        self.lastPlayed = lastPlayed
        self.playerInfo = playerInfo

    def getLastPlayed(self) :
        localTime = time.localtime(self.lastPlayed)
        return time.strftime("%Y-%m-%d %H:%M:%S", localTime)
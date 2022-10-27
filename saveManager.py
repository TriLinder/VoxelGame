import json
import os
import time
import shutil
import pygame as pg

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
            screenshotFile = os.path.join(dir, "screenshot.png")

            if not os.path.isfile(infoFile) :
                continue

            with open(infoFile, "r") as f :
                info = json.loads(f.read())
        
            save = Save(worldName=info["worldName"], worldId=info["worldId"], seed=info["seed"], lastPlayed=info["lastPlayed"], playerInfo=info["player"])
            save.loadScreenshot(screenshotFile)

            saves.append(save)
        
        saves.sort(key=lambda save: save.lastPlayed, reverse=True)

        return saves
    
    def newWorld(self, name=None, seed=None) :
        self.app.gamePaused = False
        self.app.inGame = True
        self.app.ui.redrawInTicks = 2

        self.app.scene.newWorld(worldName=name, seed=seed)
        self.app.scene.reset()

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

        self.screenshot = None

    def loadScreenshot(self, path) :
        self.screenshot = pg.image.load(path)

    def getLastPlayed(self) :
        localTime = time.localtime(self.lastPlayed)
        return time.strftime("%Y-%m-%d %H:%M:%S", localTime)
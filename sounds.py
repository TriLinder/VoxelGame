import pygame as pg
import random
import json
import os

soundsDir = "sounds"

with open(os.path.join(soundsDir, "sounds.json"), "r") as f :
    soundList = json.loads(f.read())

class SoundEngine :
    def __init__(self, app) -> None :
        self.app = app
        
        self.pgSounds = {}
        self.soundPools = {}

        for category in soundList :
            self.soundPools[category] = {}
            for poolId in soundList[category] :
                self.soundPools[category][poolId] = SoundPool(self, soundList[category][poolId])
    
    def play(self, category, poolId) :
        self.soundPools[category][poolId].play()

    def getPgSound(self, path) :
        if not path in self.pgSounds :
            self.pgSounds[path] = pg.mixer.Sound(os.path.join(soundsDir, path))

        return self.pgSounds[path]

class SoundPool :
    def __init__(self, soundE, pool) -> None:
        self.soundE = soundE
        self.poolPaths = pool
        self.poolPgSounds = []

        for path in self.poolPaths :
            self.poolPgSounds.append(soundE.getPgSound(path))
        
    def play(self, index=None) :
        if index :
            sound = self.poolPgSounds[index]
        else :
            sound = random.choice(self.poolPgSounds)

        sound.play()
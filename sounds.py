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

        pg.mixer.set_num_channels(32)

        for category in soundList :
            self.soundPools[category] = {}
            for poolId in soundList[category] :
                self.soundPools[category][poolId] = SoundPool(self, soundList[category][poolId])
    
    def play(self, category, poolId, pos=None, volume=1.0, force=False) :
        self.soundPools[category][poolId].play(pos=pos, volume=volume, force=force)

    def stop(self, category, poolId, fadeout=None) :
        self.soundPools[category][poolId].stop(fadeout=fadeout)

    def getPgSound(self, path) :
        if not path in self.pgSounds :
            self.pgSounds[path] = pg.mixer.Sound(os.path.join(soundsDir, path))

        return self.pgSounds[path]

class SoundPool :
    def __init__(self, soundE, pool) -> None:
        self.soundE = soundE
        self.poolPaths = pool
        self.poolPgSounds = []

        self.soundEndTime = -1
        self.channel = None

        for path in self.poolPaths :
            self.poolPgSounds.append(soundE.getPgSound(path))
        
    def play(self, index=None, pos=None, volume=1.0, force=False) :
        if not self.soundE.app.time > self.soundEndTime and (not force) : #Sound already playing
            return
        
        if index :
            sound = self.poolPgSounds[index]
        else :
            sound = random.choice(self.poolPgSounds)

        c = pg.mixer.find_channel(force=False)

        c.set_volume(volume * self.soundE.app.config.volume)

        if c :
            c.play(sound)
            self.soundEndTime = self.soundE.app.time + sound.get_length()
            self.channel = c
    
    def stop(self, fadeout=None) :
        if self.channel and (not self.soundE.app.time > self.soundEndTime) :
            if fadeout :
                self.channel.fadeout(fadeout)
                self.soundEndTime = self.soundE.app.time + (fadeout / 1000)
            else :
                self.channel.stop()
                self.soundEndTime = self.soundE.app.time + 0
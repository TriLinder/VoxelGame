import math
import uuid
import time
import random
import json
import os

from chunk import Chunk
from worldGen import WorldGen

class Scene :
    def __init__(self, app) -> None :
        self.app = app
        self.config = app.config
        self.camera = self.app.camera

        self.newWorld()

        self.loadedChunks = {}
    
    def newWorld(self, seed=None, worldName=None, worldId=None) :
        self.worldId = worldId
        if not self.worldId :
            self.worldId = uuid.uuid4().hex

        self.worldName = worldName
        if not self.worldName :
            self.worldName = f"world-{self.worldId}"

        if not seed :
            seed = random.randint(0, 10000000)
        
        self.worldGen = WorldGen(seed)
    
    def reset(self) :
        self.app.player.reset()
    
    def saveToDict(self) :
        j = {}

        j["lastPlayed"] = round(time.time())
        j["player"] = self.app.player.saveToDict()
        j["seed"] = self.worldGen.seed
        j["worldId"] = self.worldId
        j["worldName"] = self.worldName

        return j
    
    def loadFromDict(self, j) :
        self.newWorld(worldId=j["worldId"], worldName=j["worldName"], seed=j["seed"])
        self.app.player.loadFromDict(j["player"])

    def saveToFile(self) :
        directory = os.path.join("saves", self.worldId)
        os.makedirs(directory, exist_ok=True)

        file = os.path.join(directory, "info.json")

        with open(file, "w") as f :
            f.write(json.dumps(self.saveToDict()))
    
    def loadFromFile(self, worldId) :
        infoFile = os.path.join("saves", worldId, "info.json")

        if not os.path.isfile(infoFile) :
            return

        with open(infoFile, "r") as f :
            j = json.loads(f.read())
        
        self.loadFromDict(j)
    
    def loadNearChunks(self) :
        chunksToLoad = []
        currentChunkX, currentChunkY = self.camera.getChunk()

        chunksToLoad.append( (currentChunkX, currentChunkY) )

        for i in range(1, self.config.renderDistance) :
            chunksToLoad.append( ((currentChunkX+i, currentChunkY+0)) )
            chunksToLoad.append( ((currentChunkX-i, currentChunkY+0)) )
            chunksToLoad.append( ((currentChunkX+0, currentChunkY+i)) )
            chunksToLoad.append( ((currentChunkX+0, currentChunkY-i)) )
        
        #Unload far-away chunks
        chunksToUnload = []
        for chunk in self.loadedChunks :
            if not chunk in chunksToLoad :
                self.loadedChunks[chunk].unload()
                chunksToUnload.append(chunk) #Prevent dictionary size changing during iteration

        for chunk in chunksToUnload :
            del self.loadedChunks[chunk]
        
        #Load unloaded chunks
        for chunk in chunksToLoad :
            self.loadChunk(chunkCoords=chunk)
    
    def loadChunk(self, chunkCoords=(0, 0)) :
        if not chunkCoords in self.loadedChunks :
            self.loadedChunks[chunkCoords] = Chunk(self.app, chunkCoords=chunkCoords)

    def chunkCoordsFromBlockCoords(self, x, z) :
        chunkX, chunkZ = math.floor(round(x) / 16), math.floor(round(z) / 16)
        
        return chunkX, chunkZ
    
    def chunkObjectFromBlockCoords(self, x, z) :
        chunkX, chunkZ = self.chunkCoordsFromBlockCoords(x, z)

        try :
            return self.loadedChunks[(chunkX, chunkZ)]
        except KeyError :
            return None
    
    def destroy(self) :
        toDestroy = []

        for chunk in self.loadedChunks.values() :
            chunk.unload()

            toDestroy.append((chunk.chunkX, chunk.chunkZ)) #Prevent dictionary size changing during iteration
        
        for chunkCoords in toDestroy :
            del self.loadedChunks[chunkCoords]

        self.saveToFile()

    def tick(self) :
        if self.app.inGame :
            self.loadNearChunks()

    def render(self) :
        for chunk in self.loadedChunks.values() :
            chunk.render()
import math

from chunk import Chunk
from worldGen import WorldGen

class Scene :
    def __init__(self, app) -> None :
        self.app = app
        self.config = app.config
        self.camera = self.app.camera

        self.worldName = "world0"

        self.worldGen = WorldGen()

        self.loadedChunks = {}
    
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

    def render(self) :
        if self.app.inGame :
            self.loadNearChunks()

        for chunk in self.loadedChunks.values() :
            chunk.render()
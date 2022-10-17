from chunk import Chunk

renderDistance = 1

class Scene :
    def __init__(self, app) -> None :
        self.app = app
        self.camera = self.app.camera

        self.loadedChunks = {}
    
    def loadNearChunks(self) :
        chunksToLoad = []
        currentChunkX, currentChunkY = self.camera.getChunk()

        chunksToLoad.append( (currentChunkX, currentChunkY) )

        for i in range(1, renderDistance) :
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


    def render(self) :
        self.loadNearChunks()

        for chunk in self.loadedChunks.values() :
            chunk.render()
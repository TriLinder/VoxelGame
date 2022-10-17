import time

import chunk
from block import Block

heightLimit = 2
chunkSize = 16

class Chunk :
    def __init__(self, app, chunkCoords=(0,0)) -> None:
        self.app = app
        self.blocks = []
        self.totalBlockCount = chunkSize*chunkSize*heightLimit

        self.chunkX = chunkCoords[0]
        self.chunkZ = chunkCoords[1]

        startTime = time.time()

        self.clear()
        #self.linesTest()
        self.cullAllBlocks()

        print(f"Chunk generation took {round(time.time() - startTime, 2)} seconds. {self.totalBlockCount} blocks generated ({round((time.time() - startTime) / (self.totalBlockCount), 3)}s per block).")

    def clear(self) :
        self.blocks = []

        blocksGenerated = 0

        for x in range(chunkSize) :
            self.blocks.append([])
            for y in range(heightLimit) :
                self.blocks[x].append([])
                for z in range(chunkSize) :
                    print(f"{(blocksGenerated/(self.totalBlockCount/100))}%")
                    self.blocks[x][y].append(Block(self.app, "grass", (x*2+(self.chunkX*chunkSize*2), y*2, z*2+(self.chunkZ*chunkSize*2))))
                    blocksGenerated += 1

    def linesTest(self) :
        for a in range(chunkSize) :
            self.blocks[a][a][a].changeId("debugBlock")
            self.blocks[a*-1][a][a*-1].changeId("debugBlock")

    def unload(self) :
        pass
    
    def getBlockID(self, x, y, z) :
        try :
            return self.blocks[x][y][z].id
        except IndexError :
            return None
    
    def cullAllBlocks(self) :
        for x in range(chunkSize) :
            for y in range(heightLimit) :
                for z in range(chunkSize) :
                    self.blocks[x][y][z].cull(surroundingBlocks=[self.getBlockID(x+1,y,z), self.getBlockID(x-1,y,z), self.getBlockID(x,y+1,z), self.getBlockID(x,y-1,z), self.getBlockID(x,y,z+1), self.getBlockID(x,y,z-1)])

    def render(self) :
        startTime = time.time()

        for x in range(chunkSize) :
            for y in range(heightLimit) :
                for z in range(chunkSize) :
                    self.blocks[x][y][z].render()
    
        #print(f"Chunk rendering took {round(time.time() - startTime, 3)} seconds. ({round((time.time() - startTime) / (self.totalBlockCount), 3)}s per block)")
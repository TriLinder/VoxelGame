import os
import time
import json

from block import Block

heightLimit = 32
chunkSize = 16

noSave = True

class Chunk :
    def __init__(self, app, chunkCoords=(0,0)) -> None:
        self.app = app
        self.worldGen = app.scene.worldGen
        self.blocks = []
        self.totalBlockCount = chunkSize*chunkSize*heightLimit

        self.chunkX = chunkCoords[0]
        self.chunkZ = chunkCoords[1]

        self.heightMap = {}

        startTime = time.time()

        self.clear()
        
        #self.linesTest()
        #self.generatePlatform()
        self.generate()

        self.cullAllBlocks()

        #print(f"Chunk generation took {round(time.time() - startTime, 2)} seconds. {self.totalBlockCount} blocks generated ({round((time.time() - startTime) / (self.totalBlockCount), 3)}s per block).")

    def clear(self) :
        self.blocks = []

        blocksGenerated = 0

        for x in range(chunkSize) :
            self.blocks.append([])
            for y in range(heightLimit) :
                self.blocks[x].append([])
                for z in range(chunkSize) :
                    #print(f"{(blocksGenerated/(self.totalBlockCount/100))}%")
                    self.blocks[x][y].append(Block(self.app, "air", (x+(self.chunkX*chunkSize), y, z+(self.chunkZ*chunkSize))))
                    blocksGenerated += 1

    def linesTest(self) :
        for a in range(chunkSize) :
            self.blocks[a][a][a].changeId("debugBlock")
            self.blocks[a*-1][a][a*-1].changeId("debugBlock")

    def generatePlatform(self) :
        for x in range(chunkSize) :
            for z in range(chunkSize) :
                self.blocks[x][0][z].changeId("grass")
    
    def generateHeight(self) :
        for x in range(chunkSize) :
            for z in range(chunkSize) :
                terrainHeight = self.worldGen.getTerrainY(x+(self.chunkX*16), z+(self.chunkZ*16), 5, 14)
                self.heightMap[(x, z)] = terrainHeight
                for y in range(terrainHeight-3) :
                    self.blocks[x][y][z].changeId("stone")
                for y in range(terrainHeight-3, terrainHeight) :
                    self.blocks[x][y][z].changeId("dirt")
                
                self.blocks[x][terrainHeight][z].changeId("grass")
    
    def generateTrees(self) :
        for x in range(chunkSize) :
            for z in range(chunkSize) :
                terrainHeight = self.heightMap[x, z]

                totalX, totalZ = int(x+(self.chunkX*chunkSize)), int(z+(self.chunkZ*chunkSize))

                shouldHaveTree = self.worldGen.shouldHaveTree(totalX, totalZ)
                if shouldHaveTree :
                    tree = self.worldGen.generateTree(totalX, totalZ)

                    #Logs
                    for y in range(terrainHeight, terrainHeight + tree["height"]) :
                        self.blocks[x][y][z].changeId("log")
                    
                    #Leaves base
                    for leaveX in range(5) :
                        for leaveZ in range(5) :
                            try :
                                if not tree["leavesToRemove"][leaveX*leaveZ] :
                                    self.blocks[x + leaveX - 2][terrainHeight + tree["height"] - 3][z + leaveZ - 2].changeId("leaves")

                                if (leaveX in range(1,4)) and (leaveZ in range(1,4)) :
                                    self.blocks[x + leaveX - 2][terrainHeight + tree["height"] - 2][z + leaveZ - 2].changeId("leaves")
                                    if not tree["leavesToRemove"][leaveX+leaveZ] :
                                        self.blocks[x + leaveX - 2][terrainHeight + tree["height"] - 1][z + leaveZ - 2].changeId("leaves")
                                        self.blocks[x + leaveX - 2][terrainHeight + tree["height"] - 3][z + leaveZ - 0].changeId("leaves")
                            except IndexError : #Leaves out of chunk
                                pass


    def generate(self) :
        self.generateHeight()
        self.generateTrees()

    def unload(self) :
        self.saveChunk()
    
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

    def chunkToDict(self) :
        j = {}

        blocksPallete = {}
        blocksPalleteIndex = 0

        blocks = []

        for x in range(chunkSize) :
            blocks.append([])
            for y in range(heightLimit) :
                blocks[x].append([])
                for z in range(chunkSize) :
                    block = self.blocks[x][y][z]

                    if not block.id in blocksPallete :
                        blocksPallete[block.id] = blocksPalleteIndex
                        blocksPalleteIndex += 1

                    blocks[x][y].append(blocksPallete[block.id])
        
        j["dimensions"] = (chunkSize, heightLimit, chunkSize)
        j["pallete"] = list(blocksPallete)
        j["blocks"] = blocks
        j["timestamp"] = round(time.time())

        return j
    
    def saveChunk(self) :
        if noSave :
            return

        j = self.chunkToDict()

        directory = os.path.join("saves", self.app.scene.worldName, "chunks")
        path = os.path.join(directory, f"{self.chunkX}_{self.chunkZ}.json")

        os.makedirs(directory, exist_ok=True)

        with open(path, "w") as f :
            f.write(json.dumps(j).replace(' ', ''))

    def getBlockFromAbsoulteCoords(self, pos) :
        x, y, z = pos
        x, y, z = round(x), round(y), round(z)
        
        try :
            return self.blocks[x - (self.chunkX*chunkSize)][y][z - (self.chunkZ*chunkSize)]
        except IndexError :
            return None

    def render(self) :
        startTime = time.time()

        for x in range(chunkSize) :
            for y in range(heightLimit) :
                for z in range(chunkSize) :
                    self.blocks[x][y][z].render()
    
        #print(f"Chunk rendering took {round(time.time() - startTime, 3)} seconds. ({round((time.time() - startTime) / (self.totalBlockCount), 3)}s per block)")
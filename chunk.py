from block import Block

heightLimit = 2
chunkSize = 16

class Chunk :
    def __init__(self, app) -> None:
        self.app = app
        self.blocks = []

        self.clear()
    
    def clear(self) :
        self.blocks = []

        for x in range(chunkSize) :
            self.blocks.append([])
            for y in range(heightLimit) :
                self.blocks[x].append([])
                for z in range(chunkSize) :
                    self.blocks[x][y].append(Block(self.app, "grass", (x*2, y*2, z*2)))
    
    def getBlockID(self, x, y, z) :
        try :
            return self.blocks[x][y][z].id
        except IndexError :
            return None

    def render(self) :
        for x in range(chunkSize) :
            self.blocks.append([])
            for y in range(heightLimit) :
                self.blocks[x].append([])
                for z in range(chunkSize) :
                    self.blocks[x][y][z].cull(surroundingBlocks=[self.getBlockID(x+1,y,z), self.getBlockID(x-1,y,z), self.getBlockID(x,y+1,z), self.getBlockID(x,y-1,z), self.getBlockID(x,y,z+1), self.getBlockID(x,y,z-1)])
                    self.blocks[x][y][z].render()
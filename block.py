from model import *
import json
import os

with open("blocks.json", "r") as f :
    blockInfo = json.loads(f.read()) 

class Block :
    def __init__(self, app, chunk, id, pos) -> None:
        self.app = app
        self.chunk = chunk

        self.changeId(id)
        self.pos = pos

        x, y, z = pos
        self.chunkRelativePos = (x - (chunk.chunkX*16), y, z - (chunk.chunkZ*16))

        self.object = None

        self.model = None

        self.physicalBlock = False
        self.isFluid = False
        self.flags = []
        
    
    def changeId(self, newId) :
        self.id = newId

        self.flags = blockInfo[self.id]["flags"]
        self.physicalBlock = not "nonPhysical" in self.flags
        self.isFluid = "fluid" in self.flags

        self.updateObject()

    def updateObject(self) :
        self.object = None
        
        if not "nonObject" in self.flags :
            self.model = blockInfo[self.id]["model"]

            if self.model == "cube" :
                x, y, z = self.pos

                if self.isFluid :
                    y -= 0.25

                self.object = Cube(self.app, pos=(x, y, z), textures=self.getTextures())
            elif self.model == "billboard" :
                self.object = Billboard(self.app, pos=self.pos, textures=self.getTextures())
    
    def getTextures(self) :
        if self.id in blockInfo :
            return blockInfo[self.id]["faceTextures"]
        return blockInfo["FALLBACK"]["faceTextures"]
    
    def cull(self, surroundingBlocks=["air", "air", "air", "air", "air", "air"]) :
        if not self.object :
            return
        
        if self.model == "cube" :
            for i in range(6) :
                surroundingBlock = surroundingBlocks[i]

                if surroundingBlock :
                    flags = blockInfo[surroundingBlock]["flags"]
                    faceVisible = ("transparent" in flags) or (not self.isFluid and "fluid" in flags)
                else :
                    faceVisible = True
                self.object.faces[i]["visible"] = faceVisible
        elif self.model == "billboard" :
            visible = False

            for i in range(6) :
                surroundingBlock = surroundingBlocks[i]

                if (not surroundingBlock) or ("transparent" in blockInfo[surroundingBlock]["flags"]) :
                    visible = True
                    break
            
            self.object.faces[0]["visible"] = visible
            self.object.faces[1]["visible"] = visible
            self.object.faces[2]["visible"] = visible
            self.object.faces[3]["visible"] = visible

    def render(self) :
        if self.object :
            self.object.render()
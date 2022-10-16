from model import *
import json
import os

nonObjectBlocks = ["air"]
transparentBlocks = ["air"]

with open(os.path.join("textures", "blocks.json"), "r") as f :
    blockTextures = json.loads(f.read()) 

class Block :
    def __init__(self, app, id, pos) -> None:
        self.id = id
        self.pos = pos
        self.object = None
        
        if not self.id in nonObjectBlocks :
            self.object = Cube(app, pos=self.pos, textures=self.getTextures())
    
    def getTextures(self) :
        if self.id in blockTextures :
            return blockTextures[self.id]["faceTextures"]
        return blockTextures["FALLBACK"]["faceTextures"]
    
    def cull(self, surroundingBlocks=["air", "air", "air", "air", "air", "air"]) :
        if not self.object :
            return
        
        for i in range(6) :
            surroundingBlock = surroundingBlocks[i]

            faceVisible = (not surroundingBlock) or (surroundingBlock in transparentBlocks)
            self.object.faces[i]["visible"] = faceVisible

    def render(self) :
        if self.object :
            self.object.render()
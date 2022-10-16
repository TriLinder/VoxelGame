import os
import pygame as pg

class TextureManager :
    def __init__(self, app) -> None :
        self.app = app
        self.ctx = self.app.ctx
        
        self.textures = {}
        self.loadTexture("test.png", "testTexture")
    
    def getTexture(self, name) :
        return self.textures[name]

    def loadTexture(self, path, name) :
        path = os.path.join("textures", path)
        texture = pg.image.load(path).convert()
        texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
        texture = self.ctx.texture(size=texture.get_size(), components=3, data=pg.image.tostring(texture, 'RGB'))

        self.textures[name] = texture

        return texture
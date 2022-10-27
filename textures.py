import os
import pygame as pg

class TextureManager :
    def __init__(self, app) -> None :
        self.app = app
        self.ctx = self.app.ctx
        
        self.textures = {}

        self.iconPath = os.path.join("textures", "icon.png")
        self.iconTexture = pg.image.load(self.iconPath)
    
    def getTexture(self, name) :
        if not name in self.textures :
            self.loadTexture(os.path.join("textures", name), name)

        return self.textures[name]

    def loadTexture(self, path, name) :
        texture = pg.image.load(path).convert()
        texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
        texture = self.ctx.texture(size=texture.get_size(), components=3, data=pg.image.tostring(texture, 'RGB'))

        self.textures[name] = texture

        return texture
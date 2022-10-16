from model import *
import random

class Scene :
    def __init__(self, app) -> None :
        self.app = app
        self.objects = []

        for x in range(0, 1) :
            for z in range(0, 1) :
                self.objects.append({"object": Cube(app, pos=(x*3, 0, z*3), textures=["grass/sides.png", "grass/sides.png", "grass/top.png", "grass/bottom.png", "grass/sides.png", "grass/sides.png"])})
    
    def render(self) :
        for object in self.objects :
            object["object"].render()
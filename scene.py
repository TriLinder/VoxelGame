from model import *
import random

class Scene :
    def __init__(self, app) -> None :
        self.app = app
        self.objects = []

        for x in range(-16, 16) :
            for z in range(-16, 16) :
                self.objects.append({"object": Cube(app, pos=(x*3, 0, z*3))})
    
    def render(self) :
        for object in self.objects :
            object["object"].render()
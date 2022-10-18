from xml.dom import InvalidModificationErr
import glm
import math

from physics import EntityPhysics

class Player :
    def __init__(self, app) -> None:
        self.app = app
        self.camera = app.camera
        self.scene = app.scene
        self.physics = EntityPhysics(app, self)

        self.physics.controlMovement = True
        self.onGround = True

        self.position = (2, 30, 3)
        self.yaw = 0
        self.pitch = 0

        self.cameraHeight = 2

    def getChunk(self) :
        x, y, z = self.position
        
        chunkX, chunkZ = math.floor(x / 16), math.floor(z / 16)
        return (chunkX, chunkZ)
    
    def inVoid(self) :
        return self.position[1] < -5

    def tick(self) :
        self.yaw, self.pitch = self.camera.yaw, self.camera.pitch

        self.physics.tick()

        if self.inVoid() :
            self.position[1] = 30

        if not self.camera.freeCam :
            self.camera.position = self.position + glm.vec3(0, self.cameraHeight, 0)
            self.camera.update()
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

        self.cameraHeight = 1.75

    def getChunk(self) :
        x, y, z = self.position
        
        chunkX, chunkZ = math.floor(x / 16), math.floor(z / 16)
        return (chunkX, chunkZ)

    def tick(self) :
        self.yaw, self.pitch = self.camera.yaw, self.camera.pitch

        self.physics.tick()
        self.camera.position = self.position + glm.vec3(0, self.cameraHeight, 0)
        self.camera.update()
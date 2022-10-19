import glm
import math
import pygame as pg
import time

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

        self.lookingAt = None
        self.lastPunchTimestamp = -1

        self.cameraHeight = 2

    def getChunk(self) :
        x, y, z = self.position
        
        return self.scene.chunkCoordsFromBlockCoords(x, z)
    
    def inVoid(self) :
        return self.position[1] < -5
    
    def losBlock(self, maxRange) :
        forward = self.physics.forward

        for r in range(maxRange) :
            pos = (self.position + glm.vec3(0, self.cameraHeight, 0)) + forward * r

            chunk = self.scene.chunkObjectFromBlockCoords(pos.x, pos.z)
            if chunk :
                block = chunk.getBlockFromAbsoulteCoords(pos)

                if block and block.physicalBlock :
                    return block

        return None
    
    def blockBreaking(self) :
        if pg.mouse.get_pressed()[0] : #LMB Pressed
            self.lookingAt = self.losBlock(8)
            
            if self.lookingAt and time.time() - self.lastPunchTimestamp > 0.25 :
                self.lastPunchTimestamp = time.time()

                block = self.lookingAt
                block.changeId("air")
                chunk = block.chunk
                chunk.cullNeighbors(block.chunkRelativePos)
        else :
            self.lastPunchTimestamp = -1

    def tick(self) :
        self.yaw, self.pitch = self.camera.yaw, self.camera.pitch

        self.physics.tick()

        if self.inVoid() :
            self.position[1] = 30

        if not self.camera.freeCam :
            self.camera.position = self.position + glm.vec3(0, self.cameraHeight, 0)
            self.camera.update()
        
        self.blockBreaking()
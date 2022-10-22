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
        self.lookingAtEmptyBlock = None
        self.lastPunchTimestamp = -1

        self.selectedBlockId = None

        self.cameraHeight = 2
        self.reach = 8

    def getChunk(self) :
        x, y, z = self.position
        
        return self.scene.chunkCoordsFromBlockCoords(x, z)
    
    def inVoid(self) :
        return self.position[1] < -5
    
    def losBlock(self, maxRange) :
        forward = self.physics.forward
        lastEmptyBlock = None

        for r in range(maxRange) :
            pos = self.camera.position + forward * r

            chunk = self.scene.chunkObjectFromBlockCoords(pos.x, pos.z)
            if chunk :
                block = chunk.getBlockFromAbsoulteCoords(pos)

                if block and block.physicalBlock :
                    self.lookingAt = block
                    self.lookingAtEmptyBlock = lastEmptyBlock

                    return self.lookingAt
                
                lastEmptyBlock = block

        self.lookingAt = None
        self.lookingAtEmptyBlock = None
        return self.lookingAt
    
    def blockBreaking(self) :
        self.losBlock(self.reach)

        if pg.mouse.get_pressed()[0] : #LMB Pressed, break block
            if self.lookingAt and time.time() - self.lastPunchTimestamp > 0.25 :
                self.lastPunchTimestamp = time.time()

                block = self.lookingAt
                block.changeId("air")
                chunk = block.chunk
                chunk.cullNeighbors(block.chunkRelativePos)
                chunk.updateNeighborFluids(block.chunkRelativePos)
        elif pg.mouse.get_pressed()[2] : #RMB Pressed, place block
            if self.selectedBlockId and self.lookingAtEmptyBlock and time.time() - self.lastPunchTimestamp > 0.25 :
                self.lastPunchTimestamp = time.time()

                block = self.lookingAtEmptyBlock
                block.changeId(self.selectedBlockId)
                chunk = block.chunk
                chunk.cullNeighbors(block.chunkRelativePos)
        elif pg.mouse.get_pressed()[1] : #Middle mouse button pressed, pick block
            if self.lookingAt :
                block = self.lookingAt

                self.selectedBlockId = block.id
        else :
            self.lastPunchTimestamp = -1

    def tick(self) :
        if self.app.gamePaused :
            return

        self.yaw, self.pitch = self.camera.yaw, self.camera.pitch

        self.physics.tick()

        if self.inVoid() :
            self.position[1] = 30

        if not self.camera.freeCam :
            self.camera.position = self.position + glm.vec3(0, self.cameraHeight, 0)
        
        self.blockBreaking()
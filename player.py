import glm

from physics import EntityPhysics

class Player :
    def __init__(self, app) -> None:
        self.app = app
        self.ui = app.ui
        self.camera = app.camera
        self.scene = app.scene
        
        self.reset()

        self.cameraHeight = 2
        self.reach = 8
    
    def reset(self) :
        self.physics = EntityPhysics(self.app, self)
        self.physics.controlMovement = True
        self.onGround = True

        self.position = glm.vec3(5, 15, 5)
        self.yaw = 0
        self.pitch = 0

        self.lookingAt = None
        self.lookingAtEmptyBlock = None
        self.lastPunchTimestamp = -1

        self.selectedBlockId = None
    
    def saveToDict(self) :
        j = {}

        j["position"] = tuple(self.position)
        j["rotation"] = (round(self.yaw, 2), round(self.pitch, 2))
        j["selectedBlockId"] = self.selectedBlockId

        return j
    
    def loadFromDict(self, j) :
        pos = j["position"]
        self.position = glm.vec3(pos[0], pos[1], pos[2])
        self.camera.yaw, self.camera.pitch = j["rotation"]
        self.selectedBlockId = j["selectedBlockId"]

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
    
    def blockInteract(self) :
        self.losBlock(self.reach)

        if self.ui.isPressed("blockBreak") : #Break block
            if self.lookingAt and self.app.time - self.lastPunchTimestamp > 0.25 :
                self.lastPunchTimestamp = self.app.time

                block = self.lookingAt
                block.changeId("air")
                chunk = block.chunk
                chunk.cullNeighbors(block.chunkRelativePos)
                chunk.updateNeighborFluids(block.chunkRelativePos)
        elif self.ui.isPressed("blockPlace") : #Place block
            if self.selectedBlockId and self.lookingAtEmptyBlock and self.app.time - self.lastPunchTimestamp > 0.25 :
                self.lastPunchTimestamp = self.app.time

                block = self.lookingAtEmptyBlock
                block.changeId(self.selectedBlockId)
                chunk = block.chunk
                chunk.cullNeighbors(block.chunkRelativePos)

                chunk.updateNeighborFluids(block.chunkRelativePos)
        elif self.ui.isPressed("blockPick") : #Pick block
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
        
        self.blockInteract()
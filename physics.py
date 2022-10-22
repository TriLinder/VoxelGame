import glm
import pygame as pg
from math import floor, ceil

class EntityPhysics :
    def __init__(self, app, entity) -> None:
        self.app = app
        self.entity = entity

        self.terminalVelocity = 2
        self.disableGravity = False

        self.up = glm.vec3(0, 0, 0)
        self.down = glm.vec3(0, 0, 0)
        self.right = glm.vec3(0, 0, 0)
        self.left = glm.vec3(0, 0, 0)
        self.forward = glm.vec3(0, 0, 0)
        self.backwards = glm.vec3(0, 0, 0)

        self.velX = 0
        self.velY = 0
        self.velZ = 0

        self.controlMovement = False
        self.walkingSpeed = 0.5

        self.inFluid = False

    def updateMovementVectors(self) :
        yaw, pitch = glm.radians(self.entity.yaw), glm.radians(self.entity.pitch)

        self.forward.x = glm.cos(yaw) * glm.cos(pitch)
        self.forward.y = glm.sin(pitch)
        self.forward.z = glm.sin(yaw) * glm.cos(pitch)

        self.forward = glm.normalize(self.forward)
        self.right = glm.normalize(glm.cross(self.forward, glm.vec3(0, 1, 0)))
        self.up = glm.normalize(glm.cross(self.right, self.forward))

        self.down = self.up * -1
        self.left = self.right * -1
        self.backwards = self.forward * -1

    def movementControl(self) :
        speed = self.walkingSpeed
        keys = pg.key.get_pressed()

        nonYForward = glm.vec3(self.forward[0], self.forward[1], self.forward[2]) #Copy by value
        nonYForward.y = 0

        nonYBackwards = nonYForward * -1

        if self.inFluid :
            speed *= 0.25
        
        self.disableGravity = False

        velocity = (self.velX, self.velY, self.velZ)

        if keys[pg.K_w] and self.entity.onGround :
            velocity = nonYForward * speed
        if keys[pg.K_a] and self.entity.onGround :
            velocity = self.left * speed
        if keys[pg.K_s] and self.entity.onGround :
            velocity = nonYBackwards * speed
        if keys[pg.K_d] and self.entity.onGround :
            velocity = self.right * speed

        self.velX, self.velY, self.velZ = velocity

        if keys[pg.K_SPACE] and self.entity.onGround :
            if not self.inFluid :
                self.jump()
            else :
                self.disableGravity = True
                self.swimUp()
        self.app.ctx.wireframe = keys[pg.K_g] #Show wireframe when held down

        #self.velX, self.velY, self.velZ = max(min(self.velX, self.terminalVelocity), self.terminalVelocity*-1), max(min(self.velY, self.terminalVelocity), self.terminalVelocity*-1), max(min(self.velZ, self.terminalVelocity), self.terminalVelocity*-1)

    def gravity(self) :
        if (not self.entity.onGround) and (not self.disableGravity) :
            if not abs(self.velY) > self.terminalVelocity :
                if not self.inFluid :
                    self.velY -= 0.005 * self.app.deltaTime
                else :
                    self.velY -= (0.005 * 0.25) * self.app.deltaTime
        elif self.entity.onGround and self.velY < 0 :
            self.velY = 0
    
    def friction(self) :
        if not self.entity.onGround :
            return

        if self.velX < 0 :
            self.velX += 0.01
        elif self.velX > 0 :
            self.velX -= 0.01
        
        if self.velZ < 0 :
            self.velZ += 0.01
        elif self.velZ > 0 :
            self.velZ -= 0.01
        
    def stopSlowMovement(self) :
        if round(self.velX, 2) == 0.0 :
            self.velX = 0
        
        if round(self.velZ, 2) == 0.0 :
            self.velZ = 0
    
    def jump(self) :
        if self.entity.onGround :
            self.velY = 0.1
            self.entity.onGround = False
            self.move()

            self.velY = 1.5
            self.move()
    
    def swimUp(self) :
        self.entity.position += glm.vec3(0, 0.01*self.app.deltaTime, 0)
        self.entity.onGround = False

    def onGroundCheck(self) :
        chunkX, chunkZ = self.entity.getChunk()
        entityX, entityY, entityZ = self.entity.position

        try :
            chunk = self.app.scene.loadedChunks[(chunkX, chunkZ)]
        except KeyError :
            print("PHYSICS: Entity's chunk not loaded")

            self.entity.onGround = True
            return self.entity.onGround

        blocks = chunk.blocks

        try :
            block = blocks[round(entityX)-(chunkX*16)][round(entityY)][round(entityZ)-(chunkZ*16)]
            self.entity.onGround = block.physicalBlock
        except IndexError : #Above chunk height limit
            self.entity.onGround = False

        if self.entity.onGround :
            self.entity.position[1] = round(self.entity.position[1])

        return self.entity.onGround
    
    def inFluidCheck(self) :
        x, y, z = self.entity.position

        chunk = self.app.scene.chunkObjectFromBlockCoords(x, z)
        if chunk :
            block = chunk.getBlockFromAbsoulteCoords((x, y + 0.5, z))
            if block :
                self.inFluid = block.isFluid

    def safePositionCheck(self, pos) :
        x, y, z = pos

        y += 1

        chunk = self.app.scene.chunkObjectFromBlockCoords(x, z)
        if chunk :
            block = chunk.getBlockFromAbsoulteCoords((x, y, z))
            if block :
                if block.pos[1] < y :
                    return True

                return not block.physicalBlock
        else :
            return True
        
        print("PHYSICS: Safe pos check failed")
        return False

    def move(self) :
        newPos = self.entity.position + glm.vec3((self.velX / 100) * self.app.deltaTime, (self.velY / 100) * self.app.deltaTime, (self.velZ / 100) * self.app.deltaTime)
        
        if (self.safePositionCheck(newPos)) :
            self.entity.position = newPos
        else :
            self.velX = 0
            self.velY = 0
            self.velZ = 0

    def tick(self) :
        self.updateMovementVectors()
        self.onGroundCheck()
        self.inFluidCheck()

        if self.controlMovement and not self.app.camera.freeCam :
            self.movementControl()

        self.gravity()
        self.friction()
        self.stopSlowMovement()

        self.move()
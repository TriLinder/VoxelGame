import glm
import pygame as pg
from math import floor, ceil

class EntityPhysics :
    def __init__(self, app, entity) -> None:
        self.app = app
        self.entity = entity

        self.terminalVelocity = 0.01
        
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

    def updateMovementVectors(self) :
        yaw, pitch = glm.radians(self.entity.yaw), glm.radians(self.entity.pitch)

        self.forward.x = glm.cos(yaw) * glm.cos(pitch)
        #self.forward.y = glm.sin(pitch)
        self.forward.y = 0
        self.forward.z = glm.sin(yaw) * glm.cos(pitch)

        self.forward = glm.normalize(self.forward)
        self.right = glm.normalize(glm.cross(self.forward, glm.vec3(0, 1, 0)))
        self.up = glm.normalize(glm.cross(self.right, self.forward))

        self.down = self.up * -1
        self.left = self.right * -1
        self.backwards = self.forward * -1

    def movementControl(self) :
        if not self.entity.onGround :
            return
        
        speed = self.walkingSpeed
        keys = pg.key.get_pressed()

        nonYForward = self.forward
        nonYForward[1] = self.entity.position[1]

        nonYBackwards = nonYForward * -1

        velocity = (self.velX, self.velY, self.velZ)
        
        if keys[pg.K_w] :
            velocity = nonYForward * speed
        if keys[pg.K_a] :
            velocity = self.left * speed
        if keys[pg.K_s] :
            velocity = nonYBackwards * speed
        if keys[pg.K_d] :
            velocity = self.right * speed
        if keys[pg.K_SPACE] :
            self.jump()
        
        self.velX, self.velY, self.velZ = velocity
        print(self.velY)
        #self.velX, self.velY, self.velZ = max(min(self.velX, self.terminalVelocity), self.terminalVelocity*-1), max(min(self.velY, self.terminalVelocity), self.terminalVelocity*-1), max(min(self.velZ, self.terminalVelocity), self.terminalVelocity*-1)

    def gravity(self) :
        if not self.entity.onGround :
            if self.velY < self.terminalVelocity :
                self.velY -= 0.005 * self.app.deltaTime
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

            self.velY = 5
            self.move()

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
            block = blocks[floor(entityX)-(chunkX*16)][ceil(entityY)][floor(entityZ)-(chunkZ*16)]
            self.entity.onGround = block.physicalBlock
        except IndexError : #Above chunk height limit
            self.entity.onGround = False
        return self.entity.onGround

    def move(self) :
        self.entity.position += glm.vec3((self.velX / 100) * self.app.deltaTime, (self.velY / 100) * self.app.deltaTime, (self.velZ / 100) * self.app.deltaTime)

    def tick(self) :
        self.updateMovementVectors()
        self.onGroundCheck()

        if self.controlMovement and not self.app.camera.freeCam :
            self.movementControl()

        self.gravity()
        self.friction()
        self.stopSlowMovement()

        self.move()
import pygame as pg
import glm

fov = 50
near = 0.1
far = 100
movementSpeed = 0.01
mouseSensitivity = 0.1

class Camera :
    def __init__(self, app, position=(2, 3, 3), yaw=-90, pitch=0) -> None:
        self.app = app
        self.aspectRatio = app.windowSize[0] / app.windowSize[1]

        self.position = glm.vec3(position)
        self.yaw = yaw
        self.pitch = pitch
        
        self.up = glm.vec3(0, 1, 0)
        self.down = self.up * -1
        self.right = glm.vec3(1, 0, 0)
        self.left = self.right * -1
        self.forward = glm.vec3(0, 0, -1)
        self.backwards = self.forward * -1

        #View matrix
        self.viewM = self.get_view_matrix()

        #Projection matrix
        self.projM = self.get_projection_matrix()
    
    def update(self) :
        self.move()
        self.rotate()
        self.updateCameraVectors()
        self.viewM = self.get_view_matrix()

    def updateCameraVectors(self) :
        yaw, pitch = glm.radians(self.yaw), glm.radians(self.pitch)

        self.forward.x = glm.cos(yaw) * glm.cos(pitch)
        self.forward.y = glm.sin(pitch)
        self.forward.z = glm.sin(yaw) * glm.cos(pitch)

        self.forward = glm.normalize(self.forward)
        self.right = glm.normalize(glm.cross(self.forward, glm.vec3(0, 1, 0)))
        self.up = glm.normalize(glm.cross(self.right, self.forward))

        self.down = self.up * -1
        self.left = self.right * -1
        self.backwards = self.forward * -1
    
    def rotate(self) :
        relX, relY = pg.mouse.get_rel()

        self.yaw += relX * mouseSensitivity
        self.pitch += (relY * mouseSensitivity) * -1

        self.pitch = max(-89, min(89, self.pitch))

    def move(self) :
        velocity = movementSpeed * self.app.deltaTime

        keys = pg.key.get_pressed()
        if keys[pg.K_w] :
            self.position += self.forward * velocity
        if keys[pg.K_a] :
            self.position += self.left * velocity
        if keys[pg.K_s] :
            self.position += self.backwards * velocity
        if keys[pg.K_d] :
            self.position += self.right * velocity
        if keys[pg.K_SPACE] :
            self.position += self.up * velocity
        if keys[pg.K_LSHIFT] :
            self.position += self.down * velocity

    def get_view_matrix(self) :
        return glm.lookAt(self.position, self.position + self.forward, self.up)

    def get_projection_matrix(self) :
        projectionMatrix = glm.perspective(glm.radians(fov), self.aspectRatio, near, far)

        return projectionMatrix
from shaderProgram import ShaderProgramManager
import pygame as pg
import numpy as np
import glm
import os

shadersDirectory = "shaders"

class Cube :
    def __init__(self, app, pos=(0,0,0), rot=(0,0,0), textures=["test.png","test.png","test.png","test.png","test.png","test.png"]) -> None:
        self.faces = []

        self.faces.append({"object": Face(app, pos=(pos[0]+0.5, pos[1]+0, pos[2]+0), rot=(0,90,0), texture=textures[0]), "visible": True})     # +x
        self.faces.append({"object": Face(app, pos=(pos[0]-0.5, pos[1]+0, pos[2]+0), rot=(0,-90,0), texture=textures[1]), "visible": True})    # -x
        self.faces.append({"object": Face(app, pos=(pos[0]+0, pos[1]+0.5, pos[2]+0), rot=(-90,0,0), texture=textures[2]), "visible": True})    # +y
        self.faces.append({"object": Face(app, pos=(pos[0]+0, pos[1]-0.5, pos[2]+0), rot=(90,0,0), texture=textures[3]), "visible": True})     # -y
        self.faces.append({"object": Face(app, pos=(pos[0]+0, pos[1]+0, pos[2]+0.5), rot=(0,0,0), texture=textures[4]), "visible": True})      # +z
        self.faces.append({"object": Face(app, pos=(pos[0]+0, pos[1]+0, pos[2]-0.5), rot=(0,180,0), texture=textures[5]), "visible": True})    # -z
    
    def render(self) :
        for face in self.faces :
            if face["visible"] :
                face["object"].render()

class Billboard :
    def __init__(self, app, pos=(0,0,0), rot=(0,0,0), textures=["test.png","test.png"]) -> None:
        self.faces = []

        self.faces.append({"object": Face(app, pos=(pos[0], pos[1], pos[2]), rot=(0,45,0), texture=textures[0]), "visible": True})
        self.faces.append({"object": Face(app, pos=(pos[0], pos[1], pos[2]), rot=(0,-45,0), texture=textures[1]), "visible": True})
        self.faces.append({"object": Face(app, pos=(pos[0], pos[1], pos[2]), rot=(0,225,0), texture=textures[1]), "visible": True})
        self.faces.append({"object": Face(app, pos=(pos[0], pos[1], pos[2]), rot=(0,-225,0), texture=textures[1]), "visible": True})
    
    def render(self) :
        for face in self.faces :
            if face["visible"] :
                face["object"].render()

class Face :
    def __init__(self, app, pos=(0,0,0), rot=(0,0,0), texture="test.png") -> None:
        self.app = app
        self.ctx = app.ctx
        self.textureMan = app.textureMan
        self.vbo = self.getVbo()
        self.shaderProgram = app.shaderMan.getShaderProgram("default", texture)
        self.vao = self.getVao()

        self.pos = pos
        self.setRotation(rot)
        self.textureID = texture        

        self.modelM = self.getModelMatrix()
        self.onInit()
    
    def onInit(self) :
        #Texture
        texture = self.textureMan.getTexture(self.textureID)
        self.shaderProgram['u_texture_0'] = texture.glo
        texture.use(location=texture.glo)
    
        #Matrixes
        self.shaderProgram['m_proj'].write(self.app.camera.projM)
        self.shaderProgram['m_view'].write(self.app.camera.viewM)
        self.shaderProgram['m_model'].write(self.modelM)
    
    def update(self) :
        self.modelM = self.getModelMatrix()

        self.shaderProgram['m_model'].write(self.modelM)
        self.shaderProgram['m_view'].write(self.app.camera.viewM)

    def getModelMatrix(self) :
        modelMatrix = glm.mat4()

        #Translate
        modelMatrix = glm.translate(modelMatrix, self.pos)

        #Rotate
        modelMatrix = glm.rotate(modelMatrix, self.rot.x, glm.vec3(1, 0, 0))
        modelMatrix = glm.rotate(modelMatrix, self.rot.y, glm.vec3(0, 1, 0))
        modelMatrix = glm.rotate(modelMatrix, self.rot.z, glm.vec3(0, 0, 1))

        return modelMatrix

    def render(self) :
        self.update()
        self.vao.render()
    
    def destroy(self) :
        self.vbo.release()
        self.shaderProgram.release()
        self.vao.release()
    
    def getVao(self) :
        vao = self.ctx.vertex_array(self.shaderProgram, [(self.vbo, '2f 3f', 'in_texcoord_0', 'in_position')])
        return vao
    
    def getVertexData(self) :
        verticies = [ (-0.5, -0.5, 0), (0.5, -0.5, 0), (0.5, 0.5, 0), (-0.5, 0.5, 0) ]
        
        indices = [ (0, 1, 2), (2, 3, 0) ]
        
        vertexData = self.get_data(verticies, indices)

        textureCoords = [ (0, 0), (1, 0), (1, 1), (0, 1) ]
        textureCoordsIndices = [ (0, 1, 2), (2, 3, 0) ]
        
        textureCoordsData = self.get_data(textureCoords, textureCoordsIndices)

        vertexData = np.hstack([textureCoordsData, vertexData])

        return vertexData
    
    @staticmethod
    def get_data(verticies, indices) :
        data = [verticies[ind] for triangle in indices for ind in triangle]
        return np.array(data, dtype='f4')
    
    def getVbo(self) :
        vertexData = self.getVertexData()
        vbo = self.ctx.buffer(vertexData)

        return vbo

    def setRotation(self, rot) :
        self.rot = glm.vec3([glm.radians(a) for a in rot])
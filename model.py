import pygame as pg
import numpy as np
import glm
import os

shadersDirectory = "shaders"

class Cube :
    def __init__(self, app) -> None:
        self.app = app
        self.ctx = app.ctx
        self.vbo = self.getVbo()
        self.shaderProgram = self.getShaderProgram("default")
        self.vao = self.getVao()
        self.modelM = self.getModelMatrix()

        self.texture = self.getTexture(os.path.join("textures", "test.png"))

        self.onInit()
    
    def onInit(self) :
        #Texture
        self.shaderProgram['u_texture_0'] = 0
        self.texture.use()
    
        #Matrixes
        self.shaderProgram['m_proj'].write(self.app.camera.projM)
        self.shaderProgram['m_view'].write(self.app.camera.viewM)
        self.shaderProgram['m_model'].write(self.modelM)
    
    def update(self) :
        modelM = self.modelM
        modelM = glm.rotate(modelM, self.app.time, glm.vec3(0, 1, 0))
        self.shaderProgram['m_model'].write(modelM)
        self.shaderProgram['m_view'].write(self.app.camera.viewM)
    
    def getTexture(self, path) :
        texture = pg.image.load(path).convert()
        texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
        texture = self.ctx.texture(size=texture.get_size(), components=3, data=pg.image.tostring(texture, 'RGB'))

        return texture

    def getModelMatrix(self) :
        modelMatrix = glm.mat4()
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
        verticies = [ (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),
                      (-1, 1, -1), (-1, -1, -1), (1, -1, -1), (1, 1, -1) ]
        
        indices = [ (0, 2, 3), (0, 1, 2),
                    (1, 7, 2), (1, 6, 7),
                    (6, 5, 4), (4, 7, 6),
                    (3, 4, 5), (3, 5, 0),
                    (3, 7, 4), (3, 2, 7),
                    (0, 6, 1), (0, 5, 6) ]
        
        vertexData = self.get_data(verticies, indices)

        textureCoords = [ (0, 0), (1, 0), (1, 1), (0, 1) ]
        textureCoordsIndices = [ (0, 2, 3), (0, 1, 2),
                                 (0, 2, 3), (0, 1, 2),
                                 (0, 1, 2), (2, 3, 0),
                                 (2, 3, 0), (2, 0, 1),
                                 (0, 2, 3), (0, 1, 2),
                                 (3, 1, 2), (3, 0, 1) ]
        
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

    def getShaderProgram(self, shaderName) :
        with open(os.path.join(shadersDirectory, shaderName + ".vert")) as f :
            vertexShader = f.read()
        
        with open(os.path.join(shadersDirectory, shaderName + ".frag")) as f :
            fragmentShader = f.read()
        
        program = self.ctx.program(vertex_shader=vertexShader, fragment_shader=fragmentShader)
        return program
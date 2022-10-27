import os

class ShaderProgramManager :
    def __init__(self, app) -> None:
        self.app = app
        self.ctx = app.ctx
        self.textureMan = app.textureMan
        
        self.shaders = {}
    
    def getShaderProgram(self, name, textureID=None) :
        if (not name in self.shaders) or (not textureID in self.shaders[name]) :
            with open(os.path.join("shaders", name + ".vert")) as f :
                vertexShader = f.read()
            
            with open(os.path.join("shaders", name + ".frag")) as f :
                fragmentShader = f.read()
            
            program = self.ctx.program(vertex_shader=vertexShader, fragment_shader=fragmentShader)
            
            if not name in self.shaders :
                self.shaders[name] = {}

            self.shaders[name][textureID] = program

            if textureID :
                texture = self.textureMan.getTexture(textureID)
                program['u_texture_0'] = texture.glo
                texture.use(location=texture.glo)
            
            try :
                program['m_proj'].write(self.app.camera.projM)
                program['m_view'].write(self.app.camera.viewM)
            except KeyError :
                pass

        return self.shaders[name][textureID]
    
    def updateCamera(self) : #Used when updating camera FOV in menu
        for name in self.shaders :
            for shaderProgram in self.shaders[name].values() :
                try :
                    shaderProgram['m_proj'].write(self.app.camera.projM)
                    shaderProgram['m_view'].write(self.app.camera.viewM)
                except KeyError :
                    pass
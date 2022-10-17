import os

class ShaderProgramManager :
    def __init__(self, app) -> None:
        self.app = app
        self.ctx = app.ctx
        
        self.shaders = {}
    
    def getShaderProgram(self, name, textureID) :
        if (not name in self.shaders) or (not textureID in self.shaders[name]) :
            with open(os.path.join("shaders", name + ".vert")) as f :
                vertexShader = f.read()
            
            with open(os.path.join("shaders", name + ".frag")) as f :
                fragmentShader = f.read()
            
            program = self.ctx.program(vertex_shader=vertexShader, fragment_shader=fragmentShader)
            
            if not name in self.shaders :
                self.shaders[name] = {}

            self.shaders[name][textureID] = program
        
        return self.shaders[name][textureID]
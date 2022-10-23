import pygame as pg
import moderngl as mgl
import sys

from model import *
from player import Player
from saveManager import SaveManager
from scene import Scene
from config import Config
from ui import UserInterface
from camera import Camera
from textures import TextureManager
from shaderProgram import ShaderProgramManager

class Color :
    def __init__(self, rgb) -> None:
        self.r = rgb[0]
        self.g = rgb[1]
        self.b = rgb[2]
    
    def normalize(self) :
        return (self.r/255, self.g/255, self.b/255)

class GraphicsEngine :
    def __init__(self, windowSize=(1600, 900)) :
        pg.init()
        self.windowSize = windowSize

        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

        pg.display.set_mode(self.windowSize, flags=pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE)

        #Mouse lock
        pg.event.set_grab(True)
        pg.mouse.set_visible(False)

        #Detect and use existing OpenGL context
        self.ctx = mgl.create_context()
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)

        #Clock and time
        self.clock = pg.time.Clock()
        self.time = 0
        self.deltaTime = 0

        #Game info
        self.gamePaused = True
        self.inGame = False

        #Config
        self.config = Config(self)

        #Camera
        self.camera = Camera(self)

        #Texture and shader managers
        self.textureMan = TextureManager(self)
        self.shaderMan = ShaderProgramManager(self)

        #Save manager
        self.saveMan = SaveManager(self)

        #Scene
        self.scene = Scene(self)

        #User interface
        self.ui = UserInterface(self)
        self.pgEvents = []

        #Player
        self.player = Player(self)


    def quit(self) :
        self.scene.destroy()
        pg.quit()
        sys.exit(0)

    def check_events(self) :
        self.pgEvents = pg.event.get()

        for e in self.pgEvents :
            if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_BACKSPACE) :
                self.quit()
            if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE and self.inGame :
                self.gamePaused = not self.gamePaused
                self.ui.redrawNextFrame = True
            if e.type == pg.WINDOWSIZECHANGED :
                self.windowSize = (e.x, e.y)

                self.camera.aspectRatio = e.x / e.y
                self.ui.resize()
    
    def render(self) :
        #Clear framebuffer
        self.ctx.clear(color=((42/255, 42/255, 42/255)))

        #Render the UI and the scene
        self.scene.render()
        self.ui.render()

        #Swap buffers
        pg.display.flip()
    
    def getTime(self) :
        self.time = pg.time.get_ticks() / 1000
    
    def run(self) :
        self.render()
        
        while True :
            self.getTime()
            self.check_events()
            self.player.tick()
            self.camera.update()
            self.scene.tick()
            self.ui.tick()
            self.render()
            self.deltaTime = self.clock.tick(self.config.fpsLimit)

if __name__ == "__main__" :
    app = GraphicsEngine()
    app.run()
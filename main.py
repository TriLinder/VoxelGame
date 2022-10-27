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

        pg.display.set_caption("Voxel Engine | ??fps")
        pg.display.set_icon(self.textureMan.iconTexture)

        if self.config.fullscreen :
            pg.display.toggle_fullscreen()


    def quit(self) :
        self.scene.destroy()
        pg.quit()
        sys.exit(0)

    def checkEvents(self) :
        self.pgEvents = pg.event.get()

        for e in self.pgEvents :
            if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_DELETE) : #Quit the application
                self.quit()
            if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE and self.inGame : #Pause the game
                self.gamePaused = not self.gamePaused
                self.ui.redrawNextFrame = True
            if e.type == pg.KEYDOWN and e.key == pg.K_F11 : #Toggle fullscreen
                pg.display.toggle_fullscreen()
                self.ui.redrawInTicks = 2
                self.config.fullscreen = not self.config.fullscreen
                self.config.writeToFile()
            if e.type == pg.WINDOWSIZECHANGED : #Resize camera and UI
                self.windowSize = (e.x, e.y)

                self.camera.aspectRatio = e.x / e.y
                self.ui.resize()
    
    def updateWindowCaption(self) :
        fps = round(self.ui.app.clock.get_fps())
        pg.display.set_caption(f"Voxel Engine | {fps}fps")

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
            self.checkEvents()
            self.player.tick()
            self.camera.update()
            self.scene.tick()
            self.ui.tick()
            self.render()
            self.deltaTime = self.clock.tick(self.config.fpsLimit)
            self.updateWindowCaption()

if __name__ == "__main__" :
    app = GraphicsEngine()
    app.run()
import pygame as pg
import pygame_menu as pgm
import moderngl as mgl
from array import array
from moderngl_window import geometry, activate_context
import math
import os
import psutil

from menu import Menu

alwaysShowDebugElements = False

class UserInterface :
    def __init__(self, app) -> None:
        self.app = app
        self.ctx = app.ctx
        
        self.elements = []
        self.showDebugElements = False
        self.debugElementsLastFrame = False

        self.redrawNextFrame = True
        self.redrawInTicks = 2

        self.defaultFontName = pg.font.get_default_font()

        self.texture = None
        self.resize()

        self.pgmTheme = pgm.themes.THEME_DARK
        self.pgmTheme.set_background_color_opacity(0)

        activate_context(ctx=self.ctx)
        self.quadFs = geometry.quad_fs()

        self.textureProgram = self.app.shaderMan.getShaderProgram("ui")
        self.textureProgram['surface'] = 0

        buffer = self.ctx.buffer(
            data=array('f', [
                # Position (x, y) , Texture coordinates (x, y)
                -1.0, 1.0, 0.0, 1.0,  # upper left
                -1.0, -1.0, 0.0, 0.0,  # lower left
                1.0, 1.0, 1.0, 1.0,  # upper right
                1.0, -1.0, 1.0, 0.0,  # lower right
            ])
        )

        self.quadFs = self.ctx.vertex_array(
            self.textureProgram,
            [
                (
                    # The buffer containing the data
                    buffer,
                    # Format of the two attributes. 2 floats for position, 2 floats for texture coordinates
                    "2f 2f",
                    # Names of the attributes in the shader program
                    "in_vert", "in_texcoord",
                )
            ],
        )

        self.elements.append( Crosshair(self) )
        self.elements.append( DebugScreen(self) )
        self.elements.append( Menu(self) )
    
    def getPressed(self) : #Slow, but only used on the keybinds settings screen
        pressedKeysSequence = pg.key.get_pressed()
        pressedMBsSequence = pg.mouse.get_pressed(num_buttons=5)

        pressed = []

        for i in range(len(pressedMBsSequence)) : #Done this way because of pygame sequence weirdness
            pressed.append(pressedMBsSequence[i])

        for i in range(len(pressedKeysSequence)) :
            pressed.append(pressedKeysSequence[i])

        return pressed

    def isPressed(self, buttonId) :
        keyCode = self.app.config.keybinds[buttonId]

        if keyCode in range(0, 5) :
            return pg.mouse.get_pressed()[keyCode]
        else :
            keyCode -= 5
            return pg.key.get_pressed()[keyCode]

    def resize(self) :
        self.res = self.app.windowSize

        self.surface = pg.Surface(self.res, flags=pg.SRCALPHA)

        if self.texture :
            self.texture.release()

        self.texture = self.ctx.texture(self.res, 4)
        self.texture.filter = mgl.NEAREST, mgl.NEAREST
        self.texture.swizzle = 'BGRA'

        for element in self.elements :
            element.resize()
        
    def tick(self) :
        pg.event.set_grab(not self.app.gamePaused)
        pg.mouse.set_visible(self.app.gamePaused)

        if self.redrawInTicks > 0 :
            self.redrawInTicks -= 1

            if self.redrawInTicks == 0 :
                self.redrawNextFrame = True

        for element in self.elements :
            element.tick()

    def writeToTexture(self) :
        textureData = self.surface.get_view('1')
        self.texture.write(textureData)

    def render(self) :
        if self.redrawNextFrame :
            self.surface.fill((0, 0, 0, 0))

            if alwaysShowDebugElements :
                self.showDebugElements = True

            if not self.ctx.wireframe : #Hide UI when in wireframe mode
                for element in self.elements :
                    if element.visible and ((not element.isDebugElement) or (element.isDebugElement and self.showDebugElements)) and (element.showInMenu or (self.app.inGame)) :
                        element.render()

            self.writeToTexture()
            
            self.redrawNextFrame = False
        
        self.ctx.enable(mgl.BLEND)
        self.texture.use(location=0)
        self.quadFs.render(mode=mgl.TRIANGLE_STRIP)
        self.ctx.disable(mgl.BLEND)

        if not self.debugElementsLastFrame == self.showDebugElements :
            self.redrawNextFrame = True

        self.debugElementsLastFrame = self.showDebugElements
    
    def drawText(self, pos, font, string, color=(255,255,255), antialias=True, center=False) :
        textSurface = font.render(string, antialias, color)
        textRect = textSurface.get_rect()

        if not center :
            textRect.x, textRect.y = pos
        else :
            textRect.center = pos

        self.surface.blit(textSurface, textRect)


# -- IN GAME -- #

class Crosshair :
    def __init__(self, ui) -> None :
        self.ui = ui

        self.visible = True
        self.showInMenu = False
        self.isDebugElement = False

        self.color = (255, 255, 255, 200) #RGBA
        self.resize()

    def resize(self) :
        screenHeight = self.ui.res[0]
        self.vh = screenHeight / 10

        self.size = math.floor(self.vh / 22)
        self.width = math.floor(self.vh / 53)
    
    def tick(self) :
        self.visible = not self.ui.app.gamePaused

    def render(self) :
        centerX = math.floor(self.ui.res[0] / 2)
        centerY = math.floor(self.ui.res[1] / 2)
        
        lines = [
            [(centerX - self.size, centerY), (centerX + self.size, centerY)],
            [(centerX, centerY - self.size), (centerX, centerY + self.size)]
        ]

        for line in lines :
            pg.draw.line(self.ui.surface, self.color, line[0], line[1], self.width)

class DebugScreen :
    def __init__(self, ui) -> None :
        self.ui = ui

        self.visible = True
        self.showInMenu = False
        self.isDebugElement = True

        self.fontColor = (255, 255, 255, 255) #RGBA
        self.fontBackground = (0, 0, 0)

        self.lines = []

        self.resize()
    
    def resize(self) :
        screenHeight = self.ui.res[0]
        self.vh = screenHeight / 10

        self.fontSize = math.floor(self.vh / 5.3)
        self.font = pg.font.SysFont(self.ui.defaultFontName, self.fontSize, bold=True)

    def tick(self) :
        if self.visible and self.ui.showDebugElements :
            self.update()
            self.ui.redrawNextFrame = True

    def update(self) :
        self.lines = []

        playerEntity = self.ui.app.player
        playerPhysics = playerEntity.physics

        if playerEntity.lookingAt :
            block = playerEntity.lookingAt
            lookingAt = f"'{block.id}' at {block.pos}"
        else :
            lookingAt = None
        
        playerPos = playerEntity.position
        playerPos = (round(playerPos[0], 2), round(playerPos[1], 2), round(playerPos[2], 2))

        cameraRot = (round(playerEntity.camera.yaw, 2), round(playerEntity.camera.pitch, 2))

        memoryUsage = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2

        self.lines.append(f"FPS: {round(self.ui.app.clock.get_fps())}")
        self.lines.append(f"MEM: {round(memoryUsage)}MiB")
        self.lines.append("")
        self.lines.append(f"Pos: {playerPos}")
        self.lines.append(f"In chunk: {playerEntity.getChunk()}")
        self.lines.append(f"Rotation: {cameraRot}")
        self.lines.append(f"Selected block: {playerEntity.selectedBlockId}")
        self.lines.append(f"Looking at: {lookingAt}")
        self.lines.append(f"On ground: {playerEntity.onGround}")
        self.lines.append(f"In fluid: {playerPhysics.inFluid}")
        self.lines.append("")
        self.lines.append(f"Seed: {self.ui.app.scene.worldGen.seed}")

    def render(self) :
        y = self.fontSize / 3
        for line in self.lines :
            if not line == "" :
                self.ui.drawText((self.fontSize / 3, y), self.font, line, antialias=False)
            y += self.fontSize
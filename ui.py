import pygame as pg
import moderngl as mgl
from array import array
from moderngl_window import geometry, activate_context

class UserInterface :
    def __init__(self, app) -> None:
        self.app = app
        self.ctx = app.ctx

        self.res = self.app.windowSize
    
        self.surface = pg.Surface(self.res, flags=pg.SRCALPHA)

        self.texture = self.ctx.texture(self.res, 4)
        self.texture.filter = mgl.NEAREST, mgl.NEAREST
        self.texture.swizzle = 'BGRA'

        activate_context(ctx=self.ctx)
        self.quadFs = geometry.quad_fs()

        self.textureProgram = self.app.shaderMan.getShaderProgram("ui", "ui")
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


    def writeToTexture(self) :
        textureData = self.surface.get_view('1')
        self.texture.write(textureData)

    def render(self) :
        self.surface.fill((0, 0, 0, 0))

        pg.draw.rect(self.surface, (255, 0, 0), [0, 0, 100, 100])

        self.writeToTexture()
        
        self.ctx.enable(mgl.BLEND)
        self.texture.use(location=0)
        self.quadFs.render(mode=mgl.TRIANGLE_STRIP)
        self.ctx.disable(mgl.BLEND)

from physics import EntityPhysics

class Player :
    def __init__(self, app) -> None:
        self.app = app
        self.camera = app.camera
        self.scene = app.scene
        self.physics = EntityPhysics(app, self)
from chunk import Chunk

class Scene :
    def __init__(self, app) -> None :
        self.app = app
        self.objects = []

        self.chunk = Chunk(app)
    
    def render(self) :
        self.chunk.render()
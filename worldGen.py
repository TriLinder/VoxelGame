import time
from perlin_noise import PerlinNoise

class WorldGen :
    def __init__(self, seed=round(time.time())) -> None:
        self.seed = seed

        self.heightNoise = PerlinNoise(octaves=10, seed=seed)

    def getTerrainY(self, x, z, min, max) :
        n = self.heightNoise([x/100, z/100])
        return min + round(n * (max - min))
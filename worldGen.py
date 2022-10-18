import time
import random
from perlin_noise import PerlinNoise

class WorldGen :
    def __init__(self, seed=round(time.time())) -> None:
        self.seed = seed

        self.heightNoise = PerlinNoise(octaves=10, seed=seed)

    def seedFromCoords(self, x, z) :
        return self.seed * (x+z) * x * z + (self.seed/2)

    def getTerrainY(self, x, z, min, max) :
        n = self.heightNoise([x/100, z/100])
        return min + round(n * (max - min))
    
    def shouldHaveTree(self, x, z) :
        random.seed(self.seedFromCoords(x, z))

        if (not x%16 in range(3, 13)) or (not z%16 in range(3, 13)) :
            return False

        return random.randint(1, 100) > 99
    
    def generateTree(self, x, z) :
        random.seed(self.seedFromCoords(x, z))

        height = random.randint(4, 6)
        leavesToRemove = []

        for i in range(5*5) :
            leavesToRemove.append(bool(random.randint(0, 1)))

        return {"height": height, "leavesToRemove": leavesToRemove}
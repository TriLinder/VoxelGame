import time
import random
from perlin_noise import PerlinNoise

class WorldGen :
    def __init__(self, seed=round(time.time())) -> None:
        self.seed = self.stringToSeed(str(seed))

        self.heightNoise = PerlinNoise(octaves=10, seed=self.seed)

    def stringToSeed(self, string) :
        b = bytes(string, encoding="utf-8")
        seed = int.from_bytes(b, "big")
        seed = seed % (2**32) - 1

        return seed 

    def seedFromCoords(self, x, z) :
        return self.stringToSeed(f"{x}_{z}")

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
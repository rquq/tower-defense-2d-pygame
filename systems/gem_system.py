from enum import Enum, auto

class GemType(Enum):
    FIRE = auto()
    ICE = auto()
    OVERCLOCK = auto()

class Gem:
    def __init__(self, gem_type):
        self.type = gem_type
        self.name = gem_type.name
        self.colors = {
            GemType.FIRE: (255, 69, 0),
            GemType.ICE: (0, 191, 255),
            GemType.OVERCLOCK: (255, 215, 0)
        }
        self.color = self.colors[gem_type]

    def apply_modifier(self, tower):
        if self.type == GemType.FIRE:
            # Maybe add dot logic to tower? 
            # Better to apply it to the projectile
            pass
        elif self.type == GemType.OVERCLOCK:
            tower.fire_rate = int(tower.fire_rate * 0.7)

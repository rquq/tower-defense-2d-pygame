from enum import Enum, auto

class GemType(Enum):
    """
    Enumeration of available gem types.
    """
    FIRE = auto()
    ICE = auto()
    OVERCLOCK = auto()

class Gem:
    """
    Represents an elemental gem that can be slotted into towers.
    Modifies base stats and adds elemental properties.
    """
    def __init__(self, gem_type):
        """
        Initializes the Gem with a type and its associated visual color.
        
        Args:
            gem_type (GemType): The type of this gem.
        """
        self.type = gem_type
        self.name = gem_type.name
        self.colors = {
            GemType.FIRE: (255, 69, 0),
            GemType.ICE: (0, 191, 255),
            GemType.OVERCLOCK: (255, 215, 0)
        }
        self.color = self.colors[gem_type]

    def apply_modifier(self, tower):
        """
        Applies the specific stat modifications to the target tower.
        
        Args:
            tower (Tower): The tower receiving the modifiers.
        """
        if self.type == GemType.FIRE:
            pass
        elif self.type == GemType.OVERCLOCK:
            tower.fire_rate = int(tower.fire_rate * 0.7)

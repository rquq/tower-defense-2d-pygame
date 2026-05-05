import pygame
from core.constants import *
from systems.asset_manager import AssetManager

class Beacon:
    """
    Support structure placed on the grid.
    Emits beneficial stat buffs to adjacent towers.
    """
    def __init__(self, x, y, beacon_type):
        """
        Initializes the Beacon at a grid coordinate with specific stats.
        
        Args:
            x (int): X pixel coordinate.
            y (int): Y pixel coordinate.
            beacon_type (str): The type of the beacon determining its stats.
        """
        stats = BEACON_STATS[beacon_type]
        self.x = x
        self.y = y
        self.type = beacon_type
        self.buff_type = stats["buff_type"]
        self.buff_val = stats["buff_val"]
        self.color = stats["color"]
        self.desc = stats["desc"]
        self.gems = [] # Slots for STAT_CARDs
        
    def add_gem(self, item):
        """
        Attempts to insert a Stat Card into the beacon's upgrade slots.
        
        Args:
            item (InventoryItem): The upgrade card to slot.
            
        Returns:
            bool: True if slotting succeeded, False if full.
        """
        if len(self.gems) < 2 and item.item_type == ItemType.STAT_CARD:
            self.gems.append(item)
            return True
        return False

    def get_all_buffs(self):
        """
        Calculates the aggregate buffs provided by the beacon and slotted cards.
        
        Returns:
            dict: Key-value map of stat types and additive buff percentages.
        """
        # Base buff from beacon type
        buffs = {self.buff_type: self.buff_val}
        # Add card buffs (Balanced values: +15% for primary, +10% for crit)
        for card in self.gems:
            name = card.name
            if name == "STRENGTH CARD": buffs["ATK"] = buffs.get("ATK", 0) + 0.15
            elif name == "AGILITY CARD": buffs["SPD"] = buffs.get("SPD", 0) + 0.15
            elif name == "VISION CARD": buffs["RNG"] = buffs.get("RNG", 0) + 0.15
            elif name == "PRECISION CARD": buffs["CRIT"] = buffs.get("CRIT", 0) + 0.10
        return buffs

    def draw(self, surface):
        """
        Renders the diamond beacon graphic and its active modification sockets.
        
        Args:
            surface (pygame.Surface): The rendering destination.
        """
        x, y = int(self.x), int(self.y)
        points = [
            (x, y - 20), # Top
            (x + 20, y), # Right
            (x, y + 20), # Bottom
            (x - 20, y)  # Left
        ]
        
        # Base shadow
        pygame.draw.polygon(surface, (20, 20, 25), [(p[0]+4, p[1]+4) for p in points])
        
        # Main body
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, (255, 255, 255), points, 2) # Border
        
        # Core pulse (visual only)
        import math
        pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 5
        pygame.draw.circle(surface, (255, 255, 255, 150), (x, y), int(5 + pulse), 1)
        
        # Card Slots as visual indicators
        for i in range(2):
            if i < len(self.gems):
                slot_color = self.gems[i].color
                sx = x - 8 + (i * 16)
                sy = y + 25 # Below the diamond
                pygame.draw.circle(surface, slot_color, (sx, sy), 4)
                pygame.draw.circle(surface, (255, 255, 255), (sx, sy), 4, 1)

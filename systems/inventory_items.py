from core.constants import ItemType, BEACON_STATS

class InventoryItem:
    def __init__(self, item_type, data):
        self.item_type = item_type # ItemType enum
        self.data = data # Dictionary or String depending on type
        self.name = ""
        self.color = (200, 200, 200)
        self.description = []
        
        if item_type == ItemType.GEM:
            self.name = data # "FIRE", "ICE", etc
            colors = {"FIRE": (255, 69, 0), "ICE": (0, 191, 255), "OVERCLOCK": (255, 215, 0)}
            self.color = colors.get(data, (200, 200, 200))
            self.description = [f"{data} GEM", "Slots into turrets"]
            
        elif item_type == ItemType.BEACON:
            self.name = data # "ATK_Beacon", etc
            stats = BEACON_STATS[data]
            self.color = stats["color"]
            self.description = [data.replace("_", " "), stats["desc"], "Place on grid"]
            
        elif item_type == ItemType.STAT_CARD:
            self.name = data["name"] # "STRENGTH CARD", etc
            card_colors = {
                "STRENGTH CARD": (255, 80, 80),   # Vibrant Red
                "AGILITY CARD": (80, 255, 80),    # Vibrant Green
                "VISION CARD": (80, 150, 255),    # Vibrant Blue
                "PRECISION CARD": (255, 220, 80)  # Vibrant Gold
            }
            self.color = card_colors.get(self.name, (200, 100, 255))
            self.description = [self.name, data["desc"], "Fits Powerup Slot"]

    def get_tooltip_data(self, t):
        lines = [f"--- {t(self.name).upper()} ---"]
        
        if self.item_type == ItemType.BEACON:
            stats = BEACON_STATS[self.data]
            lines += [
                f"{t('DESCRIPTION')}: {t(stats['desc']).upper()}.",
                f"{t('USAGE')}: {t('BEACON_USAGE')}"
            ]
        elif self.item_type == ItemType.GEM:
            gem_descs = {
                "FIRE": "INFUSES BULLETS WITH SCORCHING ENERGY, ADDING +2 RAW ATK AND BURNING ENEMIES.",
                "ICE": "CHILLS ENEMIES ON HIT, REDUCING THEIR MOVEMENT SPEED BY 40%.",
                "OVERCLOCK": "FRANTICALLY OVERCLOCKS TURRET GEARS, INCREASING SPD BY 30%."
            }
            desc = gem_descs.get(self.data, "A MYSTERIOUS ELEMENTAL GEM.")
            lines += [
                f"{t('DESCRIPTION')}: {t(desc)}",
                f"{t('USAGE')}: {t('BUFF_USAGE')}"
            ]
        elif self.item_type == ItemType.STAT_CARD:
            lines += [
                f"{t('DESCRIPTION')}: {t(self.data['desc']).upper()}.",
                f"{t('USAGE')}: {t('BLESSING_USAGE')}"
            ]
        return lines

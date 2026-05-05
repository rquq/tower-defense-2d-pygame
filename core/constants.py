from enum import Enum, auto
import os
import sys

# Windows DPI Awareness
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

# External Assets
# External Assets
FONT_PATH = None

# HD Grid Consts
WIN_WIDTH = 1920
WIN_HEIGHT = 1080
GRID_COLS = 28
GRID_ROWS = 14
GRID_SIZE = 60 
FPS = 60 

# Layout with Separate UI Panes (Padding)
UI_HUD_HEIGHT = 60
UI_BOTTOM_HEIGHT = 156
OFFSET_X = (WIN_WIDTH - (GRID_COLS * GRID_SIZE)) // 2
available_h = WIN_HEIGHT - UI_HUD_HEIGHT - UI_BOTTOM_HEIGHT
OFFSET_Y = UI_HUD_HEIGHT + (available_h - (GRID_ROWS * GRID_SIZE)) // 2

# Colors (Bright Cartoony Fantasy Palette)
COLOR_BG = (90, 160, 60)       # Darker grass background margin
COLOR_UI_PANEL = (20, 50, 30)  # Lush green for UI borders
COLOR_UI_TEXT = (200, 240, 210) # Light minty text
COLOR_ENEMY = (200, 50, 50)
COLOR_PATH = (240, 210, 150)   # Sandy dirt path
COLOR_GRID = (130, 200, 80)    # Bright vibrant grass
COLOR_ACCENT = (250, 200, 50)  # Bright gold
COLOR_VALID = (50, 255, 50, 150)
COLOR_INVALID = (255, 50, 50, 150)

# Binary Survival
BASE_HEALTH = 1

def get_pixel_pos(col, row):
    """
    Docstring for def get_pixel_pos.
    """
    return (col * GRID_SIZE + OFFSET_X + GRID_SIZE // 2, 
            row * GRID_SIZE + OFFSET_Y + GRID_SIZE // 2)

# Scaling
# Scaling
BASE_ENEMY_HP = 25
HP_SCALING = 1.15 # Increased difficulty scaling
ENEMY_SPEED_SCALING = 1.01
ENEMY_SPAWN_INTERVAL = 900
BLESSING_INTERVAL = 2

# Tower Types & Default Stats (Elemental Cannons)
TOWER_STATS = {
    "Earth Cannon": {"range": 180, "fire_rate": 35, "damage": 5, "color": (60, 120, 50), "cost": 50, "bullet_speed": 12, "crit_chance": 0.1, "crit_mult": 1.5, "aoe": 0, "desc": "Standard stone cannon."},
    "Wind Ballista": {"range": 550, "fire_rate": 120, "damage": 25, "color": (150, 255, 150), "cost": 100, "bullet_speed": 28, "crit_chance": 0.3, "crit_mult": 1.5, "aoe": 0, "desc": "Long-range piercing ballista."},
    "Fire Mortar": {"range": 160, "fire_rate": 75, "damage": 15, "color": (255, 100, 30), "cost": 150, "bullet_speed": 8, "aoe": 90, "crit_chance": 0.05, "crit_mult": 1.5, "desc": "Fiery AoE explosions."},
    "Storm Spire": {"range": 140, "fire_rate": 45, "damage": 2, "color": (200, 200, 50), "cost": 200, "bullet_speed": 40, "crit_chance": 0.1, "crit_mult": 1.5, "aoe": 0, "desc": "Chain lightning strikes."},
    "Frost Cannon": {"range": 200, "fire_rate": 65, "damage": 4, "color": (150, 200, 255), "cost": 175, "bullet_speed": 12, "slow": 0.5, "crit_chance": 0, "crit_mult": 1.5, "aoe": 0, "desc": "Freezing ice cannon."}
}

ENEMY_TYPES = {
    "Slime": {"hp": 1.0, "speed": 3.0, "color": (50, 200, 50), "gold": 12, "min_wave": 1},
    "Wolf": {"hp": 0.6, "speed": 4.5, "color": (120, 120, 130), "gold": 18, "min_wave": 3},
    "Golem": {"hp": 3.0, "speed": 1.5, "color": (100, 150, 90), "gold": 35, "min_wave": 5, "def": 2},
    "Orc": {"hp": 0.3, "speed": 5.5, "color": (50, 150, 50), "gold": 10, "min_wave": 7},
    "Monster": {"hp": 6.5, "speed": 2.5, "color": (200, 50, 200), "gold": 80, "min_wave": 10, "def": 3},
    "Dragon": {"hp": 1.2, "speed": 6.0, "color": (250, 50, 50), "gold": 60, "min_wave": 12, "def": 0}
}

class GameState(Enum):
    """
    Docstring for class GameState.
    """
    MENU = auto()
    PLAYING = auto()
    POWERUP = auto()
    GAME_OVER = auto()

class ItemType(Enum):
    """
    Docstring for class ItemType.
    """
    GEM = auto()
    BEACON = auto()
    STAT_CARD = auto()

BEACON_STATS = {
    "ATTACK BEACON": {"color": (255, 0, 80), "buff_type": "ATK", "buff_val": 0.25, "desc": "Boosts adjacent dmg by 25%"},
    "SPEED BEACON": {"color": (50, 255, 50), "buff_type": "SPD", "buff_val": 0.25, "desc": "Boosts adjacent speed by 25%"},
    "RANGE BEACON": {"color": (0, 150, 255), "buff_type": "RNG", "buff_val": 0.25, "desc": "Boosts adjacent range by 25%"}
}

POWERUP_TYPES = ["BEACON", "CARD", "GLOBAL"]

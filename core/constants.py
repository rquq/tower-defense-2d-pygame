from enum import Enum, auto
import os
import sys

if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

class Config:
    """Lớp cấu trúc cấu hình trung tâm, mô phỏng theo layout của Engine.
    
    Lớp này chứa các trạng thái (Enums) và tất cả hằng số hệ thống được khởi tạo
    trong __init__, giúp quản lý tài nguyên tập trung và nhất quán.
    """
    
    class GameState(Enum):
        """Các trạng thái chính của vòng lặp trò chơi."""
        MENU = auto()
        PLAYING = auto()
        POWERUP = auto()
        GAME_OVER = auto()

    class ItemType(Enum):
        """Các loại vật phẩm trong hệ thống kho đồ."""
        GEM = auto()
        BEACON = auto()
        STAT_CARD = auto()

    def __init__(self):
        # Cấu hình cửa sổ
        self.WIN_WIDTH = 1920
        self.WIN_HEIGHT = 1080
        self.FPS = 60
        
        # Cấu hình lưới (Grid)
        self.GRID_COLS = 28
        self.GRID_ROWS = 14
        self.GRID_SIZE = 60
        
        # Cấu hình giao diện (UI)
        self.UI_HUD_HEIGHT = 60
        self.UI_BOTTOM_HEIGHT = 156
        
        # Các giá trị tính toán (Offset)
        self.OFFSET_X = (self.WIN_WIDTH - self.GRID_COLS * self.GRID_SIZE) // 2
        self.AVAILABLE_H = self.WIN_HEIGHT - self.UI_HUD_HEIGHT - self.UI_BOTTOM_HEIGHT
        self.OFFSET_Y = self.UI_HUD_HEIGHT + (self.AVAILABLE_H - self.GRID_ROWS * self.GRID_SIZE) // 2
        
        # Bảng màu
        self.COLOR_BG = (90, 160, 60)
        self.COLOR_UI_PANEL = (20, 50, 30)
        self.COLOR_UI_TEXT = (200, 240, 210)
        self.COLOR_ENEMY = (200, 50, 50)
        self.COLOR_PATH = (240, 210, 150)
        self.COLOR_GRID = (130, 200, 80)
        self.COLOR_ACCENT = (250, 200, 50)
        self.COLOR_VALID = (50, 255, 50, 150)
        self.COLOR_INVALID = (255, 50, 50, 150)
        
        # Cấu hình gameplay
        self.BASE_HEALTH = 1
        self.BASE_ENEMY_HP = 25
        self.HP_SCALING = 1.15
        self.ENEMY_SPEED_SCALING = 1.01
        self.ENEMY_SPAWN_INTERVAL = 900
        self.BLESSING_INTERVAL = 2
        
        # Dữ liệu thực thể
        self.TOWER_STATS = {
            'Earth Cannon': {'range': 180, 'fire_rate': 35, 'damage': 5, 'color': (60, 120, 50), 'cost': 50, 'bullet_speed': 12, 'crit_chance': 0.1, 'crit_mult': 1.5, 'aoe': 0, 'desc': 'Standard stone cannon.'},
            'Wind Ballista': {'range': 550, 'fire_rate': 120, 'damage': 25, 'color': (150, 255, 150), 'cost': 100, 'bullet_speed': 28, 'crit_chance': 0.3, 'crit_mult': 1.5, 'aoe': 0, 'desc': 'Long-range piercing ballista.'},
            'Fire Mortar': {'range': 160, 'fire_rate': 75, 'damage': 15, 'color': (255, 100, 30), 'cost': 150, 'bullet_speed': 8, 'aoe': 90, 'crit_chance': 0.05, 'crit_mult': 1.5, 'desc': 'Fiery AoE explosions.'},
            'Storm Spire': {'range': 140, 'fire_rate': 45, 'damage': 2, 'color': (200, 200, 50), 'cost': 200, 'bullet_speed': 40, 'crit_chance': 0.1, 'crit_mult': 1.5, 'aoe': 0, 'desc': 'Chain lightning strikes.'},
            'Frost Cannon': {'range': 200, 'fire_rate': 65, 'damage': 4, 'color': (150, 200, 255), 'cost': 175, 'bullet_speed': 12, 'slow': 0.5, 'crit_chance': 0, 'crit_mult': 1.5, 'aoe': 0, 'desc': 'Freezing ice cannon.'}
        }
        
        self.ENEMY_TYPES = {
            'Slime': {'hp': 1.0, 'speed': 3.0, 'color': (50, 200, 50), 'gold': 12, 'min_wave': 1},
            'Wolf': {'hp': 0.6, 'speed': 4.5, 'color': (120, 120, 130), 'gold': 18, 'min_wave': 3},
            'Golem': {'hp': 3.0, 'speed': 1.5, 'color': (100, 150, 90), 'gold': 35, 'min_wave': 5, 'def': 2},
            'Orc': {'hp': 0.3, 'speed': 5.5, 'color': (50, 150, 50), 'gold': 10, 'min_wave': 7},
            'Monster': {'hp': 6.5, 'speed': 2.5, 'color': (200, 50, 200), 'gold': 80, 'min_wave': 10, 'def': 3},
            'Dragon': {'hp': 1.2, 'speed': 6.0, 'color': (250, 50, 50), 'gold': 60, 'min_wave': 12, 'def': 0}
        }
        
        self.BEACON_STATS = {
            'ATTACK BEACON': {'color': (255, 0, 80), 'buff_type': 'ATK', 'buff_val': 0.25, 'desc': 'Boosts adjacent dmg by 25%'},
            'SPEED BEACON': {'color': (50, 255, 50), 'buff_type': 'SPD', 'buff_val': 0.25, 'desc': 'Boosts adjacent speed by 25%'},
            'RANGE BEACON': {'color': (0, 150, 255), 'buff_type': 'RNG', 'buff_val': 0.25, 'desc': 'Boosts adjacent range by 25%'}
        }
        
        self.POWERUP_TYPES = ['BEACON', 'CARD', 'GLOBAL']
        self.FONT_PATH = None

    def get_pixel_pos(self, col, row):
        """Chuyển đổi tọa độ ô trên lưới thành tọa độ pixel thực tế trên màn hình."""
        return (col * self.GRID_SIZE + self.OFFSET_X + self.GRID_SIZE // 2, 
                row * self.GRID_SIZE + self.OFFSET_Y + self.GRID_SIZE // 2)

# Đối tượng duy nhất cung cấp truy cập toàn cục
C = Config()
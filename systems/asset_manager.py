import pygame
import os

class AssetManager:
    """Hệ thống quản lý tập trung các tài nguyên hình ảnh và âm thanh của trò chơi."""
    _instance = None

    def __init__(self):
        """Khởi tạo các cấu trúc dữ liệu để lưu trữ tài nguyên."""
        self.towers = {}
        self.enemies = {}
        self.env = {}
        self.sounds = {}
        self.beacons = {}
        self.icons = {}
        self.initialized = False

    @classmethod
    def get_instance(cls):
        """Lấy đối tượng quản lý tài nguyên duy nhất trong hệ thống."""
        if cls._instance is None:
            cls._instance = AssetManager()
        return cls._instance

    def init(self):
        """Thực hiện việc nạp thực tế các tệp tin tài nguyên từ bộ nhớ ngoài."""
        if self.initialized:
            return
        self.initialized = True
        tex_dir = os.path.join('assets', 'textures')
        if os.path.exists(tex_dir):
            try:
                enemy_files = {'Slime': 'green_slime.png', 'Wolf': 'wolf.png', 'Golem': 'stone_golem.png', 'Orc': 'green_orc.png', 'Monster': 'tree_monster.png', 'Dragon': 'dragon.png'}
                for name, filename in enemy_files.items():
                    path = os.path.join(tex_dir, filename)
                    if os.path.exists(path):
                        self.enemies[name] = pygame.image.load(path).convert_alpha()
                env_files = {'Cave': 'cave.png', 'Castle': 'castle.png', 'medium_tree': 'medium_tree.png', 'small_tree': 'small_tree.png', 'small_small_tree': 'small_small_tree.png', 'flower': 'a flower.png', 'grass_bunch_1': 'grass_bunch_1.png', 'leaves_bush': 'leaves_bush.png'}
                for name, filename in env_files.items():
                    path = os.path.join(tex_dir, filename)
                    if os.path.exists(path):
                        self.env[name] = pygame.image.load(path).convert_alpha()
                icon_files = {'GEM_FIRE': 'red_gem.png', 'GEM_ICE': 'blue_gem.png', 'GEM_OVERCLOCK': 'orange_gem.png', 'CARD_STRENGTH': 'red_book.png', 'CARD_AGILITY': 'green_book.png', 'CARD_VISION': 'blue_book.png', 'CARD_PRECISION': 'yellow_book.png', 'FRAME': 'empty_frame.png'}
                for name, filename in icon_files.items():
                    path = os.path.join(tex_dir, filename)
                    if os.path.exists(path):
                        self.icons[name] = pygame.image.load(path).convert_alpha()
            except Exception as e:
                print('Failed to load textures:', e)
        sound_dir = os.path.join('assets', 'sounds')
        if os.path.exists(sound_dir):
            for file in os.listdir(sound_dir):
                if file.endswith('.wav'):
                    try:
                        name = file.replace('.wav', '')
                        self.sounds[name] = pygame.mixer.Sound(os.path.join(sound_dir, file))
                        self.sounds[name].set_volume(0.3)
                    except Exception as e:
                        print(f'Failed to load sound {file}: {e}')

    def play_sound(self, name):
        """Phát một hiệu ứng âm thanh cụ thể."""
        if name in self.sounds:
            self.sounds[name].play()
import pygame
import os

class AssetManager:
    _instance = None

    def __init__(self):
        self.towers = {}
        self.enemies = {}
        self.env = {}
        self.sounds = {}
        self.beacons = {}
        self.icons = {}
        self.initialized = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = AssetManager()
        return cls._instance

    def init(self):
        if self.initialized: return
        self.initialized = True
        
        try:
            self.towers = {}
            self.enemies = {}
            self.beacons = {}
            self.icons = {}
            self.env = {}

        except Exception as e:
            print("Failed to load or slice assets:", e)

            
        # Load Sounds
        sound_dir = os.path.join("assets", "sounds")
        if os.path.exists(sound_dir):
            for file in os.listdir(sound_dir):
                if file.endswith('.wav'):
                    try:
                        name = file.replace('.wav', '')
                        self.sounds[name] = pygame.mixer.Sound(os.path.join(sound_dir, file))
                        self.sounds[name].set_volume(0.3) # Global volume down for 8-bit sounds
                    except Exception as e:
                        print(f"Failed to load sound {file}: {e}")

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def _extract_sprites(self, path, expected_count):
        if not os.path.exists(path): return []
        
        img = pygame.image.load(path).convert_alpha()
        width, height = img.get_size()
        
        # We need to consider "white" as the transparent background.
        # But image gen might have slightly off-white pixels (e.g. 250, 250, 250).
        # Let's manually scan the image and set near-white to alpha 0
        img.lock()
        for x in range(width):
            for y in range(height):
                r, g, b, a = img.get_at((x, y))
                if r > 240 and g > 240 and b > 240:
                    img.set_at((x, y), (0, 0, 0, 0)) # Make it transparent
        img.unlock()

        # Simple division strategy based on expected_count
        # AI gens usually space them reasonably well horizontally
        section_width = width // expected_count
        sprites = []
        for i in range(expected_count):
            rect = pygame.Rect(i * section_width, 0, section_width, height)
            sub = img.subsurface(rect).copy()
            
            # Find the actual bounding box inside the sub-region
            bbox = sub.get_bounding_rect()
            if bbox.width > 0 and bbox.height > 0:
                final_sprite = sub.subsurface(bbox).copy()
                sprites.append(final_sprite)
            else:
                sprites.append(sub)
        
        return sprites

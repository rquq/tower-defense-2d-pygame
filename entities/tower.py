import pygame
import math
from core.constants import *
from entities.projectile import Projectile
from systems.gem_system import GemType
from systems.asset_manager import AssetManager

class Tower:
    """
    Core defensive structures designed to secure boundaries securely.
    """
    def __init__(self, x, y, tower_type):
        """
        Initializes individual firing modules.
        """
        stats = TOWER_STATS[tower_type]
        self.x = x
        self.y = y
        self.type = tower_type
        
        self.base_range = stats["range"]
        self.base_fire_rate = stats["fire_rate"]
        self.base_damage = stats["damage"]
        self.bullet_speed = stats["bullet_speed"]
        self.aoe = stats.get("aoe", 0)
        
        self.range = self.base_range
        self.fire_rate = self.base_fire_rate
        self.damage = self.base_damage
        
        self.color = stats["color"]
        self.crit_chance = stats.get("crit_chance", 0)
        self.crit_mult = stats.get("crit_mult", 1.5)
        
        self.cooldown = 0
        self.target = None
        self.projectiles = []
        self.target_mode = "FIRST"
        self.angle = 0
        
        self.gems = []
        self.fire_mod = False
        self.ice_mod = False

    def add_gem(self, item):
        """
        Appends functional enhancements.
        """
        if len(self.gems) < 2:
            self.gems.append(item)
            if item.item_type == ItemType.GEM:
                if item.name == "FIRE": self.fire_mod = True
                if item.name == "ICE": self.ice_mod = True
            self.recalculate()
            return True
        return False

    def recalculate(self, adjacency_buffs=[]):
        """
        Updates localized stat summaries.
        """
        self.range = self.base_range
        self.fire_rate = self.base_fire_rate
        self.damage = self.base_damage
        self.crit_chance = TOWER_STATS[self.type].get("crit_chance", 0)
        
        for item in self.gems:
            if item.item_type == ItemType.GEM:
                if item.name == "OVERCLOCK": self.fire_rate = int(self.fire_rate * 0.7)
                if item.name == "FIRE": self.damage += 2

        dmg_m, spd_m, rng_m = 1.0, 1.0, 1.0
        for stat, val in adjacency_buffs:
            if stat == "damage": dmg_m += val
            elif stat == "fire_rate": spd_m += val
            elif stat == "range": rng_m += val
            elif stat == "crit": self.crit_chance += val
            
        self.damage = int(self.damage * dmg_m)
        self.fire_rate = max(5, int(self.fire_rate / spd_m))
        self.range = int(self.range * rng_m)

    def update(self, spatial_manager, vfx_manager):
        """
        Maintains targeting ranges continually.
        """
        if self.cooldown > 0: self.cooldown -= 1
        self.target = self.find_target(spatial_manager)
        if self.target:
            self.angle = math.atan2(self.target.y - self.y, self.target.x - self.x)
            if self.cooldown <= 0:
                self.fire()
                self.cooldown = self.fire_rate
        
        for proj in self.projectiles[:]:
            proj.update(spatial_manager, vfx_manager)
            if proj.is_dead: self.projectiles.remove(proj)

    def find_target(self, spatial_manager):
        """
        Locates threats effectively.
        """
        in_range = spatial_manager.get_nearby_entities(self.x, self.y, self.range)
        if not in_range: return None
        
        if self.target_mode == "FIRST": 
            return max(in_range, key=lambda e: e.target_waypoint_idx)
        elif self.target_mode == "STRONGEST": 
            return max(in_range, key=lambda e: e.health)
        elif self.target_mode == "CLOSEST": 
            return min(in_range, key=lambda e: (e.x - self.x)**2 + (e.y - self.y)**2)
        return in_range[0]

    def fire(self):
        """
        Launches lethal payload protocols.
        """
        final_dmg = self.damage
        is_crit = False
        import random
        if random.random() < self.crit_chance:
            final_dmg *= self.crit_mult
            is_crit = True
            
        f_mod = self.fire_mod or (self.type == "Fire Mortar")
        i_mod = self.ice_mod or (self.type == "Frost Cannon")
        new_proj = Projectile(self.x, self.y, self.target, final_dmg, self.bullet_speed, self.color, self.color, self.aoe, 
                                fire_mod=f_mod, ice_mod=i_mod)
        if is_crit: new_proj.color = (255, 255, 255)
        elif self.fire_mod: new_proj.color = (255, 120, 0)
        elif self.ice_mod: new_proj.color = (150, 255, 255)
        
        self.projectiles.append(new_proj)
        
        sounds = {
            "Earth Cannon": "shoot_cannon",
            "Wind Ballista": "shoot_arrow",
            "Fire Mortar": "shoot_fire",
            "Storm Spire": "shoot_lightning",
            "Frost Cannon": "shoot_ice"
        }
        if self.type in sounds:
            AssetManager.get_instance().play_sound(sounds[self.type])

    @classmethod
    def draw_design(cls, surface, cx, cy, type_name, color, angle, scale=1.0, is_shadow=False):
        """
        Processes graphical aesthetics.
        """
        R = int(14 * scale)
        base_c = (20, 20, 30, 100) if is_shadow else (90, 90, 100)
        line_c = (20, 20, 30, 100) if is_shadow else (60, 60, 70)
        top_c = (20, 20, 30, 100) if is_shadow else color
        
        if is_shadow:
            pygame.draw.rect(surface, (20, 20, 30, 120), (cx-R+4, cy-R+4, R*2, R*2), border_radius=2)
        else:
            pygame.draw.rect(surface, base_c, (cx-R, cy-R, R*2, R*2))
            pygame.draw.rect(surface, line_c, (cx-R, cy-R, R*2, R*2), 1)

        off = 4 if is_shadow else 0
        bx = cx + math.cos(angle) * int(18 * scale) + off
        by = cy + math.sin(angle) * int(18 * scale) + off
        
        if type_name == "Earth Cannon":
            pygame.draw.line(surface, top_c, (cx+off, cy+off), (bx, by), max(3, int(6*scale)))
        elif type_name == "Wind Ballista":
            pygame.draw.line(surface, color, (cx, cy), (bx, by), 2)
            pygame.draw.line(surface, color, (cx-int(8*scale), cy), (cx+int(8*scale), cy), 2)
        elif type_name == "Fire Mortar":
            pygame.draw.circle(surface, color, (cx, cy), int(10*scale))
        elif type_name == "Storm Spire":
            pts = [(cx, cy-int(12*scale)), (cx+int(8*scale), cy+int(6*scale)), (cx-int(8*scale), cy+int(6*scale))]
            pygame.draw.polygon(surface, color, pts)
        elif type_name == "Frost Cannon":
            p2x = cx + math.cos(angle + 0.3) * int(15 * scale)
            p2y = cy + math.sin(angle + 0.3) * int(15 * scale)
            pygame.draw.line(surface, color, (cx, cy), (bx, by), 2)
            pygame.draw.line(surface, color, (cx, cy), (p2x, p2y), 2)
        else:
            pygame.draw.line(surface, color, (cx, cy), (bx, by), 2)

    def draw(self, surface):
        """
        Draws basic modules properly.
        """
        cx, cy = int(self.x), int(self.y)
        Tower.draw_design(surface, cx, cy, self.type, self.color, self.angle)
        
        for i in range(2):
            if i < len(self.gems):
                slot_color = self.gems[i].color
                sx = cx - 8 + (i * 16)
                sy = cy + 8
                pygame.draw.circle(surface, slot_color, (sx, sy), 4)
                pygame.draw.circle(surface, (255, 255, 255), (sx, sy), 4, 1)
                
        for proj in self.projectiles: proj.draw(surface)

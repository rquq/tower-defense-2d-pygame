import pygame
import math
from core.constants import *
from systems.asset_manager import AssetManager

class Projectile:
    def __init__(self, x, y, target, damage, speed, color, tip_color, aoe=0, fire_mod=False, ice_mod=False):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = speed
        self.color = color # This is the trail/effect color
        self.tip_color = tip_color # This is the consistent arrow head color
        self.aoe = aoe
        self.fire_mod = fire_mod
        self.ice_mod = ice_mod
        self.is_dead = False
        self.history = [(x, y)]

    def update(self, spatial_manager, vfx_manager):
        if self.target and not self.target.is_dead:
            # Move towards target
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            dist_sq = dx**2 + dy**2
            
            if dist_sq <= self.speed**2:
                self.hit(spatial_manager, vfx_manager)
            else:
                dist = math.sqrt(dist_sq)
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
                self.history.append((self.x, self.y))
                if len(self.history) > 6:
                    self.history.pop(0)
        else:
            self.is_dead = True

    def hit(self, spatial_manager, vfx_manager):
        targets = []
        if self.aoe > 0:
            targets = spatial_manager.get_nearby_entities(self.x, self.y, self.aoe)
        elif not self.target.is_dead:
            targets.append(self.target)

        if targets:
            AssetManager.get_instance().play_sound("enemy_hit")

        for e in targets:
            dmg = self.damage + (2 if self.fire_mod else 0)
            actual_dmg = max(1, dmg - getattr(e, 'defense', 0))
            is_crit = (self.color == (255, 255, 255))
            
            e.health -= actual_dmg
            
            # VFX Feedback
            vfx_manager.create_floating_text(e.x, e.y - 20, str(int(actual_dmg)), (255, 255, 0) if is_crit else (200, 255, 255), is_crit=is_crit)
            
            if self.ice_mod:
                # Stronger Frost Slow (70% reduction)
                if not hasattr(e, '_original_speed'):
                    e._original_speed = e.speed
                e.speed = e._original_speed * 0.3 # 70% slow
                e._slow_timer = 180 # 3 seconds
            
            if self.fire_mod:
                # Apply Burn (Damage over time)
                e._burn_timer = 180 # 3 seconds
                e._burn_tick = 30 # Every 0.5s
                e._burn_dmg = 2
        self.is_dead = True

    def draw(self, surface):
        if len(self.history) > 1:
            # Draw pixelated colored trail
            for i, (hx, hy) in enumerate(self.history[:-1]):
                size = max(1, int(6 * (i + 1) / len(self.history)))
                trail_rect = pygame.Rect(int(hx - size/2), int(hy - size/2), size, size)
                # Trail uses effect color (Fire/Ice/Crit)
                pygame.draw.rect(surface, self.color, trail_rect)
                
            px, py = self.history[-2]
            cx, cy = self.history[-1]
            dx, dy = cx - px, cy - py
            dist = math.hypot(dx, dy)
            if dist > 0:
                angle = math.degrees(math.atan2(-dy, dx))
                
                # Create a simple 16x8 pixelated arrow surface
                arr_surf = pygame.Surface((16, 8), pygame.SRCALPHA)
                
                # Shaft (consistent dark brown)
                pygame.draw.rect(arr_surf, (80, 50, 30), (2, 3, 10, 2))
                
                # Fletching (consistent white)
                pygame.draw.rect(arr_surf, (240, 240, 240), (0, 1, 3, 2))
                pygame.draw.rect(arr_surf, (240, 240, 240), (0, 5, 3, 2))
                
                # Tip (Consistent Tower Color)
                pygame.draw.rect(arr_surf, self.tip_color, (12, 2, 4, 4))
                pygame.draw.rect(arr_surf, self.tip_color, (14, 1, 2, 6))
                
                # Rotate and blit
                rotated_arr = pygame.transform.rotate(arr_surf, angle)
                rect = rotated_arr.get_rect(center=(cx, cy))
                surface.blit(rotated_arr, rect)
        else:
            # Fallback for very short distance
            pygame.draw.rect(surface, self.tip_color, (int(self.x)-3, int(self.y)-3, 6, 6))

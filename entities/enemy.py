import pygame
import random
from core.constants import *
from systems.asset_manager import AssetManager
import math

class Enemy:
    """
    Hostile entity executing path waypoints towards player base.
    """
    def __init__(self, waypoints, type_name, hp_mult=1.0, speed_mult=1.0):
        """
        Sets core properties and initial entry vector.
        """
        self.waypoints = waypoints
        self.target_waypoint_idx = 0
        
        stats = ENEMY_TYPES[type_name]
        self.type_name = type_name
        self.max_health = stats["hp"] * BASE_ENEMY_HP * hp_mult
        self.health = self.max_health
        self.speed = stats["speed"] * 1.0 * speed_mult
        self.color = stats["color"]
        self.reward = stats["gold"]
        self.defense = stats.get("def", 0)
        
        self.x, self.y = list(self.waypoints[0])
        self.is_dead = False
        self.reached_end = False
        self.anim_timer = random.randint(0, 100)
        self.rotation = 0

    def update(self):
        """
        Moves through waypoint coordinates per frame.
        """
        if hasattr(self, '_slow_timer') and self._slow_timer > 0:
            self._slow_timer -= 1
            if self._slow_timer <= 0:
                self.speed = getattr(self, '_original_speed', self.speed)
                
        if hasattr(self, '_burn_timer') and self._burn_timer > 0:
            self._burn_timer -= 1
            if self._burn_timer % getattr(self, '_burn_tick', 30) == 0:
                self.health -= getattr(self, '_burn_dmg', 1)

        if self.target_waypoint_idx < len(self.waypoints):
            target_x, target_y = self.waypoints[self.target_waypoint_idx]
            
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.hypot(dx, dy)
            
            if dist <= self.speed:
                self.x, self.y = target_x, target_y
                self.target_waypoint_idx += 1
                if self.target_waypoint_idx >= len(self.waypoints):
                    self.reached_end = True
            else:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
        
        self.anim_timer += 1
        self.rotation += 0.1
        
        if self.health <= 0:
            self.is_dead = True

    def draw(self, surface):
        """
        Draws current frame state with optional visual effects.
        """
        cx, cy = int(self.x), int(self.y)
        t = self.anim_timer
        
        base_color = self.color
        if hasattr(self, '_slow_timer') and self._slow_timer > 0:
            base_color = (min(255, base_color[0]+30), min(255, base_color[1]+100), min(255, base_color[2]+155))
        elif hasattr(self, '_burn_timer') and self._burn_timer > 0:
            base_color = (min(255, base_color[0]+155), min(255, base_color[1]+50), base_color[2])
            
        dark_color = (max(0, base_color[0]-100), max(0, base_color[1]-100), max(0, base_color[2]-100))
        fly_y = cy + math.sin(t * 0.1) * 2
        
        asset = AssetManager.get_instance().enemies.get(self.type_name)
        if asset:
            t_width, t_height = asset.get_size()
            target_h = GRID_SIZE
            target_w = int((t_width / t_height) * target_h)
            if target_w > GRID_SIZE:
                target_w = GRID_SIZE
                target_h = int((t_height / t_width) * target_w)
            
            scaled_asset = pygame.transform.scale(asset, (target_w, target_h))
            surface.blit(scaled_asset, (cx - target_w//2, int(fly_y) - target_h//2))
            
            if self.health < self.max_health:
                bar_w = 30
                fill_w = int(bar_w * (self.health / self.max_health))
                hx, hy = cx - 15, cy - 35
                pygame.draw.rect(surface, (40, 20, 20), (hx, hy, bar_w, 4))
                pygame.draw.rect(surface, (50, 255, 50), (hx, hy, fill_w, 4))
            return

        if self.type_name == "Slime":
            pygame.draw.circle(surface, dark_color, (cx, int(fly_y)), 18)
            pygame.draw.ellipse(surface, base_color, (cx-16, int(fly_y)-14, 32, 28))
            pygame.draw.ellipse(surface, (255, 255, 255, 120), (cx-10, int(fly_y)-10, 8, 4))
            pygame.draw.circle(surface, (0, 0, 0), (cx-5, int(fly_y)-2), 2)
            pygame.draw.circle(surface, (0, 0, 0), (cx+5, int(fly_y)-2), 2)
            
        elif self.type_name == "Wolf":
            pygame.draw.ellipse(surface, base_color, (cx+5, int(fly_y)-10, 15, 10))
            pygame.draw.circle(surface, (0, 0, 0), (cx+18, int(fly_y)-8), 2)
            pygame.draw.polygon(surface, dark_color, [(cx+5, int(fly_y)-10), (cx+2, int(fly_y)-18), (cx+10, int(fly_y)-6)])
            pygame.draw.ellipse(surface, dark_color, (cx-15, int(fly_y)-12, 25, 16))
            leg_offset = math.sin(t * 0.4) * 4
            pygame.draw.line(surface, dark_color, (cx-8, int(fly_y)), (cx-12+leg_offset, int(fly_y)+8), 3)
            pygame.draw.line(surface, dark_color, (cx+3, int(fly_y)-2), (cx+5-leg_offset, int(fly_y)+8), 3)
            pygame.draw.line(surface, base_color, (cx-14, int(fly_y)-6), (cx-24, int(fly_y)-10+leg_offset), 4)

        elif self.type_name == "Golem":
            for i in range(-1, 2):
                for j in range(-1, 2):
                    pygame.draw.rect(surface, base_color if (i+j)%2==0 else dark_color, (cx+i*10-5, int(fly_y)+j*10-15, 10, 10))
            pygame.draw.rect(surface, (0,0,0), (cx-15, int(fly_y)-25, 30, 40), 2)
            pygame.draw.rect(surface, (255, 0, 0), (cx-6, int(fly_y)-12, 12, 4))
            
        elif self.type_name == "Dragon":
            pygame.draw.ellipse(surface, base_color, (cx-12, int(fly_y)-10, 24, 20))
            pygame.draw.circle(surface, base_color, (cx+12, int(fly_y)-15), 8)
            pygame.draw.polygon(surface, dark_color, [(cx+12, int(fly_y)-20), (cx+16, int(fly_y)-28), (cx+18, int(fly_y)-16)])
            wing_y = math.sin(t * 0.6) * 15
            pygame.draw.polygon(surface, dark_color, [(cx, int(fly_y)-5), (cx-15, int(fly_y)-25+wing_y), (cx-5, int(fly_y)-15+wing_y), (cx, int(fly_y))])
            pygame.draw.polygon(surface, dark_color, [(cx, int(fly_y)-5), (cx+15, int(fly_y)-25+wing_y), (cx+5, int(fly_y)-15+wing_y), (cx, int(fly_y))])
            pygame.draw.polygon(surface, dark_color, [(cx-10, int(fly_y)), (cx-25, int(fly_y)+10), (cx-8, int(fly_y)+6)])
            pygame.draw.circle(surface, (255, 255, 0), (cx+15, int(fly_y)-16), 2)

        else:
            pygame.draw.circle(surface, base_color, (cx, int(fly_y)), 14)
            pygame.draw.circle(surface, dark_color, (cx, int(fly_y)+4), 8)
            pygame.draw.line(surface, (0, 0, 0), (cx-8, int(fly_y)-6), (cx-2, int(fly_y)-4), 2)
            pygame.draw.line(surface, (0, 0, 0), (cx+8, int(fly_y)-6), (cx+2, int(fly_y)-4), 2)
            pygame.draw.circle(surface, (255, 0, 0), (cx-4, int(fly_y)-3), 1)
            pygame.draw.circle(surface, (255, 0, 0), (cx+4, int(fly_y)-3), 1)
            pygame.draw.polygon(surface, (255, 255, 255), [(cx-4, int(fly_y)+4), (cx-2, int(fly_y)+8), (cx, int(fly_y)+4)])
            pygame.draw.polygon(surface, (255, 255, 255), [(cx+4, int(fly_y)+4), (cx+2, int(fly_y)+8), (cx, int(fly_y)+4)])

        if self.health < self.max_health:
            bar_w = 30
            fill_w = int(bar_w * (self.health / self.max_health))
            hx, hy = cx - 15, cy - 35
            pygame.draw.rect(surface, (40, 20, 20), (hx, hy, bar_w, 4))
            pygame.draw.rect(surface, (50, 255, 50), (hx, hy, fill_w, 4))

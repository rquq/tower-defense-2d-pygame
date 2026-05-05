import pygame
from core.constants import *
from entities.enemy import Enemy
import random
from systems.inventory_items import InventoryItem
from systems.asset_manager import AssetManager

class WaveManager:
    """
    Orchestrates wave progression tracking enemy states accurately.
    """
    def __init__(self, vfx_manager):
        """
        Loads baseline gold stores.
        """
        self.vfx_manager = vfx_manager
        self.wave_number = 1
        self.health = BASE_HEALTH
        self.gold = 150
        self.enemies = []
        self.enemies_to_spawn = 0
        self.spawn_timer = 0
        self.last_spawn_time = 0
        self.is_wave_active = False
        self.inventory = [] # List of InventoryItem objects
        self.item_drop_rate = 0.1 # 10% chance for gem on kill
        self.mob_gold_multiplier = 1.0
        self.wave_interval_multiplier = 1.0

    def start_wave(self, waypoint_list):
        """
        Increases total wave numbers dynamically.
        """
        self.is_wave_active = True
        self.active_waypoints = waypoint_list
        if self.wave_number < 5:
            self.enemies_to_spawn = 5 + self.wave_number * 2
        else:
            self.enemies_to_spawn = 15 + (self.wave_number - 5) * 7
        self.spawn_timer = 0

    def spawn_enemy(self, waypoint_list):
        """
        Spawns units utilizing probability scaling rules.
        """
        hp_mult = HP_SCALING ** (self.wave_number - 1)
        speed_mult = ENEMY_SPEED_SCALING ** (self.wave_number - 1)
        
        available = [t for t, stats in ENEMY_TYPES.items() if stats.get("min_wave", 1) <= self.wave_number]
        etype = random.choice(available)
        self.enemies.append(Enemy(waypoint_list, etype, hp_mult, speed_mult))

    def update(self):
        """
        Refreshes enemy conditions efficiently.
        """
        if self.is_wave_active:
            self.spawn_timer += 1
            if self.enemies_to_spawn > 0 and self.spawn_timer >= ENEMY_SPAWN_INTERVAL // 16:
                self.spawn_enemy(self.active_waypoints)
                self.enemies_to_spawn -= 1
                self.spawn_timer = 0
            
            for enemy in self.enemies[:]:
                enemy.update()
                if enemy.reached_end:
                    AssetManager.get_instance().play_sound("base_hit")
                    self.health -= 1
                    self.enemies.remove(enemy)
                elif enemy.health <= 0:
                    AssetManager.get_instance().play_sound("enemy_death")
                    self.vfx_manager.create_death_effect(enemy.x, enemy.y, enemy.color)
                    reward = int(enemy.reward * self.mob_gold_multiplier)
                    self.gold += reward
                    if random.random() < 0.25:
                        roll = random.random()
                        if roll < 0.25:
                            b_type = random.choice(["ATTACK BEACON", "SPEED BEACON", "RANGE BEACON"])
                            self.inventory.append(InventoryItem(ItemType.BEACON, b_type))
                        elif roll < 0.50:
                            c_data = random.choice([
                                {"name": "STRENGTH CARD", "desc": "GRANT +15% ATK"},
                                {"name": "AGILITY CARD", "desc": "GRANT +15% SPD"},
                                {"name": "VISION CARD", "desc": "GRANT +15% RNG"},
                                {"name": "PRECISION CARD", "desc": "GRANT +10% CRIT"}
                            ])
                            self.inventory.append(InventoryItem(ItemType.STAT_CARD, c_data))
                        else:
                            g_type = random.choice(["FIRE", "ICE", "OVERCLOCK"])
                            self.inventory.append(InventoryItem(ItemType.GEM, g_type))
                    self.enemies.remove(enemy)
            
            if self.enemies_to_spawn == 0 and len(self.enemies) == 0:
                self.is_wave_active = False
                self.wave_number += 1
        
    def draw(self, surface):
        """
        Applies batch iteration logic for drawing.
        """
        for enemy in self.enemies:
            enemy.draw(surface)

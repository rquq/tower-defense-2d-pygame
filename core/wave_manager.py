import pygame
from core.constants import *
from entities.enemy import Enemy
import random
from systems.inventory_items import InventoryItem
from systems.asset_manager import AssetManager

class WaveManager:
    def __init__(self, vfx_manager):
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
        self.is_wave_active = True
        self.active_waypoints = waypoint_list
        # Scale enemy count: Managed early, aggressive late
        if self.wave_number < 5:
            self.enemies_to_spawn = 5 + self.wave_number * 2
        else:
            # Ramps up significantly after W5: 15, 22, 29, 36...
            self.enemies_to_spawn = 15 + (self.wave_number - 5) * 7
        self.spawn_timer = 0

    def spawn_enemy(self, waypoint_list):
        hp_mult = HP_SCALING ** (self.wave_number - 1)
        speed_mult = ENEMY_SPEED_SCALING ** (self.wave_number - 1)
        
        # Filter available types based on current wave
        available = [t for t, stats in ENEMY_TYPES.items() if stats.get("min_wave", 1) <= self.wave_number]
        etype = random.choice(available)
        self.enemies.append(Enemy(waypoint_list, etype, hp_mult, speed_mult))

    def update(self):
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
                    # 25% total drop chance
                    if random.random() < 0.25:
                        roll = random.random()
                        if roll < 0.25:
                            # 25% Beacon
                            b_type = random.choice(["ATTACK BEACON", "SPEED BEACON", "RANGE BEACON"])
                            self.inventory.append(InventoryItem(ItemType.BEACON, b_type))
                        elif roll < 0.50:
                            # 25% Blessing (Stat Card)
                            c_data = random.choice([
                                {"name": "STRENGTH CARD", "desc": "GRANT +15% ATK"},
                                {"name": "AGILITY CARD", "desc": "GRANT +15% SPD"},
                                {"name": "VISION CARD", "desc": "GRANT +15% RNG"},
                                {"name": "PRECISION CARD", "desc": "GRANT +10% CRIT"}
                            ])
                            self.inventory.append(InventoryItem(ItemType.STAT_CARD, c_data))
                        else:
                            # 50% Gem (Buff)
                            g_type = random.choice(["FIRE", "ICE", "OVERCLOCK"])
                            self.inventory.append(InventoryItem(ItemType.GEM, g_type))
                    self.enemies.remove(enemy)
            
            if self.enemies_to_spawn == 0 and len(self.enemies) == 0:
                self.is_wave_active = False
                self.wave_number += 1
                # Increase difficulty every wave
        
    def draw(self, surface):
        for enemy in self.enemies:
            enemy.draw(surface)

import pygame
import sys
import os
import math
import random
from core.constants import *
from core.wave_manager import WaveManager
from entities.tower import Tower
from entities.beacon import Beacon
from systems.pathfinding import PathSystem
from systems.inventory_items import InventoryItem, ItemType
from systems.vfx_system import VFXManager
from systems.asset_manager import AssetManager
from systems.spatial_manager import SpatialManager
from core.locales import TEXT, LANGUAGES

class Engine:
    def __init__(self, is_dev=False):
        self.lang_idx = 0
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        self.display_surface = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        pygame.display.set_caption("Fantasy Tower Defense 2D")
        self.clock = pygame.time.Clock()
        
        AssetManager.get_instance().init()
        
        try:
            self.fonts = {
                "tiny": pygame.font.SysFont("calibri", 20),
                "small": pygame.font.SysFont("calibri", 28),
                "medium": pygame.font.SysFont("calibri", 42),
                "large": pygame.font.SysFont("calibri", 96, bold=True),
                "mono": pygame.font.SysFont("consolas,monospace", 22, bold=True)
            }
        except Exception:
            fallback = pygame.font.match_font('consolas,monospace')
            self.fonts = {f: pygame.font.SysFont(fallback, s) for f, s in zip(["tiny", "small", "medium", "large"], [20, 28, 42, 96])}
            self.fonts["mono"] = pygame.font.SysFont("consolas,monospace", 22, bold=True)
        
        self.path_system = PathSystem()
        self.vfx_manager = VFXManager()
        self.spatial_manager = SpatialManager(cell_size=200)
        self.wave_manager = WaveManager(self.vfx_manager)
        
        self.needs_stat_recalc = True
        self.is_dev = is_dev
        if is_dev: self.wave_manager.gold = 999999
        self.towers = []
        self.beacons = []
        self.selected_type = "Earth Cannon"
        self.state = GameState.MENU
        self.running = True
        self.next_wave_timer = (2 if is_dev else 30) * FPS
        self.current_powerups = []
        self.powerups_offered = False
        self.powerup_timer = 0
        
        self.selected_inv_idx = -1
        self.inv_scroll = 0
        self.trash_mode = False
        self.auto_slot_mode = False
        self.auto_slot_timer = 0
        
        # Pre-generated environment details
        self.trees = []
        self.generate_trees()
        
        self.background_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
        self.render_static_background()

    def t(self, key):
        return TEXT[LANGUAGES[self.lang_idx]].get(key, key)

    def generate_trees(self):
        self.trees = []
        # Dense "Single Circle" scatter with 10% grid overlap for seamless blending
        for _ in range(700):
            side = random.choice(["L", "R", "T"])
            size = random.randint(70, 130)
            rad = size // 2
            overlap = int(rad * 0.1) # 10% overlap into the grid
            if side == "L": 
                x, y = random.randint(-rad, OFFSET_X - rad + overlap), random.randint(-rad, WIN_HEIGHT + rad)
            elif side == "R": 
                x, y = random.randint(WIN_WIDTH - OFFSET_X + rad - overlap, WIN_WIDTH + rad), random.randint(-rad, WIN_HEIGHT + rad)
            else: 
                x, y = random.randint(-rad, WIN_WIDTH + rad), random.randint(-rad, UI_HUD_HEIGHT - rad + overlap)
            self.trees.append(self._create_tree_data(x, y, size))
    def _create_tree_data(self, bx, by, size):
        r = random.Random(bx * 7 + by * 13)
        # Middle-ground vibrant forest greens
        color = (r.randint(35, 65), r.randint(110, 155), r.randint(35, 65))
        return {
            "pos": (bx, by),
            "size": size,
            "color": color
        }

    def render_static_background(self):
        ctx = self.background_surface
        # 1. Perfectly Aligned Checkered Background
        # Extend the grid range to cover the whole screen relative to the play grid's origin
        start_c = - (OFFSET_X // GRID_SIZE) - 2
        end_c = GRID_COLS + ((WIN_WIDTH - (OFFSET_X + GRID_COLS * GRID_SIZE)) // GRID_SIZE) + 4
        start_r = - (OFFSET_Y // GRID_SIZE) - 2
        end_r = GRID_ROWS + ((WIN_HEIGHT - (OFFSET_Y + GRID_ROWS * GRID_SIZE)) // GRID_SIZE) + 4
        
        for c in range(start_c, end_c):
            for r in range(start_r, end_r):
                gx, gy = OFFSET_X + c * GRID_SIZE, OFFSET_Y + r * GRID_SIZE
                color = (85, 165, 65) if (c + r) % 2 == 0 else (95, 175, 75)
                ctx.fill(color, (gx, gy, GRID_SIZE, GRID_SIZE))
                
                # Sparser background details
                rnd = random.Random(c * 777 + r * 333)
                if rnd.random() < 0.3:
                    for _ in range(rnd.randint(1, 3)):
                        nx, ny = gx + rnd.randint(5, GRID_SIZE-5), gy + rnd.randint(5, GRID_SIZE-5)
                        pygame.draw.line(ctx, (60, 120, 40), (nx, ny), (nx, ny-rnd.randint(2, 5)), 1)

        # 2. Path and Grid Details (Restricted to play area)
        for c in range(GRID_COLS):
            for r in range(GRID_ROWS):
                gx, gy = OFFSET_X + c * GRID_SIZE, OFFSET_Y + r * GRID_SIZE
                # Subtle Grid Borders
                pygame.draw.rect(ctx, (70, 140, 40), (gx, gy, GRID_SIZE, GRID_SIZE), 1)
                
                if (c, r) in self.path_system.walkable_tiles:
                    # Sandy Dirt Path Overlay
                    ctx.fill((230, 205, 140), (gx, gy, GRID_SIZE, GRID_SIZE))
                    rnd = random.Random(c * 100 + r)
                    for _ in range(rnd.randint(4, 7)):
                        px, py = gx + rnd.randint(5, GRID_SIZE-5), gy + rnd.randint(5, GRID_SIZE-5)
                        pygame.draw.circle(ctx, (170, 150, 110), (px, py), rnd.randint(1, 3))
                else:
                    # Real Grass Blades & Big Tufts (already checkered by step 1)
                    rnd = random.Random(c * 777 + r * 333)
                    for _ in range(rnd.randint(12, 18)):
                        nx, ny = gx + rnd.randint(3, GRID_SIZE-3), gy + rnd.randint(5, GRID_SIZE-3)
                        h = rnd.randint(4, 9)
                        grass_color = (rnd.randint(60, 100), rnd.randint(160, 210), rnd.randint(50, 80))
                        shadow_color = (max(0, grass_color[0]-40), max(0, grass_color[1]-40), max(0, grass_color[2]-40))
                        pygame.draw.line(ctx, shadow_color, (nx+1, ny), (nx+1, ny-h+1), 1)
                        pygame.draw.line(ctx, grass_color, (nx, ny), (nx + rnd.randint(-1, 1), ny-h), 1)
                        if h > 6: pygame.draw.circle(ctx, (min(255, grass_color[0]+30), min(255, grass_color[1]+30), min(255, grass_color[2]+30)), (nx, ny-h), 1)

                    # --- Big Grass Tufts (3-leaf shaped) ---
                    for _ in range(rnd.randint(2, 4)):
                        nx, ny = gx + rnd.randint(5, GRID_SIZE-5), gy + rnd.randint(5, GRID_SIZE-5)
                        h = rnd.randint(8, 12); grass_color = (rnd.randint(40, 80), rnd.randint(140, 190), rnd.randint(40, 70))
                        shadow_color = (max(0, grass_color[0]-30), max(0, grass_color[1]-30), max(0, grass_color[2]-30))
                        for ang in [-0.4, 0, 0.4]:
                            tx, ty = nx + math.sin(ang) * h, ny - math.cos(ang) * h
                            pygame.draw.line(ctx, shadow_color, (nx+1, ny), (tx+1, ty+1), 2)
                            pygame.draw.line(ctx, grass_color, (nx, ny), (tx, ty), 2)

                    # --- Small Field Flowers ---
                    if rnd.random() < 0.15:
                        for _ in range(rnd.randint(1, 2)):
                            fx, fy = gx + rnd.randint(10, GRID_SIZE-10), gy + rnd.randint(10, GRID_SIZE-10)
                            f_color = rnd.choice([(220, 80, 80), (80, 150, 220), (180, 80, 220), (255, 230, 100)])
                            pygame.draw.line(ctx, (40, 100, 30), (fx, fy), (fx, fy-3), 1)
                            pygame.draw.circle(ctx, f_color, (fx, fy-3), 2); pygame.draw.circle(ctx, (255, 255, 255), (fx, fy-3), 1)

        # 2. Border Lines for Grid (Subtle)
        for c in range(GRID_COLS + 1):
            pygame.draw.line(ctx, (70, 140, 40), (OFFSET_X + c * GRID_SIZE, OFFSET_Y), (OFFSET_X + c * GRID_SIZE, OFFSET_Y + GRID_ROWS * GRID_SIZE), 1)
        for r in range(GRID_ROWS + 1):
            pygame.draw.line(ctx, (70, 140, 40), (OFFSET_X, OFFSET_Y + r * GRID_SIZE), (OFFSET_X + GRID_COLS * GRID_SIZE, OFFSET_Y + r * GRID_SIZE), 1)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU: 
                    if event.key == pygame.K_l: self.lang_idx = (self.lang_idx + 1) % len(LANGUAGES)
                    else: self.state = GameState.PLAYING
                elif self.state == GameState.PLAYING:
                    keys = {pygame.K_1: "Earth Cannon", pygame.K_2: "Wind Ballista", pygame.K_3: "Fire Mortar", pygame.K_4: "Storm Spire", pygame.K_5: "Frost Cannon"}
                    if event.key in keys: 
                        self.selected_type = keys[event.key]; self.trash_mode = False; self.selected_inv_idx = -1
                    if event.key == pygame.K_n: self.force_start_wave()
                    if event.key == pygame.K_t: self.trash_mode = not self.trash_mode
                    if event.key == pygame.K_ESCAPE: self.selected_inv_idx = -1; self.trash_mode = False
                    if self.is_dev:
                        if event.key == pygame.K_g: self.wave_manager.gold += 10000
                        if event.key == pygame.K_h: self.wave_manager.health = 100
                        if event.key == pygame.K_k:
                            for e in self.wave_manager.enemies: e.health = 0
                elif self.state == GameState.POWERUP:
                    if pygame.K_1 <= event.key <= pygame.K_3: self.apply_powerup(event.key - pygame.K_1)
                elif self.state == GameState.GAME_OVER: self.reset_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: self.handle_click()
                elif event.button == 4: self.inv_scroll = max(0, self.inv_scroll - 1)
                elif event.button == 5: self.inv_scroll = min(max(0, len(self.wave_manager.inventory)-8), self.inv_scroll + 1)

    def handle_click(self):
        mx, my = pygame.mouse.get_pos(); panel_y = WIN_HEIGHT - UI_BOTTOM_HEIGHT
        if self.state == GameState.MENU:
            lw = self.fonts["small"].size(self.t("LANGUAGE"))[0] + 40
            lx, ly = WIN_WIDTH//2 - lw//2, WIN_HEIGHT//2 + 120
            if lx <= mx <= lx + lw and ly <= my <= ly + 40:
                self.lang_idx = (self.lang_idx + 1) % len(LANGUAGES)
                AssetManager.get_instance().play_sound("ui_click")
            else: self.state = GameState.PLAYING
            return

        if self.state == GameState.POWERUP:
            start_x = WIN_WIDTH // 2 - 450
            for i in range(3):
                if start_x + i * 310 <= mx <= start_x + i * 310 + 280 and 350 <= my <= 650:
                    AssetManager.get_instance().play_sound("powerup"); self.apply_powerup(i); return
            return

        if self.state == GameState.PLAYING:
            # Shop section click
            if 60 <= mx <= 160 and panel_y + 25 <= my <= panel_y + 125:
                AssetManager.get_instance().play_sound("ui_click")
                self.trash_mode = not self.trash_mode; self.selected_inv_idx = -1; return
            for i, tower_type in enumerate(TOWER_STATS.keys()):
                bx = 180 + i * 115
                if bx <= mx <= bx+100 and (panel_y+20) <= my <= (panel_y+120):
                    AssetManager.get_instance().play_sound("ui_click"); self.selected_type = tower_type
                    self.selected_inv_idx = -1; self.trash_mode = False; return

            # Inventory section click
            if 810 <= mx <= 930 and panel_y + 25 <= my <= panel_y + 65:
                self.auto_slot_mode = not self.auto_slot_mode
                AssetManager.get_instance().play_sound("ui_click"); return
            for i in range(min(16, len(self.wave_manager.inventory))):
                item_idx = i + self.inv_scroll
                if item_idx >= len(self.wave_manager.inventory): break
                if 810 + i*45 <= mx <= 810 + i*45 + 40 and panel_y + 80 <= my <= panel_y + 120:
                    AssetManager.get_instance().play_sound("ui_click")
                    self.selected_inv_idx = item_idx; self.trash_mode = False; return

            if not self.wave_manager.is_wave_active and WIN_WIDTH-250 <= mx <= WIN_WIDTH-30 and 8 <= my <= 40:
                self.force_start_wave(); return
            if my > panel_y: return # Already handled shop/inventory clicks
            if self.trash_mode:
                for t in self.towers[:]:
                    if math.hypot(t.x - mx, t.y - my) < GRID_SIZE//2:
                        AssetManager.get_instance().play_sound("sell"); self.towers.remove(t)
                        self.needs_stat_recalc = True; return
                for b in self.beacons[:]:
                    if math.hypot(b.x - mx, b.y - my) < GRID_SIZE//2:
                        AssetManager.get_instance().play_sound("sell"); self.beacons.remove(b)
                        self.needs_stat_recalc = True; return
            elif self.selected_inv_idx != -1:
                item = self.wave_manager.inventory[self.selected_inv_idx]
                if item.item_type == ItemType.BEACON:
                    gx, gy = (mx - OFFSET_X) // GRID_SIZE, (my - OFFSET_Y) // GRID_SIZE
                    px, py = gx * GRID_SIZE + OFFSET_X + GRID_SIZE // 2, gy * GRID_SIZE + OFFSET_Y + GRID_SIZE // 2
                    if self.is_valid_placement(gx, gy, px, py):
                        AssetManager.get_instance().play_sound("place_tower")
                        self.beacons.append(Beacon(px, py, item.name))
                        self.wave_manager.inventory.pop(self.selected_inv_idx); self.selected_inv_idx = -1
                        self.needs_stat_recalc = True; return
                elif item.item_type == ItemType.STAT_CARD:
                    for b in self.beacons:
                        if math.hypot(b.x - mx, b.y - my) < GRID_SIZE//2:
                            if b.add_gem(item):
                                AssetManager.get_instance().play_sound("powerup")
                                self.wave_manager.inventory.pop(self.selected_inv_idx)
                                self.selected_inv_idx = -1; self.needs_stat_recalc = True; return
                elif item.item_type == ItemType.GEM:
                    for t in self.towers:
                        if math.hypot(t.x - mx, t.y - my) < GRID_SIZE//2:
                            if t.add_gem(item):
                                AssetManager.get_instance().play_sound("powerup")
                                self.wave_manager.inventory.pop(self.selected_inv_idx)
                                self.selected_inv_idx = -1; self.needs_stat_recalc = True; return
            else:
                gx, gy = (mx - OFFSET_X) // GRID_SIZE, (my - OFFSET_Y) // GRID_SIZE
                px, py = gx * GRID_SIZE + OFFSET_X + GRID_SIZE // 2, gy * GRID_SIZE + OFFSET_Y + GRID_SIZE // 2
                if self.is_valid_placement(gx, gy, px, py):
                    cost = TOWER_STATS[self.selected_type]['cost']
                    if self.wave_manager.gold >= cost:
                        AssetManager.get_instance().play_sound("place_tower")
                        self.wave_manager.gold -= cost; self.towers.append(Tower(px, py, self.selected_type))
                        self.needs_stat_recalc = True

    def is_valid_placement(self, gx, gy, px, py):
        if not (0 <= gx < GRID_COLS and 0 <= gy < GRID_ROWS) or (gx, gy) in self.path_system.walkable_tiles: return False
        for t in self.towers:
            if math.hypot(t.x - px, t.y - py) < GRID_SIZE: return False
        for b in self.beacons:
            if math.hypot(b.x - px, b.y - py) < GRID_SIZE: return False
        return True

    def calculate_adjacency_buffs(self):
        beacon_map = {( (int(b.x) - OFFSET_X) // GRID_SIZE, (int(b.y) - OFFSET_Y) // GRID_SIZE ): b for b in self.beacons}
        for t in self.towers:
            tgx, tgy = (int(t.x) - OFFSET_X) // GRID_SIZE, (int(t.y) - OFFSET_Y) // GRID_SIZE
            buff_list = []
            for nb in [(tgx+1, tgy), (tgx-1, tgy), (tgx, tgy+1), (tgx, tgy-1)]:
                if nb in beacon_map:
                    beacon = beacon_map[nb]
                    b_buffs = beacon.get_all_buffs()
                    for b_type, b_val in b_buffs.items():
                        stat_map = {"ATK": "damage", "SPD": "fire_rate", "RNG": "range", "CRIT": "crit"}
                        buff_list.append((stat_map[b_type], b_val))
            t.recalculate(buff_list)

    def force_start_wave(self):
        if not self.wave_manager.is_wave_active and self.state == GameState.PLAYING:
            AssetManager.get_instance().play_sound("wave_start")
            self.wave_manager.start_wave(self.path_system.get_enemy_waypoints())
            self.next_wave_timer = int(20 * FPS * self.wave_manager.wave_interval_multiplier)

    def update(self):
        if self.state == GameState.PLAYING:
            self.vfx_manager.update(); self.wave_manager.update()
            self.spatial_manager.clear()
            for enemy in self.wave_manager.enemies: self.spatial_manager.add_entity(enemy)
            if self.needs_stat_recalc: self.calculate_adjacency_buffs(); self.needs_stat_recalc = False
            for tower in self.towers: 
                tower.update(self.spatial_manager, self.vfx_manager)
            for b in self.beacons:
                bgx, bgy = (int(b.x) - OFFSET_X) // GRID_SIZE, (int(b.y) - OFFSET_Y) // GRID_SIZE
                for t in self.towers:
                    tgx, tgy = (int(t.x) - OFFSET_X) // GRID_SIZE, (int(t.y) - OFFSET_Y) // GRID_SIZE
                    if abs(tgx - bgx) + abs(tgy - bgy) == 1 and random.random() < 0.15:
                        self.vfx_manager.spawn_link_particle(b.x, b.y, t.x, t.y, b.color)
            if self.auto_slot_mode: self.process_auto_slots()
            if not self.wave_manager.is_wave_active:
                if self.wave_manager.wave_number % BLESSING_INTERVAL == 0 and not self.powerups_offered:
                    self.state = GameState.POWERUP; self.trigger_powerup(); return
                self.next_wave_timer -= 1
                if self.next_wave_timer <= 0: self.force_start_wave()
            else: self.powerups_offered = False; self.next_wave_timer = (2 if self.is_dev else 30) * FPS
            if self.wave_manager.health <= 0:
                if self.state != GameState.GAME_OVER: AssetManager.get_instance().play_sound("game_over")
                self.state = GameState.GAME_OVER
        elif self.state == GameState.POWERUP:
            self.powerup_timer -= 1
            if self.powerup_timer <= 0: self.state = GameState.PLAYING

    def draw(self):
        temp_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
        old_surface, self.display_surface = self.display_surface, temp_surface
        if self.state == GameState.MENU: self.draw_menu()
        elif self.state in [GameState.PLAYING, GameState.POWERUP, GameState.GAME_OVER]:
            self.draw_playing()
            if self.state == GameState.POWERUP: self.draw_powerup_menu()
            elif self.state == GameState.GAME_OVER: 
                self.display_surface.blit(self.apply_blur(self.display_surface, 3, 2), (0, 0))
                self.draw_game_over()
            self.draw_tooltips()
        self.display_surface = old_surface
        self.display_surface.blit(temp_surface, (0, 0))
        pygame.display.flip()

    def apply_blur(self, surface, amount=3, passes=2):
        w, h = surface.get_size(); blurred = surface
        for _ in range(passes):
            small = pygame.transform.smoothscale(blurred, (w // amount, h // amount))
            blurred = pygame.transform.smoothscale(small, (w, h))
        return blurred

    def draw_text_with_shadow(self, text, font, color, pos, shadow_color=(0, 0, 0, 180), offset=(2, 2)):
        self.display_surface.blit(font.render(text, True, shadow_color), (pos[0] + offset[0], pos[1] + offset[1]))
        self.display_surface.blit(font.render(text, True, color), pos)

    def draw_wrapped_text_centered(self, text, font, color, center_x, start_y, max_width):
        words = text.split(' '); lines = []; current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= max_width: current_line = test_line
            else:
                if current_line: lines.append(current_line.strip())
                current_line = word + " "
        if current_line: lines.append(current_line.strip())
        line_height = font.get_linesize()
        for i, line in enumerate(lines):
            tw = font.size(line)[0]
            self.draw_text_with_shadow(line, font, color, (center_x - tw // 2, start_y + i * line_height))

    def draw_menu(self):
        ctx = self.display_surface; ctx.blit(self.background_surface, (0, 0))
        self.draw_surrounding_forests(ctx)
        ctx.blit(self.apply_blur(ctx, 4, 3), (0, 0))
        s = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA); s.fill((0, 0, 0, 160)); ctx.blit(s, (0, 0))
        title = self.t("TITLE"); font_l = self.fonts["large"]
        self.draw_text_with_shadow(title, font_l, COLOR_ACCENT, (WIN_WIDTH//2 - font_l.size(title)[0]//2, WIN_HEIGHT//2 - 100), offset=(4, 4))
        start = self.t("PRESS_START"); font_m = self.fonts["medium"]
        self.draw_text_with_shadow(start, font_m, COLOR_UI_TEXT, (WIN_WIDTH//2 - font_m.size(start)[0]//2, WIN_HEIGHT//2 + 50))
        lang = self.t("LANGUAGE"); font_s = self.fonts["small"]; lw = font_s.size(lang)[0] + 40
        lx, ly = WIN_WIDTH//2 - lw//2, WIN_HEIGHT//2 + 120; mx, my = pygame.mouse.get_pos()
        hover = lx <= mx <= lx + lw and ly <= my <= ly + 40
        pygame.draw.rect(ctx, (70, 120, 70) if hover else (50, 100, 50), (lx, ly, lw, 40), border_radius=5)
        pygame.draw.rect(ctx, (200, 200, 150), (lx, ly, lw, 40), 2, border_radius=5)
        self.draw_text_with_shadow(lang, font_s, COLOR_UI_TEXT, (lx + 20, ly + 5))

    def draw_playing(self):
        ctx = self.display_surface; ctx.blit(self.background_surface, (0, 0))
        t = pygame.time.get_ticks() / 1000
        self.draw_surrounding_forests(ctx)
        self.draw_monster_cave(*get_pixel_pos(0, 4), t)
        self.draw_castle_base(get_pixel_pos(27, 9), t)
        shadow_surf = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
        for b in self.beacons:
            x, y = int(b.x), int(b.y)
            pts = [(x, y-20), (x+20, y), (x, y+20), (x-20, y)]
            pygame.draw.polygon(shadow_surf, (0, 0, 0, 70), [(p[0]+5, p[1]+5) for p in pts])
        for t in self.towers:
            Tower.draw_design(shadow_surf, t.x, t.y, t.type, (0, 0, 0), t.angle, is_shadow=True)
        ctx.blit(shadow_surf, (0,0))
        for b in self.beacons: b.draw(ctx)
        for tower in self.towers: tower.draw(ctx)
        self.wave_manager.draw(ctx); self.vfx_manager.draw(ctx, self.fonts["tiny"])
        self.draw_ui()
        if self.state == GameState.PLAYING: self.draw_placement_preview()

    def draw_placement_preview(self):
        mx, my = pygame.mouse.get_pos(); gx, gy = (mx-OFFSET_X)//GRID_SIZE, (my-OFFSET_Y)//GRID_SIZE
        if not (0 <= gx < GRID_COLS and 0 <= gy < GRID_ROWS): return
        px, py = gx*GRID_SIZE+OFFSET_X+GRID_SIZE//2, gy*GRID_SIZE+OFFSET_Y+GRID_SIZE//2
        ctx = self.display_surface
        if self.trash_mode:
            s = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA); s.fill((200, 50, 50, 100)); ctx.blit(s, (px-GRID_SIZE//2, py-GRID_SIZE//2)); return
        if self.selected_inv_idx != -1:
            item = self.wave_manager.inventory[self.selected_inv_idx]
            if item.item_type == ItemType.BEACON:
                v = self.is_valid_placement(gx, gy, px, py)
            elif item.item_type == ItemType.STAT_CARD:
                v = any((int(b.x)-OFFSET_X)//GRID_SIZE == gx and (int(b.y)-OFFSET_Y)//GRID_SIZE == gy for b in self.beacons)
            else: # GEM
                v = any((int(t.x)-OFFSET_X)//GRID_SIZE == gx and (int(t.y)-OFFSET_Y)//GRID_SIZE == gy for t in self.towers)
            s = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA); s.fill(COLOR_VALID if v else COLOR_INVALID); ctx.blit(s, (px-GRID_SIZE//2, py-GRID_SIZE//2)); return
        if OFFSET_Y < my < WIN_HEIGHT-UI_BOTTOM_HEIGHT:
            v = self.is_valid_placement(gx, gy, px, py)
            s = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA); s.fill(COLOR_VALID if v else COLOR_INVALID); ctx.blit(s, (px-GRID_SIZE//2, py-GRID_SIZE//2))
            pygame.draw.circle(ctx, (255,255,255,40), (px, py), TOWER_STATS[self.selected_type]['range'], 1)

    def draw_ui(self):
        ctx = self.display_surface; hud_gray = (50, 50, 60)
        self.draw_hud_module(30, 8, 160, f"{self.t('WAVE')}: {self.wave_manager.wave_number}", hud_gray)
        if self.wave_manager.is_wave_active: 
            self.draw_hud_module(210, 8, 160, f"{self.t('MOBS')}: {self.wave_manager.enemies_to_spawn + len(self.wave_manager.enemies)}", hud_gray, (255, 100, 100))
        self.draw_hud_module(WIN_WIDTH // 2 - 110, 8, 220, f"{self.t('GOLD')}: {int(self.wave_manager.gold)}", hud_gray, (255, 215, 0))
        if not self.wave_manager.is_wave_active:
            self.draw_hud_module(WIN_WIDTH - 420, 8, 150, f"{self.t('IN')}: {max(0, self.next_wave_timer // FPS)}s", (40, 40, 50))
            bx = WIN_WIDTH - 250
            pygame.draw.rect(ctx, (40, 150, 40), (bx, 8, 220, 32), border_radius=5)
            pygame.draw.rect(ctx, (200, 180, 50), (bx, 8, 220, 32), 2, border_radius=5)
            txt = self.t("START_NOW"); tw = self.fonts["mono"].size(txt)[0]
            self.draw_text_with_shadow(txt, self.fonts["mono"], (255, 255, 255), (bx+110-tw//2, 12))
        py = WIN_HEIGHT - UI_BOTTOM_HEIGHT; sx, sw, sy, sh = 10, WIN_WIDTH-20, py+5, UI_BOTTOM_HEIGHT-10
        pygame.draw.rect(ctx, (80, 60, 40), (sx-2, sy-2, sw+4, sh+4), border_radius=15)
        pygame.draw.rect(ctx, (240, 225, 190), (sx, sy, sw, sh), border_radius=15)
        pygame.draw.rect(ctx, (220, 205, 170), (sx+8, sy+8, sw-16, sh-16), border_radius=10)
        for rx, ry in [(sx+15, sy+15), (sx+sw-15, sy+15), (sx+15, sy+sh-15), (sx+sw-15, sy+sh-15)]:
            pygame.draw.circle(ctx, (120, 110, 100), (rx, ry), 5); pygame.draw.circle(ctx, (60, 50, 40), (rx, ry), 5, 1)
        mx, my = pygame.mouse.get_pos()
        bx, by = 60, py + 25; hover = bx <= mx <= bx+100 and by <= my <= by+100
        pygame.draw.rect(ctx, (230, 70, 70) if self.trash_mode else (80, 130, 80) if hover else (60, 100, 60), (bx, by, 100, 100), border_radius=10)
        pygame.draw.rect(ctx, (255, 215, 0) if self.trash_mode else (40, 70, 40), (bx, by, 100, 100), 4 if self.trash_mode else 3, border_radius=10)
        bc, ix, iy = (60, 60, 60) if self.trash_mode else (180, 40, 40), bx+50, by+50
        pygame.draw.rect(ctx, bc, (ix-20, iy-15, 40, 35), border_radius=3)
        pygame.draw.rect(ctx, bc, (ix-25, iy-22, 50, 8), border_radius=2)
        pygame.draw.rect(ctx, bc, (ix-8, iy-28, 16, 8), border_radius=2)
        lc = (230, 70, 70) if self.trash_mode else (130, 130, 130)
        for lx in [-10, 0, 10]: pygame.draw.rect(ctx, lc, (ix + lx - 2, iy - 8, 4, 22), border_radius=1)
        for i, (name, s) in enumerate(TOWER_STATS.items()):
            bx, by = 180 + i*115, py+25; hover = bx <= mx <= bx+100 and by <= my <= by+100
            sel = (name == self.selected_type and not self.trash_mode and self.selected_inv_idx == -1)
            pygame.draw.rect(ctx, (100, 150, 100) if sel else (80, 120, 80) if hover else (70, 110, 70), (bx, by, 100, 100), border_radius=8)
            pygame.draw.rect(ctx, (255, 215, 0) if sel else (40, 80, 40), (bx, by, 100, 100), 5 if sel else 3, border_radius=8)
            Tower.draw_design(ctx, bx+50, by+40, name, s['color'], -math.pi/4, scale=1.2)
            rx, ry, rw, rh = bx+17.5, by+75, 65, 26
            pygame.draw.rect(ctx, (245, 235, 210), (rx, ry, rw, rh), border_radius=6); pygame.draw.rect(ctx, (60, 100, 60), (rx, ry, rw, rh), 2, border_radius=6)
            ct = self.fonts["mono"].render(f"${s['cost']}", True, (40, 80, 40)); ctx.blit(ct, (bx+50-ct.get_width()//2, ry+(rh-ct.get_height())//2))

        # --- SEPARATOR ---
        pygame.draw.line(ctx, (180, 170, 140), (780, py+20), (780, py+UI_BOTTOM_HEIGHT-20), 2)

        # --- INVENTORY SECTION ---
        ax, ay, aw, ah = 810, py+25, 120, 40
        ahover = ax <= mx <= ax+aw and ay <= my <= ay+ah
        pygame.draw.rect(ctx, (60, 150, 60) if self.auto_slot_mode else (120, 80, 80) if ahover else (100, 60, 60), (ax, ay, aw, ah), border_radius=8)
        pygame.draw.rect(ctx, (255, 215, 0) if self.auto_slot_mode else (40, 40, 50), (ax, ay, aw, ah), 2, border_radius=8)
        atxt = self.t("AUTO") + ": " + (self.t("ON") if self.auto_slot_mode else self.t("OFF"))
        af = self.fonts["tiny"].render(atxt, True, (255, 255, 255))
        ctx.blit(af, (ax + (aw - af.get_width()) // 2, ay + (ah - af.get_height()) // 2))

        sy = py+25; it = f"{self.t('INVENTORY')} ({len(self.wave_manager.inventory)})"
        self.draw_text_with_shadow(it, self.fonts["small"], (40, 80, 40), (950, sy+5), shadow_color=(210, 200, 180))
        for i in range(16):
            idx = i + self.inv_scroll
            if idx >= len(self.wave_manager.inventory): break
            item = self.wave_manager.inventory[idx]; gx, gy = 810+i*45, sy+55
            hover = gx <= mx <= gx+40 and gy <= my <= gy+40; sel = (idx == self.selected_inv_idx)
            pygame.draw.rect(ctx, (120, 160, 120) if sel else (100, 140, 100) if hover else (80, 120, 80), (gx, gy, 40, 40), border_radius=5)
            pygame.draw.rect(ctx, (255, 215, 0) if sel else (50, 90, 50), (gx, gy, 40, 40), 3 if sel else 2, border_radius=5)
            ix, iy = gx+20, gy+20
            if item.item_type == ItemType.GEM:
                pts = [(ix, iy-8), (ix+8, iy), (ix, iy+8), (ix-8, iy)]; pygame.draw.polygon(ctx, item.color, pts); pygame.draw.polygon(ctx, (255,255,255), pts, 1)
            elif item.item_type == ItemType.BEACON: pygame.draw.circle(ctx, item.color, (ix, iy), 8, 2); pygame.draw.circle(ctx, (255,255,255), (ix, iy), 2)
            elif item.item_type == ItemType.STAT_CARD: pygame.draw.rect(ctx, item.color, (ix-6, iy-8, 12, 16), 1)
        
        if len(self.wave_manager.inventory) > 16: self.draw_text_with_shadow("< SCROLL >", self.fonts["tiny"], (120, 110, 100), (WIN_WIDTH - 200, sy+110), shadow_color=(210, 200, 180))
        self.draw_text_with_shadow(f"FPS: {int(self.clock.get_fps())}", self.fonts["mono"], (255, 255, 255), (WIN_WIDTH - 120, WIN_HEIGHT - 40))

    def draw_hud_module(self, x, y, w, text, bg, tc=(255, 240, 200)):
        ctx = self.display_surface; font = self.fonts["mono"]; txt = font.render(text, True, tc); aw = max(w, txt.get_width()+25); h = 36
        pygame.draw.rect(ctx, (40, 80, 50), (x, y, aw, h), border_radius=6); pygame.draw.rect(ctx, (20, 50, 30), (x, y, aw, h), 2, border_radius=6)
        for rx, ry in [(x+6, y+6), (x+aw-6, y+6), (x+6, y+h-6), (x+aw-6, y+h-6)]:
            pygame.draw.circle(ctx, (110, 110, 120), (rx, ry), 2); pygame.draw.circle(ctx, (20, 20, 30), (rx, ry), 2, 1)
        self.draw_text_with_shadow(text, font, tc, (x+(aw-txt.get_width())//2, y+(h-txt.get_height())//2), shadow_color=(0,0,0,120))

    def draw_tooltips(self):
        mx, my = pygame.mouse.get_pos(); py = WIN_HEIGHT - UI_BOTTOM_HEIGHT
        for i, (name, s) in enumerate(TOWER_STATS.items()):
            bx = 180 + i*115
            if bx <= mx <= bx+100 and py+20 <= my <= py+120:
                spd_rating = int(1000 / s['fire_rate'])
                self.render_tooltip(mx, my-250, [f"--- {self.t(name).upper()} ---", f"{self.t('COST')}: ${s['cost']}", f"{self.t('ATK')}: {s['damage']}", f"{self.t('SPD')}: {spd_rating}", f"{self.t('RNG')}: {s['range']}", f"{self.t('CRIT')}: {int(s.get('crit_chance',0)*100)}% ({s.get('crit_mult',1.5)}X)", f"{self.t('AOE')}: {s.get('aoe', 0)}"]); return
        for i in range(min(16, len(self.wave_manager.inventory))):
            idx = i + self.inv_scroll
            if idx < len(self.wave_manager.inventory):
                gx, gy = 810 + i*45, py + 80
                if gx <= mx <= gx+40 and gy <= my <= gy+40: self.render_tooltip(mx-160, my-180, self.wave_manager.inventory[idx].get_tooltip_data(self.t)); return
        for b in self.beacons:
            if math.hypot(b.x - mx, b.y - my) < GRID_SIZE//2:
                all_buffs = b.get_all_buffs()
                buff_lines = [f"--- {self.t(b.type).upper()} ---", f"{self.t('DESCRIPTION')}: {self.t(b.desc)}"]
                for b_type, b_val in all_buffs.items(): buff_lines.append(f"{self.t(b_type)}: +{int(b_val*100)}%")
                buff_lines.append(f"{self.t('SLOTS')}: {len(b.gems)}/2")
                self.render_tooltip(mx+15, my-80, buff_lines); return
        for t in self.towers:
            if math.hypot(t.x - mx, t.y - my) < GRID_SIZE//2: 
                spd_rating = int(1000 / t.fire_rate); base_spd = int(1000 / t.base_fire_rate); gem_names = [self.t(g.name).upper() for g in t.gems]
                lines = [f"--- {self.t(t.type).upper()} ---", f"{self.t('ATK')}: {t.damage} ({self.t('BASE')} {t.base_damage})", f"{self.t('SPD')}: {spd_rating} ({self.t('BASE')} {base_spd})", f"{self.t('RNG')}: {t.range} ({self.t('BASE')} {t.base_range})", f"{self.t('CRIT')}: {int(t.crit_chance*100)}% ({t.crit_mult}X)", f"{self.t('AOE')}: {t.aoe}", f"{self.t('SLOTS')}: {len(t.gems)}/2"]
                if gem_names: lines.append(f"{self.t('SOCKETS')}: {', '.join(gem_names)}")
                self.render_tooltip(mx+15, my-220, lines); return

    def render_tooltip(self, x, y, lines):
        font = self.fonts["tiny"]; final_lines = []
        for rl in lines:
            txt = str(rl).upper(); words = txt.split(' '); curr = ""
            for w in words:
                if font.size(curr + w + " ")[0] <= 300: curr += w + " "
                else:
                    if curr: final_lines.append(curr.strip())
                    curr = w + " "
            if curr: final_lines.append(curr.strip())
        h, w = len(final_lines) * 22 + 15, 320; x, y = max(10, min(x, WIN_WIDTH-w-10)), max(10, min(y, WIN_HEIGHT-h-10)); ctx = self.display_surface
        pygame.draw.rect(ctx, (60, 50, 40), (x-2, y-2, w+4, h+4), border_radius=8)
        pygame.draw.rect(ctx, (245, 235, 210), (x, y, w, h), border_radius=8)
        pygame.draw.rect(ctx, (225, 215, 185), (x+5, y+5, w-10, h-10), border_radius=5)
        for i, l in enumerate(final_lines): self.draw_text_with_shadow(l, font, (60, 40, 20), (x+15, y+8 + i*22), shadow_color=(185, 200, 175))

    def draw_surrounding_forests(self, ctx):
        for tree in sorted(self.trees, key=lambda t: t["pos"][1]):
            px, py = tree["pos"]; sz = tree["size"]; color = tree["color"]
            pygame.draw.circle(ctx, color, (px, py), sz // 2)

    def draw_monster_cave(self, cx, cy, t):
        ctx = self.display_surface; asset = AssetManager.get_instance().env.get("Cave")
        if asset: ctx.blit(pygame.transform.scale(asset, (GRID_SIZE, GRID_SIZE)), (cx-GRID_SIZE//2, cy-GRID_SIZE//2)); return
        pygame.draw.rect(ctx, (20, 40, 25), (cx-GRID_SIZE//2+2, cy-GRID_SIZE//2+2, GRID_SIZE-4, GRID_SIZE-4), border_radius=8)
        pygame.draw.rect(ctx, (10, 20, 10), (cx-GRID_SIZE//2+8, cy-GRID_SIZE//2+8, GRID_SIZE-16, GRID_SIZE-16), border_radius=4)
        eye_c = (155 + int(abs(math.sin(t*4))*100), 40, 40)
        for ex in [-10, 10]: pygame.draw.circle(ctx, eye_c, (cx+ex, cy-4), 4)

    def draw_castle_base(self, pos, t):
        hx, hy, ctx = pos[0], pos[1], self.display_surface; asset = AssetManager.get_instance().env.get("Castle")
        if asset: ctx.blit(pygame.transform.scale(asset, (GRID_SIZE, GRID_SIZE)), (hx-GRID_SIZE//2, hy-GRID_SIZE//2)); return
        pygame.draw.rect(ctx, (210, 220, 210), (hx-25, hy-10, 50, 35)); pygame.draw.rect(ctx, (160, 170, 160), (hx-25, hy-10, 50, 35), 2)
        pygame.draw.polygon(ctx, (50, 110, 50), [(hx-32, hy-10), (hx, hy-45), (hx+32, hy-10)])
        pygame.draw.rect(ctx, (40, 70, 50), (hx-8, hy+12, 16, 15), border_radius=3)

    def draw_powerup_menu(self):
        ctx = self.display_surface; s = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA); s.fill((0,0,0,210)); ctx.blit(s, (0,0))
        title = self.t("POWERUP_MENU"); tx = WIN_WIDTH//2 - self.fonts["medium"].size(title)[0]//2; self.draw_text_with_shadow(title, self.fonts["medium"], (255, 215, 0), (tx, 180))
        timer = f"{self.t('TIME_REMAINING')}: {max(0, self.powerup_timer // FPS)}s"; tsx = WIN_WIDTH//2 - self.fonts["small"].size(timer)[0]//2; self.draw_text_with_shadow(timer, self.fonts["small"], (255, 100, 100), (tsx, 235))
        sx, mx, my = WIN_WIDTH//2-450, *pygame.mouse.get_pos()
        for i, p in enumerate(self.current_powerups):
            cx = sx + i*310; hover = cx <= mx <= cx+280 and 350 <= my <= 650
            pygame.draw.rect(ctx, (50, 50, 70) if hover else (30, 30, 45), (cx, 320, 280, 350), border_radius=15)
            pygame.draw.rect(ctx, (255, 215, 0) if hover else (120, 120, 140), (cx, 320, 280, 350), 4, border_radius=15)
            self.draw_wrapped_text_centered(self.t(p["name"]).upper(), self.fonts["medium"], (255,255,255), cx+140, 360, 260)
            self.draw_wrapped_text_centered(self.t(p["desc"]), self.fonts["small"], (200,200,200), cx+140, 480, 240)
            sc = f"{self.t('PRESS')} [{i+1}]"; self.draw_text_with_shadow(sc, self.fonts["small"], COLOR_ACCENT, (cx+140-self.fonts["small"].size(sc)[0]//2, 600))

    def draw_game_over(self):
        ctx = self.display_surface; s = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA); s.fill((60,0,0,225)); ctx.blit(s, (0,0))
        txt = self.fonts["large"].render(self.t("MISSION FAILED"), True, (255,100,100)); ctx.blit(txt, (WIN_WIDTH//2-txt.get_width()//2, WIN_HEIGHT//2-50))
        st = self.t("PRESS ANY KEY TO RESTART"); self.draw_text_with_shadow(st, self.fonts["medium"], (255, 255, 255), (WIN_WIDTH//2-self.fonts["medium"].size(st)[0]//2, WIN_HEIGHT//2+100))

    def trigger_powerup(self):
        self.powerups_offered = True; self.powerup_timer = (2 if self.is_dev else 15) * FPS
        pool = [
            {"name": "ATTACK BEACON", "type": "BEACON", "data": "ATTACK BEACON", "desc": "BOOSTS ADJACENT DMG BY 25%"},
            {"name": "SPEED BEACON", "type": "BEACON", "data": "SPEED BEACON", "desc": "BOOSTS ADJACENT SPEED BY 25%"},
            {"name": "RANGE BEACON", "type": "BEACON", "data": "RANGE BEACON", "desc": "BOOSTS ADJACENT RANGE BY 25%"},
            {"name": "STR UPGRADE", "type": "CARD", "data": {"name": "STRENGTH CARD", "desc": "GRANT +15% ATK"}, "desc": "STRENGTH CARD"},
            {"name": "AGI UPGRADE", "type": "CARD", "data": {"name": "AGILITY CARD", "desc": "GRANT +15% SPD"}, "desc": "AGILITY CARD"},
            {"name": "VIS UPGRADE", "type": "CARD", "data": {"name": "VISION CARD", "desc": "GRANT +15% RNG"}, "desc": "VISION CARD"},
            {"name": "PRE UPGRADE", "type": "CARD", "data": {"name": "PRECISION CARD", "desc": "GRANT +10% CRIT"}, "desc": "PRECISION CARD"}
        ]
        globals = [
            {"name": "GOLD RUSH", "type": "GLOBAL", "data": "GOLD", "desc": "+500 GOLD INSTANTLY"},
            {"name": "TAX REBATE", "type": "GLOBAL", "data": "TAX", "desc": "MOBS DROP 50% MORE GOLD"}
        ]
        options = pool + globals; weights = [1]*len(pool) + [6]*len(globals); selected = []; temp_options = list(options); temp_weights = list(weights)
        while len(selected) < 3 and temp_options:
            idx = random.choices(range(len(temp_options)), weights=temp_weights, k=1)[0]
            selected.append(temp_options[idx]); temp_options.pop(idx); temp_weights.pop(idx)
        self.current_powerups = selected

    def apply_powerup(self, idx):
        if idx >= len(self.current_powerups): return
        p = self.current_powerups[idx]
        if p["type"] == "GLOBAL":
            if p["data"] == "GOLD": self.wave_manager.gold += 500
            elif p["data"] == "TAX": self.wave_manager.mob_gold_multiplier += 0.5
        elif p["type"] == "CARD": self.wave_manager.inventory.append(InventoryItem(ItemType.STAT_CARD, p["data"]))
        elif p["type"] == "BEACON": self.wave_manager.inventory.append(InventoryItem(ItemType.BEACON, p["data"]))
        self.state = GameState.PLAYING

    def reset_game(self):
        self.wave_manager = WaveManager(self.vfx_manager)
        if self.is_dev: self.wave_manager.gold = 999999
        self.towers, self.beacons, self.selected_type, self.state = [], [], "Earth Cannon", GameState.PLAYING
        self.next_wave_timer = (2 if self.is_dev else 30) * FPS; self.current_powerups, self.powerups_offered, self.selected_inv_idx, self.inv_scroll, self.trash_mode, self.needs_stat_recalc = [], False, -1, 0, False, True

    def process_auto_slots(self):
        self.auto_slot_timer += 1
        if self.auto_slot_timer < 30: return 
        self.auto_slot_timer = 0
        if not self.wave_manager.inventory: return
        for i in range(len(self.wave_manager.inventory)-1, -1, -1):
            item = self.wave_manager.inventory[i]; slotted = False
            if item.item_type == ItemType.GEM:
                for t in self.towers:
                    if t.add_gem(item):
                        self.wave_manager.inventory.pop(i); AssetManager.get_instance().play_sound("powerup")
                        self.needs_stat_recalc = True; slotted = True; break
            elif item.item_type == ItemType.STAT_CARD:
                for b in self.beacons:
                    if b.add_gem(item):
                        self.wave_manager.inventory.pop(i); AssetManager.get_instance().play_sound("powerup")
                        self.needs_stat_recalc = True; slotted = True; break
            if slotted: break

    def run(self):
        while self.running:
            self.handle_events(); self.update(); self.draw()
            self.clock.tick(FPS)
        pygame.quit(); sys.exit()

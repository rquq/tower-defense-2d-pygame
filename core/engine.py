import pygame
import sys
import os
import math
import random
from core.constants import C
from core.wave_manager import WaveManager
from entities.tower import Tower
from entities.beacon import Beacon
from systems.pathfinding import PathSystem
from systems.inventory_items import InventoryItem
from systems.vfx_system import VFXManager
from systems.asset_manager import AssetManager
from systems.spatial_manager import SpatialManager
from core.locales import TEXT, LANGUAGES

class Engine:
    """Lớp điều khiển trung tâm chịu trách nhiệm quản lý vòng lặp trò chơi, xử lý sự kiện và điều phối các hệ thống con."""

    def __init__(self, is_dev=False):
        """Khởi tạo môi trường trò chơi, thiết lập màn hình, nạp tài nguyên và chuẩn bị các thành phần cốt lõi."""
        self.lang_idx = 0
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        self.display_surface = pygame.display.set_mode((C.WIN_WIDTH, C.WIN_HEIGHT))
        pygame.display.set_caption('Fantasy Tower Defense 2D')
        self.clock = pygame.time.Clock()
        AssetManager.get_instance().init()
        try:
            self.fonts = {'tiny': pygame.font.SysFont('calibri', 20), 'small': pygame.font.SysFont('calibri', 28), 'medium': pygame.font.SysFont('calibri', 42), 'large': pygame.font.SysFont('calibri', 96, bold=True), 'mono': pygame.font.SysFont('consolas,monospace', 22, bold=True)}
        except Exception:
            fallback = pygame.font.match_font('consolas,monospace')
            self.fonts = {f: pygame.font.SysFont(fallback, s) for f, s in zip(['tiny', 'small', 'medium', 'large'], [20, 28, 42, 96])}
            self.fonts['mono'] = pygame.font.SysFont('consolas,monospace', 22, bold=True)
        self.path_system = PathSystem()
        self.vfx_manager = VFXManager()
        self.spatial_manager = SpatialManager(cell_size=200)
        self.wave_manager = WaveManager(self.vfx_manager)
        self.needs_stat_recalc = True
        self.is_dev = is_dev
        if is_dev:
            self.wave_manager.gold = 999999
        self.towers = []
        self.beacons = []
        self.selected_type = 'Earth Cannon'
        self.state = C.GameState.MENU
        self.running = True
        self.next_wave_timer = (2 if is_dev else 30) * C.FPS
        self.current_powerups = []
        self.powerups_offered = False
        self.powerup_timer = 0
        self.selected_inv_idx = -1
        self.inv_scroll = 0
        self.trash_mode = False
        self.auto_slot_mode = False
        self.auto_slot_timer = 0
        self.trees = []
        self.generate_trees()
        self.background_surface = pygame.Surface((C.WIN_WIDTH, C.WIN_HEIGHT))
        self.render_static_background()

    def t(self, key):
        """Hàm hỗ trợ dịch thuật đa ngôn ngữ dựa trên từ khóa cung cấp.

Thông số:
    key là từ khóa cần được dịch"""
        return TEXT[LANGUAGES[self.lang_idx]].get(key, key)

    def generate_trees(self):
        """Tạo ra dữ liệu vị trí và màu sắc cho các cây cối xung quanh khu vực chơi để trang trí bản đồ."""
        self.trees = []
        for _ in range(1200):
            side = random.choices(['L', 'R', 'T'], weights=[1, 1, 4])[0]
            size = random.randint(70, 130)
            rad = size // 2
            if side == 'L':
                x, y = (random.randint(-rad, C.OFFSET_X), random.randint(-rad, C.WIN_HEIGHT + rad))
            elif side == 'R':
                x, y = (random.randint(C.WIN_WIDTH - C.OFFSET_X, C.WIN_WIDTH + rad), random.randint(-rad, C.WIN_HEIGHT + rad))
            else:
                x, y = (random.randint(-rad, C.WIN_WIDTH + rad), random.randint(-rad, C.OFFSET_Y))
            self.trees.append(self._create_tree_data(x, y, size))

    def _create_tree_data(self, bx, by, size):
        """Tạo ra các thuộc tính ngẫu nhiên cho một cái cây cụ thể dựa trên tọa độ của nó."""
        r = random.Random(bx * 7 + by * 13)
        color = (r.randint(35, 65), r.randint(110, 155), r.randint(35, 65))
        return {'pos': (bx, by), 'size': size, 'color': color}

    def render_static_background(self):
        """Vẽ và lưu trữ các thành phần tĩnh của bản đồ như nền cỏ, đường đi và các chi tiết trang trí vào một bề mặt riêng để tối ưu hiệu năng."""
        ctx = self.background_surface
        start_c = -(C.OFFSET_X // C.GRID_SIZE) - 2
        end_c = C.GRID_COLS + (C.WIN_WIDTH - (C.OFFSET_X + C.GRID_COLS * C.GRID_SIZE)) // C.GRID_SIZE + 4
        start_r = -(C.OFFSET_Y // C.GRID_SIZE) - 2
        end_r = C.GRID_ROWS + (C.WIN_HEIGHT - (C.OFFSET_Y + C.GRID_ROWS * C.GRID_SIZE)) // C.GRID_SIZE + 4
        for c in range(start_c, end_c):
            for r in range(start_r, end_r):
                gx, gy = (C.OFFSET_X + c * C.GRID_SIZE, C.OFFSET_Y + r * C.GRID_SIZE)
                color = (85, 165, 65) if (c + r) % 2 == 0 else (95, 175, 75)
                ctx.fill(color, (gx, gy, C.GRID_SIZE, C.GRID_SIZE))
                rnd = random.Random(c * 777 + r * 333)
                if rnd.random() < 0.3:
                    for _ in range(rnd.randint(1, 3)):
                        nx, ny = (gx + rnd.randint(5, C.GRID_SIZE - 5), gy + rnd.randint(5, C.GRID_SIZE - 5))
                        pygame.draw.line(ctx, (60, 120, 40), (nx, ny), (nx, ny - rnd.randint(4, 8)), 2)
        for c in range(C.GRID_COLS):
            for r in range(C.GRID_ROWS):
                gx, gy = (C.OFFSET_X + c * C.GRID_SIZE, C.OFFSET_Y + r * C.GRID_SIZE)
                pygame.draw.rect(ctx, (70, 140, 40), (gx, gy, C.GRID_SIZE, C.GRID_SIZE), 1)
                if (c, r) in self.path_system.walkable_tiles:
                    ctx.fill((230, 205, 140), (gx, gy, C.GRID_SIZE, C.GRID_SIZE))
                    rnd = random.Random(c * 100 + r)
                    for _ in range(rnd.randint(4, 7)):
                        px, py = (gx + rnd.randint(5, C.GRID_SIZE - 5), gy + rnd.randint(5, C.GRID_SIZE - 5))
                        pygame.draw.circle(ctx, (170, 150, 110), (px, py), rnd.randint(1, 3))
                else:
                    rnd = random.Random(c * 777 + r * 333)
                    for _ in range(rnd.randint(8, 14)):
                        nx, ny = (gx + rnd.randint(3, C.GRID_SIZE - 3), gy + rnd.randint(5, C.GRID_SIZE - 3))
                        h = rnd.randint(8, 16)
                        grass_color = (rnd.randint(60, 100), rnd.randint(160, 210), rnd.randint(50, 80))
                        shadow_color = (max(0, grass_color[0] - 40), max(0, grass_color[1] - 40), max(0, grass_color[2] - 40))
                        pygame.draw.line(ctx, shadow_color, (nx + 1, ny), (nx + 1, ny - h + 1), 2)
                        pygame.draw.line(ctx, grass_color, (nx, ny), (nx + rnd.randint(-1, 1), ny - h), 2)
                        if h > 10:
                            pygame.draw.circle(ctx, (min(255, grass_color[0] + 30), min(255, grass_color[1] + 30), min(255, grass_color[2] + 30)), (nx, ny - h), 2)
                    for _ in range(rnd.randint(2, 4)):
                        nx, ny = (gx + rnd.randint(5, C.GRID_SIZE - 5), gy + rnd.randint(5, C.GRID_SIZE - 5))
                        h = rnd.randint(14, 22)
                        grass_color = (rnd.randint(40, 80), rnd.randint(140, 190), rnd.randint(40, 70))
                        shadow_color = (max(0, grass_color[0] - 30), max(0, grass_color[1] - 30), max(0, grass_color[2] - 30))
                        for ang in [-0.4, 0, 0.4]:
                            tx, ty = (nx + math.sin(ang) * h, ny - math.cos(ang) * h)
                            pygame.draw.line(ctx, shadow_color, (nx + 1, ny), (tx + 1, ty + 1), 3)
                            pygame.draw.line(ctx, grass_color, (nx, ny), (tx, ty), 3)
                    if rnd.random() < 0.25:
                        for _ in range(rnd.randint(1, 2)):
                            fx, fy = (gx + rnd.randint(10, C.GRID_SIZE - 10), gy + rnd.randint(10, C.GRID_SIZE - 10))
                            f_color = rnd.choice([(220, 80, 80), (80, 150, 220), (180, 80, 220), (255, 230, 100)])
                            pygame.draw.line(ctx, (40, 100, 30), (fx, fy), (fx, fy - 6), 2)
                            pygame.draw.circle(ctx, f_color, (fx, fy - 6), 5)
                            pygame.draw.circle(ctx, (255, 255, 255), (fx, fy - 6), 2)
        for c in range(C.GRID_COLS + 1):
            pygame.draw.line(ctx, (70, 140, 40), (C.OFFSET_X + c * C.GRID_SIZE, C.OFFSET_Y), (C.OFFSET_X + c * C.GRID_SIZE, C.OFFSET_Y + C.GRID_ROWS * C.GRID_SIZE), 1)
        for r in range(C.GRID_ROWS + 1):
            pygame.draw.line(ctx, (70, 140, 40), (C.OFFSET_X, C.OFFSET_Y + r * C.GRID_SIZE), (C.OFFSET_X + C.GRID_COLS * C.GRID_SIZE, C.OFFSET_Y + r * C.GRID_SIZE), 1)
        self.draw_surrounding_forests(ctx)

    def handle_events(self):
        """Lắng nghe và xử lý các sự kiện từ người dùng như phím bấm, chuột và yêu cầu thoát trò chơi."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if self.state == C.GameState.MENU:
                    if event.key == pygame.K_l:
                        self.lang_idx = (self.lang_idx + 1) % len(LANGUAGES)
                    else:
                        self.state = C.GameState.PLAYING
                elif self.state == C.GameState.PLAYING:
                    keys = {pygame.K_1: 'Earth Cannon', pygame.K_2: 'Wind Ballista', pygame.K_3: 'Fire Mortar', pygame.K_4: 'Storm Spire', pygame.K_5: 'Frost Cannon'}
                    if event.key in keys:
                        self.selected_type = keys[event.key]
                        self.trash_mode = False
                        self.selected_inv_idx = -1
                    if event.key == pygame.K_n:
                        self.force_start_wave()
                    if event.key == pygame.K_t:
                        self.trash_mode = not self.trash_mode
                    if event.key == pygame.K_ESCAPE:
                        self.selected_inv_idx = -1
                        self.trash_mode = False
                    if self.is_dev:
                        if event.key == pygame.K_g:
                            self.wave_manager.gold += 10000
                        if event.key == pygame.K_h:
                            self.wave_manager.health = 100
                        if event.key == pygame.K_k:
                            for e in self.wave_manager.enemies:
                                e.health = 0
                elif self.state == C.GameState.POWERUP:
                    if pygame.K_1 <= event.key <= pygame.K_3:
                        self.apply_powerup(event.key - pygame.K_1)
                elif self.state == C.GameState.GAME_OVER:
                    self.reset_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_click()
                elif event.button == 4:
                    self.inv_scroll = max(0, self.inv_scroll - 1)
                elif event.button == 5:
                    self.inv_scroll = min(max(0, len(self.wave_manager.inventory) - 8), self.inv_scroll + 1)

    def handle_click(self):
        """Phân tích vị trí click chuột để thực hiện các hành động như xây tháp, chọn vật phẩm hoặc tương tác với menu."""
        mx, my = pygame.mouse.get_pos()
        panel_y = C.WIN_HEIGHT - C.UI_BOTTOM_HEIGHT
        if self.state == C.GameState.MENU:
            lw = self.fonts['small'].size(self.t('LANGUAGE'))[0] + 40
            lx, ly = (C.WIN_WIDTH // 2 - lw // 2, C.WIN_HEIGHT // 2 + 120)
            if lx <= mx <= lx + lw and ly <= my <= ly + 40:
                self.lang_idx = (self.lang_idx + 1) % len(LANGUAGES)
                AssetManager.get_instance().play_sound('ui_click')
            else:
                self.state = C.GameState.PLAYING
            return
        if self.state == C.GameState.POWERUP:
            start_x = C.WIN_WIDTH // 2 - 450
            for i in range(3):
                if start_x + i * 310 <= mx <= start_x + i * 310 + 280 and 350 <= my <= 650:
                    AssetManager.get_instance().play_sound('powerup')
                    self.apply_powerup(i)
                    return
            return
        if self.state == C.GameState.PLAYING:
            if 60 <= mx <= 160 and panel_y + 25 <= my <= panel_y + 125:
                AssetManager.get_instance().play_sound('ui_click')
                self.trash_mode = not self.trash_mode
                self.selected_inv_idx = -1
                return
            for i, tower_type in enumerate(C.TOWER_STATS.keys()):
                bx = 180 + i * 115
                if bx <= mx <= bx + 100 and panel_y + 20 <= my <= panel_y + 120:
                    AssetManager.get_instance().play_sound('ui_click')
                    self.selected_type = tower_type
                    self.selected_inv_idx = -1
                    self.trash_mode = False
                    return
            if 810 <= mx <= 930 and panel_y + 25 <= my <= panel_y + 65:
                self.auto_slot_mode = not self.auto_slot_mode
                AssetManager.get_instance().play_sound('ui_click')
                return
            for i in range(min(16, len(self.wave_manager.inventory))):
                item_idx = i + self.inv_scroll
                if item_idx >= len(self.wave_manager.inventory):
                    break
                if 810 + i * 65 <= mx <= 810 + i * 65 + 60 and panel_y + 80 <= my <= panel_y + 140:
                    AssetManager.get_instance().play_sound('ui_click')
                    self.selected_inv_idx = item_idx
                    self.trash_mode = False
                    return
            if not self.wave_manager.is_wave_active and C.WIN_WIDTH - 250 <= mx <= C.WIN_WIDTH - 30 and (8 <= my <= 40):
                self.force_start_wave()
                return
            if my > panel_y:
                return
            if self.trash_mode:
                for t in self.towers[:]:
                    if math.hypot(t.x - mx, t.y - my) < C.GRID_SIZE // 2:
                        AssetManager.get_instance().play_sound('sell')
                        self.towers.remove(t)
                        self.needs_stat_recalc = True
                        return
                for b in self.beacons[:]:
                    if math.hypot(b.x - mx, b.y - my) < C.GRID_SIZE // 2:
                        AssetManager.get_instance().play_sound('sell')
                        self.beacons.remove(b)
                        self.needs_stat_recalc = True
                        return
            elif self.selected_inv_idx != -1:
                item = self.wave_manager.inventory[self.selected_inv_idx]
                if item.item_type == C.ItemType.BEACON:
                    gx, gy = ((mx - C.OFFSET_X) // C.GRID_SIZE, (my - C.OFFSET_Y) // C.GRID_SIZE)
                    px, py = (gx * C.GRID_SIZE + C.OFFSET_X + C.GRID_SIZE // 2, gy * C.GRID_SIZE + C.OFFSET_Y + C.GRID_SIZE // 2)
                    if self.is_valid_placement(gx, gy, px, py):
                        AssetManager.get_instance().play_sound('place_tower')
                        self.beacons.append(Beacon(px, py, item.name))
                        self.wave_manager.inventory.pop(self.selected_inv_idx)
                        self.selected_inv_idx = -1
                        self.needs_stat_recalc = True
                        return
                elif item.item_type == C.ItemType.STAT_CARD:
                    for b in self.beacons:
                        if math.hypot(b.x - mx, b.y - my) < C.GRID_SIZE // 2:
                            if b.add_gem(item):
                                AssetManager.get_instance().play_sound('powerup')
                                self.wave_manager.inventory.pop(self.selected_inv_idx)
                                self.selected_inv_idx = -1
                                self.needs_stat_recalc = True
                                return
                elif item.item_type == C.ItemType.GEM:
                    for t in self.towers:
                        if math.hypot(t.x - mx, t.y - my) < C.GRID_SIZE // 2:
                            if t.add_gem(item):
                                AssetManager.get_instance().play_sound('powerup')
                                self.wave_manager.inventory.pop(self.selected_inv_idx)
                                self.selected_inv_idx = -1
                                self.needs_stat_recalc = True
                                return
            else:
                gx, gy = ((mx - C.OFFSET_X) // C.GRID_SIZE, (my - C.OFFSET_Y) // C.GRID_SIZE)
                px, py = (gx * C.GRID_SIZE + C.OFFSET_X + C.GRID_SIZE // 2, gy * C.GRID_SIZE + C.OFFSET_Y + C.GRID_SIZE // 2)
                if self.is_valid_placement(gx, gy, px, py):
                    cost = C.TOWER_STATS[self.selected_type]['cost']
                    if self.wave_manager.gold >= cost:
                        AssetManager.get_instance().play_sound('place_tower')
                        self.wave_manager.gold -= cost
                        self.towers.append(Tower(px, py, self.selected_type))
                        self.needs_stat_recalc = True

    def is_valid_placement(self, gx, gy, px, py):
        """Kiểm tra xem một vị trí trên bản đồ có cho phép xây dựng công trình hay không.

Thông số:
    gx là tọa độ cột trên lưới
    gy là tọa độ hàng trên lưới
    px là tọa độ X pixel tương ứng
    py là tọa độ Y pixel tương ứng"""
        if not (0 <= gx < C.GRID_COLS and 0 <= gy < C.GRID_ROWS) or (gx, gy) in self.path_system.walkable_tiles:
            return False
        for t in self.towers:
            if math.hypot(t.x - px, t.y - py) < C.GRID_SIZE:
                return False
        for b in self.beacons:
            if math.hypot(b.x - px, b.y - py) < C.GRID_SIZE:
                return False
        return True

    def calculate_adjacency_buffs(self):
        """Tính toán và áp dụng các chỉ số tăng cường cho tháp khi chúng được đặt cạnh các công trình hỗ trợ Beacon."""
        beacon_map = {((int(b.x) - C.OFFSET_X) // C.GRID_SIZE, (int(b.y) - C.OFFSET_Y) // C.GRID_SIZE): b for b in self.beacons}
        for t in self.towers:
            tgx, tgy = ((int(t.x) - C.OFFSET_X) // C.GRID_SIZE, (int(t.y) - C.OFFSET_Y) // C.GRID_SIZE)
            buff_list = []
            for nb in [(tgx + 1, tgy), (tgx - 1, tgy), (tgx, tgy + 1), (tgx, tgy - 1)]:
                if nb in beacon_map:
                    beacon = beacon_map[nb]
                    b_buffs = beacon.get_all_buffs()
                    for b_type, b_val in b_buffs.items():
                        stat_map = {'ATK': 'damage', 'SPD': 'fire_rate', 'RNG': 'range', 'CRIT': 'crit'}
                        buff_list.append((stat_map[b_type], b_val))
            t.recalculate(buff_list)

    def force_start_wave(self):
        """Kích hoạt đợt tấn công mới ngay lập tức mà không cần đợi thời gian đếm ngược."""
        if not self.wave_manager.is_wave_active and self.state == C.GameState.PLAYING:
            AssetManager.get_instance().play_sound('wave_start')
            self.wave_manager.start_wave(self.path_system.get_enemy_waypoints())
            self.next_wave_timer = int(20 * C.FPS * self.wave_manager.wave_interval_multiplier)

    def update(self):
        """Cập nhật trạng thái logic của toàn bộ các thực thể và hệ thống trong mỗi khung hình."""
        if self.state == C.GameState.PLAYING:
            self.vfx_manager.update()
            self.wave_manager.update()
            self.spatial_manager.clear()
            for enemy in self.wave_manager.enemies:
                self.spatial_manager.add_entity(enemy)
            if self.needs_stat_recalc:
                self.calculate_adjacency_buffs()
                self.needs_stat_recalc = False
            for tower in self.towers:
                tower.update(self.spatial_manager, self.vfx_manager)
            for b in self.beacons:
                bgx, bgy = ((int(b.x) - C.OFFSET_X) // C.GRID_SIZE, (int(b.y) - C.OFFSET_Y) // C.GRID_SIZE)
                for t in self.towers:
                    tgx, tgy = ((int(t.x) - C.OFFSET_X) // C.GRID_SIZE, (int(t.y) - C.OFFSET_Y) // C.GRID_SIZE)
                    if abs(tgx - bgx) + abs(tgy - bgy) == 1 and random.random() < 0.15:
                        self.vfx_manager.spawn_link_particle(b.x, b.y, t.x, t.y, b.color)
            if self.auto_slot_mode:
                self.process_auto_slots()
            if self.wave_manager.health <= 0:
                if self.state != C.GameState.GAME_OVER:
                    AssetManager.get_instance().play_sound('game_over')
                self.state = C.GameState.GAME_OVER
            elif not self.wave_manager.is_wave_active:
                if self.wave_manager.wave_number % C.BLESSING_INTERVAL == 0 and (not self.powerups_offered):
                    self.state = C.GameState.POWERUP
                    self.trigger_powerup()
                    return
                self.next_wave_timer -= 1
                if self.next_wave_timer <= 0:
                    self.force_start_wave()
            else:
                self.powerups_offered = False
                self.next_wave_timer = (2 if self.is_dev else 30) * C.FPS
        elif self.state == C.GameState.POWERUP:
            self.powerup_timer -= 1
            if self.powerup_timer <= 0:
                self.state = C.GameState.PLAYING

    def draw(self):
        """Thực hiện việc vẽ tất cả các thành phần lên màn hình hiển thị."""
        temp_surface = pygame.Surface((C.WIN_WIDTH, C.WIN_HEIGHT))
        old_surface, self.display_surface = (self.display_surface, temp_surface)
        if self.state == C.GameState.MENU:
            self.draw_menu()
        elif self.state in [C.GameState.PLAYING, C.GameState.POWERUP, C.GameState.GAME_OVER]:
            self.draw_playing()
            if self.state == C.GameState.POWERUP:
                self.draw_powerup_menu()
            elif self.state == C.GameState.GAME_OVER:
                self.display_surface.blit(self.apply_blur(self.display_surface, 3, 2), (0, 0))
                self.draw_game_over()
            self.draw_tooltips()
        self.display_surface = old_surface
        self.display_surface.blit(temp_surface, (0, 0))
        pygame.display.flip()

    def apply_blur(self, surface, amount=3, passes=2):
        """Tạo hiệu ứng làm mờ cho một bề mặt hình ảnh cụ thể.

Thông số:
    surface là hình ảnh cần làm mờ
    amount là mức độ làm mờ
    passes là số lần lặp lại hiệu ứng"""
        w, h = surface.get_size()
        blurred = surface
        for _ in range(passes):
            small = pygame.transform.smoothscale(blurred, (w // amount, h // amount))
            blurred = pygame.transform.smoothscale(small, (w, h))
        return blurred

    def draw_text_with_shadow(self, text, font, color, pos, shadow_color=(0, 0, 0, 180), offset=(2, 2)):
        """Vẽ văn bản có kèm hiệu ứng đổ bóng để tăng độ rõ nét.

Thông số:
    text là nội dung văn bản
    font là bộ phông chữ sử dụng
    color là màu sắc chính
    pos là vị trí vẽ"""
        self.display_surface.blit(font.render(text, True, shadow_color), (pos[0] + offset[0], pos[1] + offset[1]))
        self.display_surface.blit(font.render(text, True, color), pos)

    def draw_wrapped_text_centered(self, text, font, color, center_x, start_y, max_width):
        """Vẽ văn bản tự động xuống dòng và căn giữa trong một vùng giới hạn.

Thông số:
    text là nội dung văn bản dài
    font là bộ phông chữ sử dụng
    color là màu sắc văn bản
    center_x là vị trí ngang trung tâm
    start_y là vị trí dọc bắt đầu
    max_width là chiều rộng tối đa cho phép"""
        words = text.split(' ')
        lines = []
        current_line = ''
        for word in words:
            test_line = current_line + word + ' '
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + ' '
        if current_line:
            lines.append(current_line.strip())
        line_height = font.get_linesize()
        for i, line in enumerate(lines):
            tw = font.size(line)[0]
            self.draw_text_with_shadow(line, font, color, (center_x - tw // 2, start_y + i * line_height))

    def draw_menu(self):
        """Vẽ giao diện màn hình chính khi người chơi mới vào trò chơi."""
        ctx = self.display_surface
        ctx.blit(self.background_surface, (0, 0))
        ctx.blit(self.apply_blur(ctx, 4, 3), (0, 0))
        s = pygame.Surface((C.WIN_WIDTH, C.WIN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 160))
        ctx.blit(s, (0, 0))
        title = self.t('TITLE')
        font_l = self.fonts['large']
        self.draw_text_with_shadow(title, font_l, C.COLOR_ACCENT, (C.WIN_WIDTH // 2 - font_l.size(title)[0] // 2, C.WIN_HEIGHT // 2 - 100), offset=(4, 4))
        start = self.t('PRESS_START')
        font_m = self.fonts['medium']
        self.draw_text_with_shadow(start, font_m, C.COLOR_UI_TEXT, (C.WIN_WIDTH // 2 - font_m.size(start)[0] // 2, C.WIN_HEIGHT // 2 + 50))
        lang = self.t('LANGUAGE')
        font_s = self.fonts['small']
        lw = font_s.size(lang)[0] + 40
        lx, ly = (C.WIN_WIDTH // 2 - lw // 2, C.WIN_HEIGHT // 2 + 120)
        mx, my = pygame.mouse.get_pos()
        hover = lx <= mx <= lx + lw and ly <= my <= ly + 40
        pygame.draw.rect(ctx, (70, 120, 70) if hover else (50, 100, 50), (lx, ly, lw, 40), border_radius=5)
        pygame.draw.rect(ctx, (200, 200, 150), (lx, ly, lw, 40), 2, border_radius=5)
        self.draw_text_with_shadow(lang, font_s, C.COLOR_UI_TEXT, (lx + 20, ly + 5))

    def draw_playing(self):
        """Vẽ toàn bộ thế giới trò chơi trong khi đang diễn ra trận đấu."""
        ctx = self.display_surface
        ctx.blit(self.background_surface, (0, 0))
        t = pygame.time.get_ticks() / 1000
        self.draw_monster_cave(*C.get_pixel_pos(0, 4), t)
        self.draw_castle_base(C.get_pixel_pos(27, 9), t)
        shadow_surf = pygame.Surface((C.WIN_WIDTH, C.WIN_HEIGHT), pygame.SRCALPHA)
        for b in self.beacons:
            x, y = (int(b.x), int(b.y))
            pts = [(x, y - 20), (x + 20, y), (x, y + 20), (x - 20, y)]
            pygame.draw.polygon(shadow_surf, (0, 0, 0, 70), [(p[0] + 5, p[1] + 5) for p in pts])
        for t in self.towers:
            Tower.draw_design(shadow_surf, t.x, t.y, t.type, (0, 0, 0), t.angle, is_shadow=True)
        ctx.blit(shadow_surf, (0, 0))
        for b in self.beacons:
            b.draw(ctx)
        for tower in self.towers:
            tower.draw(ctx)
        self.wave_manager.draw(ctx)
        self.vfx_manager.draw(ctx, self.fonts['tiny'])
        self.draw_ui()
        if self.state == C.GameState.PLAYING:
            self.draw_placement_preview()

    def draw_placement_preview(self):
        """Hiển thị hình ảnh xem trước của công trình hoặc vật phẩm tại vị trí chuột đang trỏ tới."""
        mx, my = pygame.mouse.get_pos()
        gx, gy = ((mx - C.OFFSET_X) // C.GRID_SIZE, (my - C.OFFSET_Y) // C.GRID_SIZE)
        if not (0 <= gx < C.GRID_COLS and 0 <= gy < C.GRID_ROWS):
            return
        px, py = (gx * C.GRID_SIZE + C.OFFSET_X + C.GRID_SIZE // 2, gy * C.GRID_SIZE + C.OFFSET_Y + C.GRID_SIZE // 2)
        ctx = self.display_surface
        if self.trash_mode:
            s = pygame.Surface((C.GRID_SIZE, C.GRID_SIZE), pygame.SRCALPHA)
            s.fill((200, 50, 50, 100))
            ctx.blit(s, (px - C.GRID_SIZE // 2, py - C.GRID_SIZE // 2))
            return
        if self.selected_inv_idx != -1:
            item = self.wave_manager.inventory[self.selected_inv_idx]
            if item.item_type == C.ItemType.BEACON:
                v = self.is_valid_placement(gx, gy, px, py)
            elif item.item_type == C.ItemType.STAT_CARD:
                v = any(((int(b.x) - C.OFFSET_X) // C.GRID_SIZE == gx and (int(b.y) - C.OFFSET_Y) // C.GRID_SIZE == gy for b in self.beacons))
            else:
                v = any(((int(t.x) - C.OFFSET_X) // C.GRID_SIZE == gx and (int(t.y) - C.OFFSET_Y) // C.GRID_SIZE == gy for t in self.towers))
            s = pygame.Surface((C.GRID_SIZE, C.GRID_SIZE), pygame.SRCALPHA)
            s.fill(C.COLOR_VALID if v else C.COLOR_INVALID)
            ctx.blit(s, (px - C.GRID_SIZE // 2, py - C.GRID_SIZE // 2))
            return
        if C.OFFSET_Y < my < C.WIN_HEIGHT - C.UI_BOTTOM_HEIGHT:
            v = self.is_valid_placement(gx, gy, px, py)
            s = pygame.Surface((C.GRID_SIZE, C.GRID_SIZE), pygame.SRCALPHA)
            s.fill(C.COLOR_VALID if v else C.COLOR_INVALID)
            ctx.blit(s, (px - C.GRID_SIZE // 2, py - C.GRID_SIZE // 2))
            pygame.draw.circle(ctx, (255, 255, 255, 40), (px, py), C.TOWER_STATS[self.selected_type]['range'], 1)

    def draw_ui(self):
        """Vẽ các thành phần giao diện người dùng như thanh trạng thái, cửa hàng và kho đồ."""
        ctx = self.display_surface
        hud_gray = (50, 50, 60)
        self.draw_hud_module(30, 8, 160, f"{self.t('WAVE')}: {self.wave_manager.wave_number}", hud_gray)
        if self.wave_manager.is_wave_active:
            self.draw_hud_module(210, 8, 160, f"{self.t('MOBS')}: {self.wave_manager.enemies_to_spawn + len(self.wave_manager.enemies)}", hud_gray, (255, 100, 100))
        self.draw_hud_module(C.WIN_WIDTH // 2 - 110, 8, 220, f"{self.t('GOLD')}: {int(self.wave_manager.gold)}", hud_gray, (255, 215, 0))
        if not self.wave_manager.is_wave_active:
            self.draw_hud_module(C.WIN_WIDTH - 420, 8, 150, f"{self.t('IN')}: {max(0, self.next_wave_timer // C.FPS)}s", (40, 40, 50))
            bx = C.WIN_WIDTH - 250
            pygame.draw.rect(ctx, (40, 150, 40), (bx, 8, 220, 32), border_radius=5)
            pygame.draw.rect(ctx, (200, 180, 50), (bx, 8, 220, 32), 2, border_radius=5)
            txt = self.t('START_NOW')
            tw = self.fonts['mono'].size(txt)[0]
            self.draw_text_with_shadow(txt, self.fonts['mono'], (255, 255, 255), (bx + 110 - tw // 2, 12))
        py = C.WIN_HEIGHT - C.UI_BOTTOM_HEIGHT
        sx, sw, sy, sh = (10, C.WIN_WIDTH - 20, py + 5, C.UI_BOTTOM_HEIGHT - 10)
        pygame.draw.rect(ctx, (80, 60, 40), (sx - 2, sy - 2, sw + 4, sh + 4), border_radius=15)
        pygame.draw.rect(ctx, (240, 225, 190), (sx, sy, sw, sh), border_radius=15)
        pygame.draw.rect(ctx, (220, 205, 170), (sx + 8, sy + 8, sw - 16, sh - 16), border_radius=10)
        for rx, ry in [(sx + 15, sy + 15), (sx + sw - 15, sy + 15), (sx + 15, sy + sh - 15), (sx + sw - 15, sy + sh - 15)]:
            pygame.draw.circle(ctx, (120, 110, 100), (rx, ry), 5)
            pygame.draw.circle(ctx, (60, 50, 40), (rx, ry), 5, 1)
        mx, my = pygame.mouse.get_pos()
        bx, by = (60, py + 25)
        hover = bx <= mx <= bx + 100 and by <= my <= by + 100
        pygame.draw.rect(ctx, (230, 70, 70) if self.trash_mode else (80, 130, 80) if hover else (60, 100, 60), (bx, by, 100, 100), border_radius=10)
        pygame.draw.rect(ctx, (255, 215, 0) if self.trash_mode else (40, 70, 40), (bx, by, 100, 100), 4 if self.trash_mode else 3, border_radius=10)
        bc, ix, iy = ((60, 60, 60) if self.trash_mode else (180, 40, 40), bx + 50, by + 50)
        pygame.draw.rect(ctx, bc, (ix - 20, iy - 15, 40, 35), border_radius=3)
        pygame.draw.rect(ctx, bc, (ix - 25, iy - 22, 50, 8), border_radius=2)
        pygame.draw.rect(ctx, bc, (ix - 8, iy - 28, 16, 8), border_radius=2)
        lc = (230, 70, 70) if self.trash_mode else (130, 130, 130)
        for lx in [-10, 0, 10]:
            pygame.draw.rect(ctx, lc, (ix + lx - 2, iy - 8, 4, 22), border_radius=1)
        for i, (name, s) in enumerate(C.TOWER_STATS.items()):
            bx, by = (180 + i * 115, py + 25)
            hover = bx <= mx <= bx + 100 and by <= my <= by + 100
            sel = name == self.selected_type and (not self.trash_mode) and (self.selected_inv_idx == -1)
            pygame.draw.rect(ctx, (100, 150, 100) if sel else (80, 120, 80) if hover else (70, 110, 70), (bx, by, 100, 100), border_radius=8)
            pygame.draw.rect(ctx, (255, 215, 0) if sel else (40, 80, 40), (bx, by, 100, 100), 5 if sel else 3, border_radius=8)
            Tower.draw_design(ctx, bx + 50, by + 40, name, s['color'], -math.pi / 4, scale=1.2)
            rx, ry, rw, rh = (bx + 17.5, by + 75, 65, 26)
            pygame.draw.rect(ctx, (245, 235, 210), (rx, ry, rw, rh), border_radius=6)
            pygame.draw.rect(ctx, (60, 100, 60), (rx, ry, rw, rh), 2, border_radius=6)
            ct = self.fonts['mono'].render(f"${s['cost']}", True, (40, 80, 40))
            ctx.blit(ct, (bx + 50 - ct.get_width() // 2, ry + (rh - ct.get_height()) // 2))
        pygame.draw.line(ctx, (180, 170, 140), (780, py + 20), (780, py + C.UI_BOTTOM_HEIGHT - 20), 2)
        ax, ay, aw, ah = (810, py + 25, 120, 40)
        ahover = ax <= mx <= ax + aw and ay <= my <= ay + ah
        pygame.draw.rect(ctx, (60, 150, 60) if self.auto_slot_mode else (120, 80, 80) if ahover else (100, 60, 60), (ax, ay, aw, ah), border_radius=8)
        pygame.draw.rect(ctx, (255, 215, 0) if self.auto_slot_mode else (40, 40, 50), (ax, ay, aw, ah), 2, border_radius=8)
        atxt = self.t('AUTO') + ': ' + (self.t('ON') if self.auto_slot_mode else self.t('OFF'))
        af = self.fonts['tiny'].render(atxt, True, (255, 255, 255))
        ctx.blit(af, (ax + (aw - af.get_width()) // 2, ay + (ah - af.get_height()) // 2))
        sy = py + 25
        it = f"{self.t('INVENTORY')} ({len(self.wave_manager.inventory)})"
        self.draw_text_with_shadow(it, self.fonts['small'], (40, 80, 40), (950, sy + 5), shadow_color=(210, 200, 180))
        for i in range(16):
            idx = i + self.inv_scroll
            if idx >= len(self.wave_manager.inventory):
                break
            item = self.wave_manager.inventory[idx]
            gx, gy = (810 + i * 65, sy + 55)
            hover = gx <= mx <= gx + 60 and gy <= my <= gy + 60
            sel = idx == self.selected_inv_idx
            pygame.draw.rect(ctx, (120, 160, 120) if sel else (100, 140, 100) if hover else (80, 120, 80), (gx, gy, 60, 60), border_radius=5)
            pygame.draw.rect(ctx, (255, 215, 0) if sel else (50, 90, 50), (gx, gy, 60, 60), 3 if sel else 2, border_radius=5)
            ix, iy = (gx + 30, gy + 30)
            from systems.asset_manager import AssetManager
            mgr = AssetManager.get_instance()
            if item.item_type == C.ItemType.GEM:
                key = f'GEM_{item.data}'
                if key in mgr.icons:
                    gem_asset = mgr.icons[key]
                    tw, th = gem_asset.get_size()
                    target_h = 52
                    target_w = int(tw / th * target_h)
                    scaled_gem = pygame.transform.scale(gem_asset, (target_w, target_h))
                    ctx.blit(scaled_gem, (ix - target_w // 2, iy - target_h // 2))
                else:
                    pts = [(ix, iy - 12), (ix + 12, iy), (ix, iy + 12), (ix - 12, iy)]
                    pygame.draw.polygon(ctx, item.color, pts)
                    pygame.draw.polygon(ctx, (255, 255, 255), pts, 1)
            elif item.item_type == C.ItemType.BEACON:
                pygame.draw.circle(ctx, item.color, (ix, iy), 12, 3)
                pygame.draw.circle(ctx, (255, 255, 255), (ix, iy), 4)
            elif item.item_type == C.ItemType.STAT_CARD:
                key = 'CARD_STRENGTH'
                if 'STRENGTH' in item.name:
                    key = 'CARD_STRENGTH'
                elif 'AGILITY' in item.name:
                    key = 'CARD_AGILITY'
                elif 'VISION' in item.name:
                    key = 'CARD_VISION'
                elif 'PRECISION' in item.name:
                    key = 'CARD_PRECISION'
                if key in mgr.icons:
                    book_asset = mgr.icons[key]
                    tw, th = book_asset.get_size()
                    target_h = 52
                    target_w = int(tw / th * target_h)
                    scaled_book = pygame.transform.scale(book_asset, (target_w, target_h))
                    ctx.blit(scaled_book, (ix - target_w // 2, iy - target_h // 2))
                    ctx.blit(scaled_book, (ix - target_w // 2, iy - target_h // 2))
                else:
                    pygame.draw.rect(ctx, item.color, (ix - 6, iy - 8, 12, 16), 1)
        if len(self.wave_manager.inventory) > 16:
            self.draw_text_with_shadow('< SCROLL >', self.fonts['tiny'], (120, 110, 100), (C.WIN_WIDTH - 200, sy + 110), shadow_color=(210, 200, 180))
        self.draw_text_with_shadow(f'C.FPS: {int(self.clock.get_fps())}', self.fonts['mono'], (255, 255, 255), (C.WIN_WIDTH - 120, C.WIN_HEIGHT - 40))

    def draw_hud_module(self, x, y, w, text, bg, tc=(255, 240, 200)):
        """Vẽ một khối thông tin trên thanh trạng thái phía trên màn hình."""
        ctx = self.display_surface
        font = self.fonts['mono']
        txt = font.render(text, True, tc)
        aw = max(w, txt.get_width() + 25)
        h = 36
        pygame.draw.rect(ctx, (40, 80, 50), (x, y, aw, h), border_radius=6)
        pygame.draw.rect(ctx, (20, 50, 30), (x, y, aw, h), 2, border_radius=6)
        for rx, ry in [(x + 6, y + 6), (x + aw - 6, y + 6), (x + 6, y + h - 6), (x + aw - 6, y + h - 6)]:
            pygame.draw.circle(ctx, (110, 110, 120), (rx, ry), 2)
            pygame.draw.circle(ctx, (20, 20, 30), (rx, ry), 2, 1)
        self.draw_text_with_shadow(text, font, tc, (x + (aw - txt.get_width()) // 2, y + (h - txt.get_height()) // 2), shadow_color=(0, 0, 0, 120))

    def draw_tooltips(self):
        """Hiển thị hộp thông tin chi tiết khi người dùng di chuyển chuột qua các thực thể hoặc vật phẩm."""
        mx, my = pygame.mouse.get_pos()
        py = C.WIN_HEIGHT - C.UI_BOTTOM_HEIGHT
        for i, (name, s) in enumerate(C.TOWER_STATS.items()):
            bx = 180 + i * 115
            if bx <= mx <= bx + 100 and py + 20 <= my <= py + 120:
                spd_rating = int(1000 / s['fire_rate'])
                self.render_tooltip(mx, my - 250, [f'--- {self.t(name).upper()} ---', f"{self.t('COST')}: ${s['cost']}", f"{self.t('ATK')}: {s['damage']}", f"{self.t('SPD')}: {spd_rating}", f"{self.t('RNG')}: {s['range']}", f"{self.t('CRIT')}: {int(s.get('crit_chance', 0) * 100)}% ({s.get('crit_mult', 1.5)}X)", f"{self.t('AOE')}: {s.get('aoe', 0)}"])
                return
        for i in range(min(16, len(self.wave_manager.inventory))):
            idx = i + self.inv_scroll
            if idx < len(self.wave_manager.inventory):
                gx, gy = (810 + i * 45, py + 80)
                if gx <= mx <= gx + 40 and gy <= my <= gy + 40:
                    self.render_tooltip(mx - 160, my - 180, self.wave_manager.inventory[idx].get_tooltip_data(self.t))
                    return
        for b in self.beacons:
            if math.hypot(b.x - mx, b.y - my) < C.GRID_SIZE // 2:
                all_buffs = b.get_all_buffs()
                buff_lines = [f'--- {self.t(b.type).upper()} ---', f"{self.t('DESCRIPTION')}: {self.t(b.desc)}"]
                for b_type, b_val in all_buffs.items():
                    buff_lines.append(f'{self.t(b_type)}: +{int(b_val * 100)}%')
                buff_lines.append(f"{self.t('SLOTS')}: {len(b.gems)}/2")
                self.render_tooltip(mx + 15, my - 80, buff_lines)
                return
        for t in self.towers:
            if math.hypot(t.x - mx, t.y - my) < C.GRID_SIZE // 2:
                spd_rating = int(1000 / t.fire_rate)
                base_spd = int(1000 / t.base_fire_rate)
                gem_names = [self.t(g.name).upper() for g in t.gems]
                lines = [f'--- {self.t(t.type).upper()} ---', f"{self.t('ATK')}: {t.damage} ({self.t('BASE')} {t.base_damage})", f"{self.t('SPD')}: {spd_rating} ({self.t('BASE')} {base_spd})", f"{self.t('RNG')}: {t.range} ({self.t('BASE')} {t.base_range})", f"{self.t('CRIT')}: {int(t.crit_chance * 100)}% ({t.crit_mult}X)", f"{self.t('AOE')}: {t.aoe}", f"{self.t('SLOTS')}: {len(t.gems)}/2"]
                if gem_names:
                    lines.append(f"{self.t('SOCKETS')}: {', '.join(gem_names)}")
                self.render_tooltip(mx + 15, my - 220, lines)
                return

    def render_tooltip(self, x, y, lines):
        """Xử lý việc vẽ hộp thoại thông tin tại một vị trí cụ thể với nội dung cho trước.

Thông số:
    x là tọa độ X hiển thị
    y là tọa độ Y hiển thị
    lines là danh sách các dòng văn bản thông tin"""
        font = self.fonts['tiny']
        final_lines = []
        for rl in lines:
            txt = str(rl).upper()
            words = txt.split(' ')
            curr = ''
            for w in words:
                if font.size(curr + w + ' ')[0] <= 300:
                    curr += w + ' '
                else:
                    if curr:
                        final_lines.append(curr.strip())
                    curr = w + ' '
            if curr:
                final_lines.append(curr.strip())
        h, w = (len(final_lines) * 22 + 15, 320)
        x, y = (max(10, min(x, C.WIN_WIDTH - w - 10)), max(10, min(y, C.WIN_HEIGHT - h - 10)))
        ctx = self.display_surface
        pygame.draw.rect(ctx, (60, 50, 40), (x - 2, y - 2, w + 4, h + 4), border_radius=8)
        pygame.draw.rect(ctx, (245, 235, 210), (x, y, w, h), border_radius=8)
        pygame.draw.rect(ctx, (225, 215, 185), (x + 5, y + 5, w - 10, h - 10), border_radius=5)
        for i, l in enumerate(final_lines):
            self.draw_text_with_shadow(l, font, (60, 40, 20), (x + 15, y + 8 + i * 22), shadow_color=(185, 200, 175))

    def draw_surrounding_forests(self, ctx):
        """Vẽ các hàng cây trang trí xung quanh khu vực chơi chính."""
        from systems.asset_manager import AssetManager
        grid_rect = pygame.Rect(C.OFFSET_X, C.OFFSET_Y, C.GRID_COLS * C.GRID_SIZE, C.GRID_ROWS * C.GRID_SIZE)
        for tree in sorted(self.trees, key=lambda t: t['pos'][1]):
            px, py = tree['pos']
            sz = tree['size']
            color = tree['color']
            env_assets = AssetManager.get_instance().env
            tree_asset = None
            if sz > 110 and 'medium_tree' in env_assets:
                tree_asset = env_assets['medium_tree']
            elif sz > 85 and 'small_tree' in env_assets:
                tree_asset = env_assets['small_tree']
            elif 'small_small_tree' in env_assets:
                tree_asset = env_assets['small_small_tree']
            if tree_asset:
                tw, th = tree_asset.get_size()
                target_w = sz
                if tree_asset == env_assets.get('small_tree') or tree_asset == env_assets.get('small_small_tree'):
                    target_w = int(sz * 1.5)
                target_h = int(th / tw * target_w)
                scaled_tree = pygame.transform.scale(tree_asset, (target_w, target_h))
                tree_rect = pygame.Rect(px - target_w // 2, py + sz // 2 - target_h, target_w, target_h)
                is_on_left = tree_rect.right <= C.OFFSET_X + 50
                is_on_right = tree_rect.left >= C.OFFSET_X + C.GRID_COLS * C.GRID_SIZE - 50
                is_on_top = tree_rect.bottom <= C.OFFSET_Y + 25
                if is_on_left or is_on_right or is_on_top:
                    ctx.blit(scaled_tree, tree_rect.topleft)
            else:
                pygame.draw.circle(ctx, color, (px, py), sz // 2)

    def draw_monster_cave(self, cx, cy, t):
        """Vẽ hang quái vật nơi kẻ địch sẽ xuất hiện."""
        ctx = self.display_surface
        asset = AssetManager.get_instance().env.get('Cave')
        if asset:
            ctx.blit(pygame.transform.scale(asset, (C.GRID_SIZE, C.GRID_SIZE)), (cx - C.GRID_SIZE // 2, cy - C.GRID_SIZE // 2))
            return
        pygame.draw.rect(ctx, (20, 40, 25), (cx - C.GRID_SIZE // 2 + 2, cy - C.GRID_SIZE // 2 + 2, C.GRID_SIZE - 4, C.GRID_SIZE - 4), border_radius=8)
        pygame.draw.rect(ctx, (10, 20, 10), (cx - C.GRID_SIZE // 2 + 8, cy - C.GRID_SIZE // 2 + 8, C.GRID_SIZE - 16, C.GRID_SIZE - 16), border_radius=4)
        eye_c = (155 + int(abs(math.sin(t * 4)) * 100), 40, 40)
        for ex in [-10, 10]:
            pygame.draw.circle(ctx, eye_c, (cx + ex, cy - 4), 4)

    def draw_castle_base(self, pos, t):
        """Vẽ căn cứ lâu đài mà người chơi cần bảo vệ."""
        hx, hy, ctx = (pos[0], pos[1], self.display_surface)
        asset = AssetManager.get_instance().env.get('Castle')
        if asset:
            ctx.blit(pygame.transform.scale(asset, (C.GRID_SIZE, C.GRID_SIZE)), (hx - C.GRID_SIZE // 2, hy - C.GRID_SIZE // 2))
            return
        pygame.draw.rect(ctx, (210, 220, 210), (hx - 25, hy - 10, 50, 35))
        pygame.draw.rect(ctx, (160, 170, 160), (hx - 25, hy - 10, 50, 35), 2)
        pygame.draw.polygon(ctx, (50, 110, 50), [(hx - 32, hy - 10), (hx, hy - 45), (hx + 32, hy - 10)])
        pygame.draw.rect(ctx, (40, 70, 50), (hx - 8, hy + 12, 16, 15), border_radius=3)

    def draw_powerup_menu(self):
        """Vẽ màn hình lựa chọn nâng cấp khi người chơi hoàn thành các mốc quan trọng."""
        ctx = self.display_surface
        s = pygame.Surface((C.WIN_WIDTH, C.WIN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 210))
        ctx.blit(s, (0, 0))
        title = self.t('POWERUP_MENU')
        tx = C.WIN_WIDTH // 2 - self.fonts['medium'].size(title)[0] // 2
        self.draw_text_with_shadow(title, self.fonts['medium'], (255, 215, 0), (tx, 180))
        timer = f"{self.t('TIME_REMAINING')}: {max(0, self.powerup_timer // C.FPS)}s"
        tsx = C.WIN_WIDTH // 2 - self.fonts['small'].size(timer)[0] // 2
        self.draw_text_with_shadow(timer, self.fonts['small'], (255, 100, 100), (tsx, 235))
        sx, mx, my = (C.WIN_WIDTH // 2 - 450, *pygame.mouse.get_pos())
        for i, p in enumerate(self.current_powerups):
            cx = sx + i * 310
            hover = cx <= mx <= cx + 280 and 350 <= my <= 650
            pygame.draw.rect(ctx, (50, 50, 70) if hover else (30, 30, 45), (cx, 320, 280, 350), border_radius=15)
            pygame.draw.rect(ctx, (255, 215, 0) if hover else (120, 120, 140), (cx, 320, 280, 350), 4, border_radius=15)
            self.draw_wrapped_text_centered(self.t(p['name']).upper(), self.fonts['medium'], (255, 255, 255), cx + 140, 360, 260)
            self.draw_wrapped_text_centered(self.t(p['desc']), self.fonts['small'], (200, 200, 200), cx + 140, 480, 240)
            sc = f"{self.t('PRESS')} [{i + 1}]"
            self.draw_text_with_shadow(sc, self.fonts['small'], C.COLOR_ACCENT, (cx + 140 - self.fonts['small'].size(sc)[0] // 2, 600))

    def draw_game_over(self):
        """Vẽ màn hình thông báo khi người chơi thua cuộc."""
        ctx = self.display_surface
        s = pygame.Surface((C.WIN_WIDTH, C.WIN_HEIGHT), pygame.SRCALPHA)
        s.fill((60, 0, 0, 225))
        ctx.blit(s, (0, 0))
        txt = self.fonts['large'].render(self.t('MISSION FAILED'), True, (255, 100, 100))
        ctx.blit(txt, (C.WIN_WIDTH // 2 - txt.get_width() // 2, C.WIN_HEIGHT // 2 - 50))
        st = self.t('PRESS ANY KEY TO RESTART')
        self.draw_text_with_shadow(st, self.fonts['medium'], (255, 255, 255), (C.WIN_WIDTH // 2 - self.fonts['medium'].size(st)[0] // 2, C.WIN_HEIGHT // 2 + 100))

    def trigger_powerup(self):
        """Khởi tạo và đưa ra danh sách các lựa chọn nâng cấp ngẫu nhiên cho người chơi."""
        self.powerups_offered = True
        self.powerup_timer = (2 if self.is_dev else 15) * C.FPS
        pool = [{'name': 'ATTACK BEACON', 'type': 'BEACON', 'data': 'ATTACK BEACON', 'desc': 'BOOSTS ADJACENT DMG BY 25%'}, {'name': 'SPEED BEACON', 'type': 'BEACON', 'data': 'SPEED BEACON', 'desc': 'BOOSTS ADJACENT SPEED BY 25%'}, {'name': 'RANGE BEACON', 'type': 'BEACON', 'data': 'RANGE BEACON', 'desc': 'BOOSTS ADJACENT RANGE BY 25%'}, {'name': 'STR UPGRADE', 'type': 'CARD', 'data': {'name': 'STRENGTH CARD', 'desc': 'GRANT +15% ATK'}, 'desc': 'STRENGTH CARD'}, {'name': 'AGI UPGRADE', 'type': 'CARD', 'data': {'name': 'AGILITY CARD', 'desc': 'GRANT +15% SPD'}, 'desc': 'AGILITY CARD'}, {'name': 'VIS UPGRADE', 'type': 'CARD', 'data': {'name': 'VISION CARD', 'desc': 'GRANT +15% RNG'}, 'desc': 'VISION CARD'}, {'name': 'PRE UPGRADE', 'type': 'CARD', 'data': {'name': 'PRECISION CARD', 'desc': 'GRANT +10% CRIT'}, 'desc': 'PRECISION CARD'}]
        globals = [{'name': 'GOLD RUSH', 'type': 'GLOBAL', 'data': 'GOLD', 'desc': '+500 GOLD INSTANTLY'}, {'name': 'TAX REBATE', 'type': 'GLOBAL', 'data': 'TAX', 'desc': 'MOBS DROP 50% MORE GOLD'}]
        options = pool + globals
        weights = [1] * len(pool) + [6] * len(globals)
        selected = []
        temp_options = list(options)
        temp_weights = list(weights)
        while len(selected) < 3 and temp_options:
            idx = random.choices(range(len(temp_options)), weights=temp_weights, k=1)[0]
            selected.append(temp_options[idx])
            temp_options.pop(idx)
            temp_weights.pop(idx)
        self.current_powerups = selected

    def apply_powerup(self, idx):
        """Áp dụng hiệu ứng của nâng cấp mà người chơi đã chọn vào trò chơi."""
        if idx >= len(self.current_powerups):
            return
        p = self.current_powerups[idx]
        if p['type'] == 'GLOBAL':
            if p['data'] == 'GOLD':
                self.wave_manager.gold += 500
            elif p['data'] == 'TAX':
                self.wave_manager.mob_gold_multiplier += 0.5
        elif p['type'] == 'CARD':
            self.wave_manager.inventory.append(InventoryItem(C.ItemType.STAT_CARD, p['data']))
        elif p['type'] == 'BEACON':
            self.wave_manager.inventory.append(InventoryItem(C.ItemType.BEACON, p['data']))
        self.state = C.GameState.PLAYING

    def reset_game(self):
        """Khôi phục toàn bộ trạng thái trò chơi về ban đầu để bắt đầu lượt chơi mới."""
        self.wave_manager = WaveManager(self.vfx_manager)
        if self.is_dev:
            self.wave_manager.gold = 999999
        self.towers, self.beacons, self.selected_type, self.state = ([], [], 'Earth Cannon', C.GameState.PLAYING)
        self.next_wave_timer = (2 if self.is_dev else 30) * C.FPS
        self.current_powerups, self.powerups_offered, self.selected_inv_idx, self.inv_scroll, self.trash_mode, self.needs_stat_recalc = ([], False, -1, 0, False, True)

    def process_auto_slots(self):
        """Tự động gắn các vật phẩm nâng cấp từ kho đồ vào các tháp còn trống nếu chế độ tự động được bật."""
        self.auto_slot_timer += 1
        if self.auto_slot_timer < 30:
            return
        self.auto_slot_timer = 0
        if not self.wave_manager.inventory:
            return
        for i in range(len(self.wave_manager.inventory) - 1, -1, -1):
            item = self.wave_manager.inventory[i]
            slotted = False
            if item.item_type == C.ItemType.GEM:
                for t in self.towers:
                    if t.add_gem(item):
                        self.wave_manager.inventory.pop(i)
                        AssetManager.get_instance().play_sound('powerup')
                        self.needs_stat_recalc = True
                        slotted = True
                        break
            elif item.item_type == C.ItemType.STAT_CARD:
                for b in self.beacons:
                    if b.add_gem(item):
                        self.wave_manager.inventory.pop(i)
                        AssetManager.get_instance().play_sound('powerup')
                        self.needs_stat_recalc = True
                        slotted = True
                        break
            if slotted:
                break

    def run(self):
        """Bắt đầu vòng lặp chính để vận hành trò chơi."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(C.FPS)
        pygame.quit()
        sys.exit()
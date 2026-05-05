import pygame
import random
import math

class Particle:
    """Thực thể hạt đơn lẻ tạo nên các hiệu ứng hình ảnh sống động."""

    def __init__(self, x, y, color, velocity, life, size=4, gravity=0, is_rect=False):
        """Thiết lập các thuộc tính vật lý và màu sắc cho hạt."""
        self.reset(x, y, color, velocity, life, size, gravity, is_rect)

    def reset(self, x, y, color, velocity, life, size=4, gravity=0, is_rect=False):
        """Khôi phục trạng thái của hạt để sử dụng lại trong hệ thống bể chứa."""
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.max_life = life
        self.life = life
        self.size = size
        self.gravity = gravity
        self.is_rect = is_rect
        self.is_dead = False

    def update(self):
        """Cập nhật chuyển động và sự suy giảm của hạt theo thời gian."""
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1
        if self.life <= 0:
            self.is_dead = True

    def draw(self, surface):
        """Vẽ hạt lên màn hình."""
        if self.life <= 0:
            return
        current_size = max(1, int(self.size * (self.life / self.max_life)))
        if self.is_rect and (abs(self.vx) > 0.1 or abs(self.vy) > 0.1):
            length = current_size * 2.5
            angle = math.atan2(self.vy, self.vx)
            tx = self.x + math.cos(angle) * length
            ty = self.y + math.sin(angle) * length
            pygame.draw.line(surface, self.color, (self.x, self.y), (tx, ty), max(2, current_size // 2))
        else:
            rect = pygame.Rect(int(self.x - current_size / 2), int(self.y - current_size / 2), current_size, current_size)
            pygame.draw.rect(surface, self.color, rect)

class FloatingText:
    """Thực thể văn bản bay hiển thị các thông số tức thời như sát thương."""

    def __init__(self, x, y, text, color, life=60, is_crit=False):
        """Thiết lập nội dung và hướng bay cho văn bản."""
        self.reset(x, y, text, color, life, is_crit)

    def reset(self, x, y, text, color, life=60, is_crit=False):
        """Khôi phục trạng thái văn bản để tái sử dụng."""
        self.x, self.y = (x, y)
        self.text = text
        self.color = color
        self.max_life = life
        self.life = life
        self.is_dead = False
        self.is_crit = is_crit
        self.surf = None

    def update(self):
        """Cập nhật vị trí bay và độ mờ của văn bản."""
        self.y -= 0.5 if self.is_crit else 0.8
        self.life -= 1
        if self.life <= 0:
            self.is_dead = True

    def draw(self, surface, font):
        """Vẽ văn bản lên màn hình."""
        if self.life <= 0:
            return
        if not self.surf:
            self.surf = font.render(self.text, True, self.color)
        alpha = int(self.life / self.max_life * 255)

        def blit_alpha(surf, pos, alpha):
            """
            Docstring for def blit_alpha.
            """
            s = surf.copy()
            s.set_alpha(alpha)
            surface.blit(s, pos)
        scale = 1.0
        if self.is_crit:
            progress = (self.max_life - self.life) / 10.0
            scale = max(1.0, 2.5 - progress * 1.5) if progress < 1.0 else 1.0
        w, h = self.surf.get_size()
        draw_surf = self.surf
        if scale != 1.0:
            draw_surf = pygame.transform.scale(self.surf, (int(w * scale), int(h * scale)))
        shadow_surf = font.render(self.text, True, (20, 20, 20))
        if scale != 1.0:
            shadow_surf = pygame.transform.scale(shadow_surf, (int(w * scale), int(h * scale)))
        sx, sy = (self.x - draw_surf.get_width() // 2, int(self.y))
        if self.is_crit:
            sy -= draw_surf.get_height() // 2
        blit_alpha(shadow_surf, (sx + 2, sy + 2), alpha // 2)
        blit_alpha(draw_surf, (sx, sy), alpha)

class VFXManager:
    """Hệ thống điều phối toàn bộ các hiệu ứng hình ảnh trong trò chơi."""

    def __init__(self):
        """Khởi tạo hệ thống và chuẩn bị các bể chứa thực thể hiệu ứng."""
        self.particles = []
        self.texts = []
        self.particle_pool = []
        self.text_pool = []
        self.shake_val = 0

    def _get_particle(self, x, y, color, velocity, life, size=4, gravity=0, is_rect=False):
        """Lấy một thực thể hạt từ bể chứa để sử dụng."""
        if self.particle_pool:
            p = self.particle_pool.pop()
            p.reset(x, y, color, velocity, life, size, gravity, is_rect)
            return p
        return Particle(x, y, color, velocity, life, size, gravity, is_rect)

    def _get_text(self, x, y, text, color, is_crit=False):
        """Lấy một thực thể văn bản từ bể chứa để sử dụng."""
        if self.text_pool:
            t = self.text_pool.pop()
            t.reset(x, y, text, color, is_crit=is_crit)
            return t
        return FloatingText(x, y, text, color, is_crit=is_crit)

    def create_floating_text(self, x, y, text, color, is_crit=False):
        """Tạo mới một hiệu ứng văn bản bay tại vị trí chỉ định."""
        self.texts.append(self._get_text(x, y, text, color, is_crit))

    def create_ambient_particle(self, x, y, color, size=3):
        """Tạo ra các hạt hiệu ứng môi trường xung quanh một vị trí."""
        vx = random.uniform(-0.3, 0.3)
        vy = random.uniform(-0.5, -0.2)
        life = random.randint(30, 60)
        self.particles.append(self._get_particle(x, y, color, (vx, vy), life, size=size))

    def spawn_link_particle(self, start_x, start_y, end_x, end_y, color):
        """Tạo hiệu ứng đường nối giữa hai thực thể."""
        sx = start_x + random.uniform(-15, 15)
        sy = start_y + random.uniform(-15, 15)
        dx = end_x - sx
        dy = end_y - sy
        dist = math.hypot(dx, dy)
        if dist > 0:
            speed = random.uniform(1.8, 3.2)
            life = int(dist / speed)
            vx = dx / dist * speed
            vy = dy / dist * speed
            self.particles.append(self._get_particle(sx, sy, color, (vx, vy), life, size=8, is_rect=True))

    def trigger_shake(self, val):
        """Kích hoạt hiệu ứng rung màn hình để tăng cảm giác va chạm."""
        self.shake_val = max(self.shake_val, val)

    def create_explosion(self, x, y, color, count=15, size=5):
        """Tạo ra hiệu ứng nổ mạnh mẽ tại một điểm."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 4)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.randint(20, 60)
            self.particles.append(self._get_particle(x, y, color, (vx, vy), life, size=size))

    def create_impact(self, x, y, color):
        """Tạo hiệu ứng va chạm nhẹ khi đạn trúng mục tiêu."""
        for _ in range(8):
            vx = random.uniform(-2, 2)
            vy = random.uniform(-2, 2)
            self.particles.append(self._get_particle(x, y, color, (vx, vy), 15, size=3))

    def create_death_effect(self, x, y, color):
        """Tạo hiệu ứng hình ảnh khi một kẻ địch bị tiêu diệt."""
        for _ in range(20):
            vx = random.uniform(-2, 2)
            vy = random.uniform(-4, 0)
            self.particles.append(self._get_particle(x, y, color, (vx, vy), 40, size=8, gravity=0.15))

    def update(self):
        """Cập nhật trạng thái của toàn bộ các hạt và văn bản đang hoạt động."""
        for p in self.particles[:]:
            p.update()
            if p.is_dead:
                self.particles.remove(p)
                self.particle_pool.append(p)
        for t in self.texts[:]:
            t.update()
            if t.is_dead:
                self.texts.remove(t)
                self.text_pool.append(t)
        if self.shake_val > 0:
            self.shake_val -= 1

    def draw(self, surface, font=None):
        """Thực hiện việc vẽ tất cả các hiệu ứng lên màn hình hiển thị."""
        for p in self.particles:
            p.draw(surface)
        if font:
            for t in self.texts:
                t.draw(surface, font)
import pygame
from core.constants import C
from systems.asset_manager import AssetManager

class Beacon:
    """Công trình hỗ trợ đặc biệt có khả năng lan tỏa hào quang để tăng sức mạnh cho tháp lân cận."""

    def __init__(self, x, y, beacon_type):
        """Khởi tạo công trình hỗ trợ tại vị trí xác định."""
        stats = C.BEACON_STATS[beacon_type]
        self.x = x
        self.y = y
        self.type = beacon_type
        self.buff_type = stats['buff_type']
        self.buff_val = stats['buff_val']
        self.color = stats['color']
        self.desc = stats['desc']
        self.gems = []

    def add_gem(self, item):
        """Gắn thêm thẻ chỉ số vào công trình hỗ trợ để mở rộng khả năng của nó."""
        if len(self.gems) < 2 and item.item_type == C.ItemType.STAT_CARD:
            self.gems.append(item)
            return True
        return False

    def get_all_buffs(self):
        """Tổng hợp toàn bộ các loại hiệu ứng tăng cường mà công trình này đang cung cấp."""
        buffs = {self.buff_type: self.buff_val}
        for card in self.gems:
            name = card.name
            if name == 'STRENGTH CARD':
                buffs['ATK'] = buffs.get('ATK', 0) + 0.15
            elif name == 'AGILITY CARD':
                buffs['SPD'] = buffs.get('SPD', 0) + 0.15
            elif name == 'VISION CARD':
                buffs['RNG'] = buffs.get('RNG', 0) + 0.15
            elif name == 'PRECISION CARD':
                buffs['CRIT'] = buffs.get('CRIT', 0) + 0.1
        return buffs

    def draw(self, surface):
        """Vẽ công trình hỗ trợ và vùng hào quang ảnh hưởng của nó."""
        x, y = (int(self.x), int(self.y))
        points = [(x, y - 20), (x + 20, y), (x, y + 20), (x - 20, y)]
        pygame.draw.polygon(surface, (20, 20, 25), [(p[0] + 4, p[1] + 4) for p in points])
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, (255, 255, 255), points, 2)
        import math
        pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 5
        pygame.draw.circle(surface, (255, 255, 255, 150), (x, y), int(5 + pulse), 1)
        for i in range(2):
            if i < len(self.gems):
                slot_color = self.gems[i].color
                sx = x - 8 + i * 16
                sy = y + 25
                pygame.draw.circle(surface, slot_color, (sx, sy), 4)
                pygame.draw.circle(surface, (255, 255, 255), (sx, sy), 4, 1)
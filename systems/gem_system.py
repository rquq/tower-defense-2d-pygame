from enum import Enum, auto

class GemType(Enum):
    """Định nghĩa các loại ngọc nguyên tố có trong trò chơi."""
    FIRE = auto()
    ICE = auto()
    OVERCLOCK = auto()

class Gem:
    """Thực thể ngọc có thể gắn vào tháp để tăng cường sức mạnh."""

    def __init__(self, gem_type):
        """Khởi tạo ngọc với loại và thuộc tính xác định."""
        self.type = gem_type
        self.name = gem_type.name
        self.colors = {GemType.FIRE: (255, 69, 0), GemType.ICE: (0, 191, 255), GemType.OVERCLOCK: (255, 215, 0)}
        self.color = self.colors[gem_type]

    def apply_modifier(self, tower):
        """Áp dụng các thay đổi chỉ số lên tháp mục tiêu."""
        if self.type == GemType.FIRE:
            pass
        elif self.type == GemType.OVERCLOCK:
            tower.fire_rate = int(tower.fire_rate * 0.7)
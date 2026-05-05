import math
from core.constants import C

class SpatialManager:
    """Quản lý vị trí các thực thể bằng lưới không gian để tối ưu hóa việc tìm kiếm mục tiêu."""

    def __init__(self, cell_size=C.GRID_SIZE * 2):
        """Thiết lập kích thước các ô lưới không gian."""
        self.cell_size = cell_size
        self.grid = {}

    def _get_cell(self, x, y):
        """Xác định ô lưới tương ứng với một tọa độ pixel."""
        return (int(x // self.cell_size), int(y // self.cell_size))

    def clear(self):
        """Làm sạch lưới dữ liệu trước khi bắt đầu khung hình mới."""
        self.grid = {}

    def add_entity(self, entity):
        """Đưa một thực thể vào đúng ô lưới quản lý của nó."""
        cell = self._get_cell(entity.x, entity.y)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(entity)

    def get_nearby_entities(self, x, y, radius):
        """Lấy danh sách các thực thể nằm trong các ô lưới xung quanh một vị trí."""
        nearby = []
        start_cell = self._get_cell(x - radius, y - radius)
        end_cell = self._get_cell(x + radius, y + radius)
        for cx in range(start_cell[0], end_cell[0] + 1):
            for cy in range(start_cell[1], end_cell[1] + 1):
                cell = (cx, cy)
                if cell in self.grid:
                    for entity in self.grid[cell]:
                        dist_sq = (entity.x - x) ** 2 + (entity.y - y) ** 2
                        if dist_sq <= radius ** 2:
                            nearby.append(entity)
        return nearby

    def get_closest_entity(self, x, y, radius, criteria=None):
        """Tìm thực thể gần một tọa độ nhất trong tầm quét hiệu quả."""
        nearby = self.get_nearby_entities(x, y, radius)
        if not nearby:
            return None
        if criteria:
            return criteria(nearby)
        return min(nearby, key=lambda e: (e.x - x) ** 2 + (e.y - y) ** 2)
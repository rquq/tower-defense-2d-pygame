import math
from core.constants import GRID_SIZE

class SpatialManager:
    """
    A simple Spatial Hash Grid to optimize entity lookups.
    Reduces O(N) searches to approximately O(1) by partitioning space into cells.
    """
    def __init__(self, cell_size=GRID_SIZE * 2):
        self.cell_size = cell_size
        self.grid = {}

    def _get_cell(self, x, y):
        return (int(x // self.cell_size), int(y // self.cell_size))

    def clear(self):
        """Clears the grid for the next frame."""
        self.grid = {}

    def add_entity(self, entity):
        """Adds an entity to its corresponding cell."""
        cell = self._get_cell(entity.x, entity.y)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(entity)

    def get_nearby_entities(self, x, y, radius):
        """
        Returns a list of entities within the specified radius of (x, y).
        Only checks cells that could potentially contain entities within range.
        """
        nearby = []
        start_cell = self._get_cell(x - radius, y - radius)
        end_cell = self._get_cell(x + radius, y + radius)

        # Iterate through all cells covered by the bounding box of the radius
        for cx in range(start_cell[0], end_cell[0] + 1):
            for cy in range(start_cell[1], end_cell[1] + 1):
                cell = (cx, cy)
                if cell in self.grid:
                    for entity in self.grid[cell]:
                        # Squared distance check is faster than sqrt
                        dist_sq = (entity.x - x)**2 + (entity.y - y)**2
                        if dist_sq <= radius**2:
                            nearby.append(entity)
        return nearby

    def get_closest_entity(self, x, y, radius, criteria=None):
        """
        Finds the closest entity within radius. 
        Optional 'criteria' lambda can be used for secondary filtering (e.g., strongest).
        """
        nearby = self.get_nearby_entities(x, y, radius)
        if not nearby:
            return None
        
        if criteria:
            return criteria(nearby)
        
        return min(nearby, key=lambda e: (e.x - x)**2 + (e.y - y)**2)

from collections import deque
from core.constants import *

def get_path_bfs(start_grid, end_grid, walkable_grid):
    """
    Simple Breadth-First Search (BFS) implementation for grid pathfinding.
    Efficiently finds the shortest path by exploring layer by layer.
    """
    queue = deque([start_grid])
    came_from = {start_grid: None}
    
    while queue:
        current = queue.popleft()
        
        if current == end_grid:
            break
            
        for dc, dr in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (current[0] + dc, current[1] + dr)
            if neighbor in walkable_grid and neighbor not in came_from:
                queue.append(neighbor)
                came_from[neighbor] = current
                
    if end_grid not in came_from: 
        return []
        
    path = []
    curr = end_grid
    while curr:
        path.append(curr)
        curr = came_from[curr]
    return path[::-1]

class PathSystem:
    """
    Docstring for class PathSystem.
    """
    def __init__(self):
        """
        Docstring for def __init__.
        """
        self.walkable_tiles = set()
        self.generate_curvy_path()
        
    def generate_curvy_path(self):
        """
        Docstring for def generate_curvy_path.
        """
        # Single curvy path, compressed for 28x14 grid
        self.add_segment((0, 4), (4, 4))
        self.add_segment((4, 4), (4, 11))
        self.add_segment((4, 11), (9, 11))
        self.add_segment((9, 11), (9, 2))
        self.add_segment((9, 2), (15, 2))
        self.add_segment((15, 2), (15, 11))
        self.add_segment((15, 11), (21, 11))
        self.add_segment((21, 11), (21, 5))
        self.add_segment((21, 5), (25, 5))
        self.add_segment((25, 5), (25, 9))
        self.add_segment((25, 9), (27, 9))
        
    def add_segment(self, start, end):
        """
        Docstring for def add_segment.
        """
        c1, r1 = start
        c2, r2 = end
        if c1 == c2:
            for r in range(min(r1, r2), max(r1, r2) + 1): self.walkable_tiles.add((c1, r))
        elif r1 == r2:
            for c in range(min(c1, c2), max(c1, c2) + 1): self.walkable_tiles.add((c, r1))

    def get_enemy_waypoints(self):
        """
        Docstring for def get_enemy_waypoints.
        """
        # Using simple BFS for pathfinding
        grid_path = get_path_bfs((0, 4), (27, 9), self.walkable_tiles)
        return [get_pixel_pos(c, r) for c, r in grid_path]

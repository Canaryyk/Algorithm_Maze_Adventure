# maze.py

import random
import config as cfg
from algorithms.maze_generator import generate_recursive_division_maze

class Maze:
    """
    这个类负责生成和存储迷宫的数据结构。
    它知道墙壁、路径、起点、终点和物品的位置，但不关心它们如何被渲染。
    纯数据模型，与图形库无关。
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = generate_recursive_division_maze(self.width, self.height)
        
        path_coords = self._get_all_path_coords()
        random.shuffle(path_coords)

        items_to_place = {
            cfg.GOLD: 5,
            cfg.TRAP: 5,
            cfg.LOCKER: 1,
            cfg.BOSS: 1,
            cfg.START: 1,
            cfg.EXIT: 1
        }
        
        for item_symbol, count in items_to_place.items():
            self._place_item(item_symbol, count, path_coords)

    def _get_all_path_coords(self):
        """获取迷宫中所有可通行的路径坐标。"""
        path_coords = []
        for r in range(self.height):
            for c in range(self.width):
                if self.grid[r][c] == cfg.PATH:
                    path_coords.append((r, c))
        return path_coords

    def _place_item(self, symbol, count, available_coords):
        """在可用的坐标上放置指定数量的物品。"""
        for _ in range(count):
            if available_coords:
                r, c = available_coords.pop()
                self.grid[r][c] = symbol
            else:
                print(f"警告: 没有足够的位置来放置 '{symbol}'。")
                break
    
    def get_item_locations(self, item_symbol):
        """获取指定类型物品的所有网格坐标。"""
        locations = []
        for r, row in enumerate(self.grid):
            for c, tile in enumerate(row):
                if tile == item_symbol:
                    locations.append((c, r)) # 返回 (x, y) 格式
        return locations

    def get_start_pos(self):
        """获取起始位置的像素坐标"""
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                if tile == cfg.START:
                    return (x * cfg.TILE_SIZE + cfg.TILE_SIZE // 2,
                            y * cfg.TILE_SIZE + cfg.TILE_SIZE // 2)
        return (cfg.TILE_SIZE // 2, cfg.TILE_SIZE // 2)

    def is_wall(self, x, y):
        """检查指定像素坐标是否为墙壁"""
        grid_x = x // cfg.TILE_SIZE
        grid_y = y // cfg.TILE_SIZE
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            return self.grid[grid_y][grid_x] == cfg.WALL
        return True # 边界外视为墙

    def get_tile_type(self, x, y):
        """获取指定网格坐标的瓦片类型"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None

    def set_tile_type(self, grid_x, grid_y, tile_type):
        """设置指定网格坐标的类型"""
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            self.grid[grid_y][grid_x] = tile_type

    def get_neighbors(self, x, y):
        """获取指定网格坐标的相邻格子"""
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # 上右下左
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbors.append((nx, ny, self.grid[ny][nx]))
        return neighbors

    def count_items(self, item_type):
        """统计指定类型物品的数量"""
        count = 0
        for row in self.grid:
            for tile in row:
                if tile == item_type:
                    count += 1
        return count

    def get_all_items(self):
        """获取所有物品的位置和类型"""
        items = {}
        for r, row in enumerate(self.grid):
            for c, tile in enumerate(row):
                if tile not in [cfg.PATH, cfg.WALL]:
                    if tile not in items:
                        items[tile] = []
                    items[tile].append((c, r))
        return items

    def is_valid_position(self, x, y):
        """检查坐标是否在迷宫范围内"""
        return 0 <= x < self.width and 0 <= y < self.height

    def is_passable(self, x, y):
        """检查指定网格坐标是否可通行"""
        if not self.is_valid_position(x, y):
            return False
        return self.grid[y][x] != cfg.WALL
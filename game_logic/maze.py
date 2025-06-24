# maze.py

import pygame
import config as cfg

class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = []
        self.generate_maze()

    def generate_maze(self):
        """
        生成迷宫。
        你的任务是用算法替换掉这里的静态地图。
        这个地图现在包含了所有你需要处理的元素。
        """
        # G=Gold, T=Trap, L=Locker, B=Boss
        self.grid = [
        ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
        ["#", "S", "#", " ", "#", " ", "#", " ", "#", " ", " ", " ", " ", " ", "#"],
        ["#", " ", "#", " ", "#", " ", "#", " ", "#", "#", "#", " ", "#", "#", "#"],
        ["#", " ", "#", " ", " ", " ", "#", " ", "#", " ", " ", " ", "#", " ", "#"],
        ["#", " ", "#", " ", "#", "#", "#", " ", "#", " ", "#", "#", "#", " ", "#"],
        ["#", " ", " ", " ", "#", " ", " ", " ", " ", " ", " ", " ", "#", " ", "#"],
        ["#", "#", "#", " ", "#", " ", "#", "#", "#", " ", "#", "#", "#", " ", "#"],
        ["#", " ", " ", "T", "G", " ", " ", " ", "#", " ", "L", " ", " ", " ", "#"],
        ["#", " ", "#", "#", "#", "#", "#", "#", "#", " ", "#", " ", "#", " ", "#"],
        ["#", " ", " ", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#"],
        ["#", "#", "#", "#", "#", " ", "#", " ", "#", "#", "#", "#", "#", " ", "#"],
        ["#", " ", " ", "G", " ", "G", " ", " ", "#", " ", " ", " ", " ", " ", "#"],
        ["#", " ", "#", "#", "#", " ", "#", " ", "#", "#", "#", " ", "#", "#", "#"],
        ["#", "G", " ", " ", "#", " ", "#", " ", " ", "G", " ", "B", " ", "E", "#"],
        ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#"]

        ]
        self.height = len(self.grid)
        self.width = len(self.grid[0]) if self.height > 0 else 0

    def get_start_pos(self):
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                if tile == cfg.START:
                    return (x * cfg.TILE_SIZE + cfg.TILE_SIZE // 2,
                            y * cfg.TILE_SIZE + cfg.TILE_SIZE // 2)
        return (cfg.TILE_SIZE // 2, cfg.TILE_SIZE // 2)

    def draw(self, surface):
        color_map = {
            cfg.WALL: cfg.WALL_COLOR,
            cfg.PATH: cfg.PATH_COLOR,
            cfg.START: cfg.START_COLOR,
            cfg.EXIT: cfg.END_COLOR,
            cfg.GOLD: cfg.GOLD_COLOR,
            cfg.TRAP: cfg.TRAP_COLOR,
            cfg.LOCKER: cfg.LOCKER_COLOR,
            cfg.BOSS: cfg.BOSS_COLOR,
        }
        for y, row in enumerate(self.grid):
            for x, tile_type in enumerate(row):
                rect = pygame.Rect(x * cfg.TILE_SIZE, y * cfg.TILE_SIZE, cfg.TILE_SIZE, cfg.TILE_SIZE)
                # 先绘制底层颜色
                base_color = cfg.PATH_COLOR if tile_type != cfg.WALL else cfg.WALL_COLOR
                pygame.draw.rect(surface, base_color, rect)
                # 如果不是普通通路或墙，再绘制上层物品颜色 (绘制一个小点的矩形以示区别)
                if tile_type in color_map and tile_type not in [cfg.PATH, cfg.WALL]:
                    item_rect = rect.inflate(-cfg.TILE_SIZE * 0.2, -cfg.TILE_SIZE * 0.2)
                    pygame.draw.rect(surface, color_map[tile_type], item_rect)

    def is_wall(self, pixel_x, pixel_y):
        """判断墙"""
        grid_x = int(pixel_x // cfg.TILE_SIZE)
        grid_y = int(pixel_y // cfg.TILE_SIZE)
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            return self.grid[grid_y][grid_x] == cfg.WALL
        return True

    def get_tile_type(self, grid_x, grid_y):
        """获取指定网格坐标的类型"""
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            return self.grid[grid_y][grid_x]
        return None

    def set_tile_type(self, grid_x, grid_y, tile_type):
        """设置指定网格坐标的类型"""
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            self.grid[grid_y][grid_x] = tile_type
 # maze.py

import pygame
import config as cfg
# 在这里，之后你需要导入你的迷宫生成算法模块
# from algorithms.maze_generator import generate_recursive_division_maze

class Maze:
    def __init__(self, width, height):
        """
        初始化迷宫对象
        :param width: 迷宫的宽度 (多少个格子)
        :param height: 迷宫的高度 (多少个格子)
        """
        self.width = width
        self.height = height
        self.grid = []  # 用一个二维列表来存储迷宫的结构
        self.generate_maze() # 生成迷宫

    def generate_maze(self):
        """
        生成迷宫的核心函数。
        目前，我们使用一个固定的静态迷宫用于测试。
        后续用算法替换掉这里的静态地图。
        """
        # --- 算法将在此处被调用 ---
        # self.grid = generate_recursive_division_maze(self.width, self.height)

        # 以下是一个用于开发的临时静态迷宫
        # 0 代表墙, 1 代表路, 2 代表起点, 3 代表终点
        self.grid = [
            [0, 2, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 0, 1, 1, 1, 0],
            [0, 1, 0, 0, 1, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 1, 1, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
            [0, 1, 1, 1, 1, 0, 1, 1, 1, 0],
            [0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 3, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]

    def get_start_pos(self):
        """返回起点的像素坐标中心点"""
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                if tile == cfg.START:
                    # 返回格子中心点的坐标
                    return (x * cfg.TILE_SIZE + cfg.TILE_SIZE // 2,
                            y * cfg.TILE_SIZE + cfg.TILE_SIZE // 2)
        return (cfg.TILE_SIZE // 2, cfg.TILE_SIZE // 2) # 如果没找到，默认返回

    def draw(self, surface):
        """
        在给定的surface上绘制整个迷宫
        :param surface: pygame的显示图层 (通常是主屏幕)
        """
        for y, row in enumerate(self.grid):
            for x, tile_type in enumerate(row):
                rect = pygame.Rect(x * cfg.TILE_SIZE, y * cfg.TILE_SIZE, cfg.TILE_SIZE, cfg.TILE_SIZE)
                if tile_type == cfg.WALL:
                    pygame.draw.rect(surface, cfg.WALL_COLOR, rect)
                elif tile_type == cfg.PATH:
                    pygame.draw.rect(surface, cfg.PATH_COLOR, rect)
                elif tile_type == cfg.START:
                    pygame.draw.rect(surface, cfg.START_COLOR, rect)
                elif tile_type == cfg.END:
                    pygame.draw.rect(surface, cfg.END_COLOR, rect)

    def is_wall(self, pixel_x, pixel_y):
        """
        检查给定的像素坐标是否在墙内。这是Player碰撞检测的关键。
        :param pixel_x: 像素x坐标
        :param pixel_y: 像素y坐标
        :return: 如果是墙，返回True，否则返回False
        """
        # 将像素坐标转换为网格坐标
        grid_x = int(pixel_x // cfg.TILE_SIZE)
        grid_y = int(pixel_y // cfg.TILE_SIZE)

        # 边界检查
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            return self.grid[grid_y][grid_x] == cfg.WALL
        return True # 视作边界外都是墙
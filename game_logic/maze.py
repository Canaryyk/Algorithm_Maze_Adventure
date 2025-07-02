"""
迷宫模块 - 核心迷宫功能
"""

import random
from typing import List, Tuple, Optional
import config as cfg
from algorithms.maze_generator import generate_recursive_division_maze


class Maze:
    """迷宫数据模型类，负责迷宫生成和物品放置"""
    
    def __init__(self, width: int, height: int, use_generated: bool ):
        """初始化迷宫"""
        self.width = width
        self.height = height
        
        if use_generated:
            self.grid = self._generate_maze()
        else:
            self.grid = self._get_preset_map()
        
        self._place_game_items()
    
    def _generate_maze(self) -> List[List[str]]:
        """使用算法生成迷宫"""
        return generate_recursive_division_maze(self.width, self.height)
    
    def _get_preset_map(self) -> List[List[str]]:
        """返回预设迷宫地图"""
        return [
            ["#","#","#","#","#","#","#","#","#","#","#","#","#","#","#"],
            ["#"," "," "," "," ","#"," "," "," "," "," "," "," "," ","#"],
            ["#","#","#"," ","#","#","#"," ","#","#","#","#","#","#","#"],
            ["#"," "," "," "," "," ","#"," "," "," ","#"," ","#"," ","#"],
            ["#","#","#"," ","#"," ","#","#","#"," ","#"," ","#"," ","#"],
            ["#"," "," "," ","#"," ","#"," "," "," "," "," "," "," ","#"],
            ["#","#","#"," ","#"," ","#","#","#","#","#"," ","#"," ","#"],
            ["#"," ","#"," ","#"," ","#"," "," "," "," "," ","#"," ","#"],
            ["#"," ","#"," ","#"," ","#","#","#"," ","#","#","#"," ","#"],
            ["#"," "," "," ","#"," "," "," "," "," "," "," ","#"," ","#"],
            ["#"," ","#","#","#","#","#","#","#","#","#","#","#","#","#"],
            ["#"," "," "," ","#"," ","#"," "," "," ","#"," "," "," ","#"],
            ["#","#","#"," ","#"," ","#"," ","#","#","#","#","#"," ","#"],
            ["#"," "," "," "," "," "," "," "," "," "," "," "," "," ","#"],
            ["#","#","#","#","#","#","#","#","#","#","#","#","#","#","#"]
        ]
    
    def _place_game_items(self) -> None:
        """在迷宫中放置游戏物品"""
        # 获取所有可通行位置
        path_coords = []
        for r in range(self.height):
            for c in range(self.width):
                if self.grid[r][c] == cfg.PATH:
                    path_coords.append((c, r))
        
        if not path_coords:
            return
        
        random.shuffle(path_coords)
        
        # 放置物品
        items = [
            (cfg.START, 1),   # 起点
            (cfg.EXIT, 1),    # 终点
            (cfg.GOLD, min(8, len(path_coords) // 4)),     # 金币
            (cfg.TRAP, min(6, len(path_coords) // 5)),     # 陷阱
            (cfg.LOCKER, 1),  # 宝箱
            (cfg.BOSS, 1),    # BOSS
        ]
        
        for item_symbol, count in items:
            for _ in range(count):
                if path_coords:
                    x, y = path_coords.pop()
                    self.grid[y][x] = item_symbol
    
    def get_start_position(self) -> Tuple[int, int]:
        """获取起始位置"""
        for r in range(self.height):
            for c in range(self.width):
                if self.grid[r][c] == cfg.START:
                    return (c, r)
        return (1, 1)  # 默认位置
    
    def get_tile_type(self, x: int, y: int) -> Optional[str]:
        """获取指定位置的瓦片类型"""
        if self.is_valid_position(x, y):
            return self.grid[y][x]
        return None
    
    def set_tile_type(self, x: int, y: int, tile_type: str) -> bool:
        """设置指定位置的类型"""
        if self.is_valid_position(x, y):
            self.grid[y][x] = tile_type
            return True
        return False
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """检查坐标是否有效"""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_wall(self, x: int, y: int) -> bool:
        """检查是否为墙壁"""
        if not self.is_valid_position(x, y):
            return True
        return self.grid[y][x] == cfg.WALL
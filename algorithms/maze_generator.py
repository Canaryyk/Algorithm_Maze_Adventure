"""
迷宫生成算法
"""

import random
from typing import List
import config as cfg


class DSU:
    """并查集数据结构，用于Kruskal算法"""
    
    def __init__(self, n: int):
        """初始化并查集"""
        self.parent: List[int] = list(range(n))
        self.num_sets: int = n
    
    def find(self, i: int) -> int:
        """查找根节点，路径压缩优化"""
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]
    
    def union(self, i: int, j: int) -> bool:
        """合并两个集合"""
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            self.parent[root_i] = root_j
            self.num_sets -= 1
            return True
        return False


def generate_kruskal_maze(width: int, height: int) -> List[List[str]]:
    """使用Kruskal算法生成迷宫"""
    # 初始化网格
    grid_width = width 
    grid_height = height 
    grid = [[cfg.WALL for _ in range(grid_width)] for _ in range(grid_height)]
    
    # 创建所有墙的列表
    walls = []
    for y in range(height):
        for x in range(width):
            if x < width - 1:
                walls.append(((x, y), (x + 1, y)))
            if y < height - 1:
                walls.append(((x, y), (x, y + 1)))
    
    random.shuffle(walls)
    
    # 初始化并查集
    num_cells = width * height
    dsu = DSU(num_cells)
    
    # 遍历墙列表，连接集合
    for wall in walls:
        cell1, cell2 = wall
        x1, y1 = cell1
        x2, y2 = cell2
        
        cell1_idx = y1 * width + x1
        cell2_idx = y2 * width + x2
        
        # 如果不连通，则打通墙
        if dsu.union(cell1_idx, cell2_idx):
            grid[y1 * 2 + 1][x1 * 2 + 1] = cfg.PATH
            grid[y2 * 2 + 1][x2 * 2 + 1] = cfg.PATH
            grid[y1 + y2 + 1][x1 + x2 + 1] = cfg.PATH
            
        if dsu.num_sets == 1:
            break
    
    return grid


def generate_recursive_division_maze(width: int, height: int) -> List[List[str]]:
    """使用递归分割法生成迷宫"""
    grid_width = width
    grid_height = height 
    grid = [[cfg.PATH for _ in range(grid_width)] for _ in range(grid_height)]
    
    # 构建外墙
    for i in range(grid_width):
        grid[0][i] = cfg.WALL
        grid[grid_height - 1][i] = cfg.WALL
    for i in range(grid_height):
        grid[i][0] = cfg.WALL
        grid[i][grid_width - 1] = cfg.WALL
    
    # 递归分割
    _recursive_divide(grid, 1, 1, grid_width - 2, grid_height - 2)
    
    return grid


def _recursive_divide(grid: List[List[str]], x: int, y: int, w: int, h: int) -> None:
    """递归分割辅助函数"""
    if w < 3 or h < 3:
        return
    
    # 决定砌墙方向
    if w < h:
        orientation = 'HORIZONTAL'
    elif h < w:
        orientation = 'VERTICAL'
    else:
        orientation = random.choice(['HORIZONTAL', 'VERTICAL'])
    
    if orientation == 'VERTICAL':
        # 垂直砌墙
        wall_x = x + 1 + 2 * random.randrange((w - 1) // 2)
        passage_y = y + 2 * random.randrange((h + 1) // 2)
        
        # 砌墙
        for i in range(y, y + h):
            grid[i][wall_x] = cfg.WALL
        # 开通道
        grid[passage_y][wall_x] = cfg.PATH
        
        # 递归处理左右区域
        _recursive_divide(grid, x, y, wall_x - x, h)
        _recursive_divide(grid, wall_x + 1, y, x + w - (wall_x + 1), h)
    
    else:  # HORIZONTAL
        # 水平砌墙
        wall_y = y + 1 + 2 * random.randrange((h - 1) // 2)
        passage_x = x + 2 * random.randrange((w + 1) // 2)
        
        # 砌墙
        for i in range(x, x + w):
            grid[wall_y][i] = cfg.WALL
        # 开通道
        grid[wall_y][passage_x] = cfg.PATH
        
        # 递归处理上下区域
        _recursive_divide(grid, x, y, w, wall_y - y)
        _recursive_divide(grid, x, wall_y + 1, w, y + h - (wall_y + 1))



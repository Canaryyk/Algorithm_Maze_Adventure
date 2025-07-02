# algorithms/maze_generator.py

import random
import config as cfg

class DSU:
    """
    一个并查集数据结构。
    用于Kruskal算法中快速判断两个单元格是否已连通。
    """
    def __init__(self, n):
        # 初始化，每个元素自成一个集合
        self.parent = list(range(n))
        self.num_sets = n

    def find(self, i):
        # 寻找元素i的根节点，并进行路径压缩优化
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        # 合并包含元素i和j的两个集合
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            self.parent[root_i] = root_j
            self.num_sets -= 1
            return True
        return False

def generate_kruskal_maze(width, height):
    """
    使用随机化Kruskal算法生成迷宫。

    :param width: 迷宫的单元格宽度 (奇数推荐)
    :param height: 迷宫的单元格高度 (奇数推荐)
    :return: 一个符合config规范的二维列表迷宫
    """
    # 1. 初始化一个填满墙的网格
    grid_width = width 
    grid_height = height 
    grid = [[cfg.WALL for _ in range(grid_width)] for _ in range(grid_height)]

    # 2. 创建所有内墙的列表
    # 一个墙由它所分隔的两个单元格坐标(cell_x, cell_y)来定义
    walls = []
    for y in range(height):
        for x in range(width):
            # 添加右侧的墙
            if x < width - 1:
                walls.append(((x, y), (x + 1, y)))
            # 添加下方的墙
            if y < height - 1:
                walls.append(((x, y), (x, y + 1)))

    # 3. 完全随机地打乱墙列表
    random.shuffle(walls)

    # 4. 初始化并查集，每个单元格是一个独立的集合
    num_cells = width * height
    dsu = DSU(num_cells)

    # 5. 遍历随机墙列表，连接集合
    for wall in walls:
        cell1, cell2 = wall
        x1, y1 = cell1
        x2, y2 = cell2

        # 将二维单元格坐标转换为一维的并查集索引
        cell1_idx = y1 * width + x1
        cell2_idx = y2 * width + x2

        # 如果两个单元格不连通，则打通墙并合并集合
        if dsu.union(cell1_idx, cell2_idx):
            # 将单元格本身和它们之间的墙都变成通路
            # 单元格在grid中的坐标是 (2*x+1, 2*y+1)
            # 墙在grid中的坐标是 (x1+x2+1, y1+y2+1)
            
            # 设置单元格为通路
            grid[y1 * 2 + 1][x1 * 2 + 1] = cfg.PATH
            grid[y2 * 2 + 1][x2 * 2 + 1] = cfg.PATH
            # 设置墙为通路
            grid[y1 + y2 + 1][x1 + x2 + 1] = cfg.PATH
            
        # 如果所有单元格都已连通，可以提前结束
        if dsu.num_sets == 1:
            break
            
    return grid




def generate_recursive_division_maze(width, height):
    """
    使用递归分割法生成迷宫。

    :param width: 迷宫的单元格宽度
    :param height: 迷宫的单元格高度
    :return: 一个符合config规范的二维列表迷宫
    """
    grid_width = width
    grid_height = height 
    grid = [[cfg.PATH for _ in range(grid_width)] for _ in range(grid_height)]

    # 1. 构建外墙
    for i in range(grid_width):
        grid[0][i] = cfg.WALL
        grid[grid_height - 1][i] = cfg.WALL
    for i in range(grid_height):
        grid[i][0] = cfg.WALL
        grid[i][grid_width - 1] = cfg.WALL

    # 2. 从整个区域开始递归分割
    _recursive_divide(grid, 1, 1, grid_width - 2, grid_height - 2)

    return grid

def _recursive_divide(grid, x, y, w, h):
    """
    递归分割辅助函数

    :param grid: 迷宫网格
    :param x: 当前区域的左上角x坐标
    :param y: 当前区域的左上角y坐标
    :param w: 当前区域的宽度
    :param h: 当前区域的高度
    """
    if w < 3 or h < 3:
        return

    # 1. 决定砌墙的方向
    # 如果区域更宽，则垂直砌墙；如果更高，则水平砌墙；如果宽高相等，则随机选择。
    if w < h:
        orientation = 'HORIZONTAL'
    elif h < w:
        orientation = 'VERTICAL'
    else:
        orientation = random.choice(['HORIZONTAL', 'VERTICAL'])

    if orientation == 'VERTICAL':
        # 2a. 垂直砌墙
        # 墙壁必须在偶数坐标上
        wall_x = x + 1 + 2 * random.randrange((w - 1) // 2)
        # 通道必须在奇数坐标上
        passage_y = y + 2 * random.randrange((h + 1) // 2)
        
        # 砌墙
        for i in range(y, y + h):
            grid[i][wall_x] = cfg.WALL
        # 开一个通道
        grid[passage_y][wall_x] = cfg.PATH

        # 3a. 对左右两个子区域进行递归
        _recursive_divide(grid, x, y, wall_x - x, h)
        _recursive_divide(grid, wall_x + 1, y, x + w - (wall_x + 1), h)

    else: # 'HORIZONTAL'
        # 2b. 水平砌墙
        # 墙壁必须在偶数坐标上
        wall_y = y + 1 + 2 * random.randrange((h - 1) // 2)
        # 通道必须在奇数坐标上
        passage_x = x + 2 * random.randrange((w + 1) // 2)

        # 砌墙
        for i in range(x, x + w):
            grid[wall_y][i] = cfg.WALL
        # 开一个通道
        grid[wall_y][passage_x] = cfg.PATH

        # 3b. 对上下两个子区域进行递归
        _recursive_divide(grid, x, y, w, wall_y - y)
        _recursive_divide(grid, x, wall_y + 1, w, y + h - (wall_y + 1))
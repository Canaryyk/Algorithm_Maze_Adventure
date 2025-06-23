# config.py

#import pygame

# 屏幕与显示设置
SCREEN_WIDTH = 800  # 窗口宽度
SCREEN_HEIGHT = 600 # 窗口高度
GAME_TITLE = "算法迷宫探险"
FPS = 60  # 游戏帧率

# 迷宫网格设置
TILE_SIZE = 20  # 每个格子的像素大小
# 注意：迷宫的实际尺寸（行和列）将在生成时确定，这里只是格子大小

# 颜色定义 (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PLAYER_COLOR = BLUE       # 玩家颜色
WALL_COLOR = (50, 50, 50)   # 墙壁颜色
PATH_COLOR = (200, 200, 200)  # 通路颜色
START_COLOR = GREEN       # 起点颜色
END_COLOR = RED           # 终点颜色

# 玩家设置
PLAYER_SPEED = 5 # 玩家移动速度 (像素/帧)

# 迷宫地图元素符号 (用于内部数据表示)
# 这样做的好处是，如果想换成其他数字或字符，只需改这里
WALL = 0
PATH = 1
START = 2
END = 3
GOLD = 4
TRAP = 5
LOCKER = 6
BOSS = 7
# config.py

#import pygame

# 屏幕与显示设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 650 # 稍微增加高度以容纳HUD
GAME_TITLE = "算法迷宫探险"
FPS = 60

# 迷宫网格设置
TILE_SIZE = 25 # 稍微增大格子尺寸，让物品更清晰

# 颜色定义 (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)

# 地图元素颜色
PLAYER_COLOR = BLUE
WALL_COLOR = (50, 50, 50)
PATH_COLOR = (200, 200, 200)
START_COLOR = GREEN
END_COLOR = RED
GOLD_COLOR = YELLOW
TRAP_COLOR = ORANGE
LOCKER_COLOR = PURPLE
BOSS_COLOR = (80, 0, 20) # 深红色

# HUD (平视显示器) 设置
HUD_FONT_SIZE = 30
HUD_BG_COLOR = GREY
HUD_HEIGHT = 50

# 玩家设置
PLAYER_MAX_HEALTH = 100
PLAYER_SPEED = 4

# 游戏数值
TRAP_DAMAGE = 25
GOLD_VALUE = 10

# 迷宫地图元素符号 (用于内部数据表示)
PATH = ' '
WALL = '#'
START = 'S'
EXIT = 'E'
GOLD = 'G'
TRAP = 'T'
LOCKER = 'L'
BOSS = 'B'

# 地图元素数值映射 (用于算法处理)
ELEMENT_MAPPING = {
    PATH: 0,    # 可通行路径
    WALL: 1,    # 不可通行墙壁
    START: 2,   # 起点
    EXIT: 3,    # 终点
    GOLD: 4,    # 金币
    TRAP: 5,    # 陷阱
    LOCKER: 6,  # 密码锁
    BOSS: 7     # BOSS战
}
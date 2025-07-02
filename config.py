# config.py

# 颜色定义
BLACK = (0, 0, 0)
YELLOW = (255, 215, 0) # 使用金黄色 (Gold)
RED = (220, 20, 60) # 使用猩红色 (Crimson)

#import pygame

# 屏幕与显示设置
SCREEN_WIDTH = 750
SCREEN_HEIGHT = 750 # 稍微增加高度以容纳HUD
GAME_TITLE = "算法迷宫探险"
FPS = 60

# 迷宫网格设置
TILE_SIZE = 45 # 稍微增大格子尺寸，让物品更清晰
MAZE_WIDTH = 15 # 迷宫宽度 (格子数)
MAZE_HEIGHT = 15 # 迷宫高度 (格子数)


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

# --- 新增：视觉与动画常量 ---

# 精灵图集路径
PLAYER_SPRITESHEET_PATH = "Sprout Lands - Sprites - Basic pack/Characters/Basic Charakter Spritesheet.png"

# 精灵原始尺寸
SPRITE_PIXEL_SIZE = 16

# 玩家动画设置
PLAYER_ANIMATION_FRAMES = 4
CHAR_ANIM_DOWN = 0
CHAR_ANIM_LEFT = 1
CHAR_ANIM_RIGHT = 2
CHAR_ANIM_UP = 3
PLAYER_ANIMATION_SPEED = 0.15 # 切换动画帧的秒数

# 缩放与缓动
TILE_SCALING = TILE_SIZE / SPRITE_PIXEL_SIZE
PLAYER_SCALING = TILE_SCALING
LERP_FACTOR = 0.1
"""
游戏配置文件 - 核心迷宫游戏配置
"""

import pathlib
from typing import Dict

# === 项目路径配置 ===
PROJECT_ROOT = pathlib.Path(__file__).parent.resolve()
ASSET_PATH = PROJECT_ROOT / "image"

# === 颜色常量 ===
YELLOW = (255, 215, 0)  # 金黄色
RED = (220, 20, 60)  # 猩红色

# === 屏幕与显示设置 ===
SCREEN_WIDTH = 750
SCREEN_HEIGHT = 750
GAME_TITLE = "算法迷宫探险"

# === 迷宫设置 ===
TILE_SIZE = 45  # 每个格子的像素大小
MAZE_WIDTH = 15  # 迷宫宽度（格子数）
MAZE_HEIGHT = 15  # 迷宫高度（格子数）

# === 玩家设置 ===
PLAYER_MAX_HEALTH = 100
PLAYER_SPEED = 4

# === 游戏数值 ===
TRAP_DAMAGE = 30
GOLD_VALUE = 50

# === 地图元素符号 ===
PATH = ' '     # 可通行路径
WALL = '#'     # 墙壁
START = 'S'    # 起点
EXIT = 'E'     # 终点
GOLD = 'G'     # 金币
TRAP = 'T'     # 陷阱
LOCKER = 'L'   # 宝箱
BOSS = 'B'     # BOSS

# === 图像缩放配置 ===
PNG_SPRITE_SIZE = 96  # PNG图片的实际尺寸
GIF_SPRITE_SIZE = 512  # GIF图片的实际尺寸

# 缩放系数计算
PNG_SCALING = TILE_SIZE / PNG_SPRITE_SIZE
GIF_SCALING = TILE_SIZE / GIF_SPRITE_SIZE

# === 资源路径配置 ===
# 玩家动画GIF路径
PLAYER_ANIM_PATHS: Dict[str, pathlib.Path] = {
    "down": ASSET_PATH / "down.gif",
    "up": ASSET_PATH / "up.gif",
    "left": ASSET_PATH / "left.gif",
    "right": ASSET_PATH / "right.gif",
}

# 环境素材路径 - 智能墙壁系统
WALL_PATHS = {
    "horizontal_middle": ASSET_PATH / "wall_horizontal_middle.png",
    "vertical_middle": ASSET_PATH / "wall_vertical_middle.png", 
    "vertical_bottom": ASSET_PATH / "wall_vertical_bottom.png",
    "vertical_top": ASSET_PATH / "wall_vertical_top.png",
    "left_bottom": ASSET_PATH / "wall_left_bottom.png",
    "left_top": ASSET_PATH / "wall_left_top.png",
    "right_bottom": ASSET_PATH / "wall_right_bottom.png",
    "right_top": ASSET_PATH / "wall_right_top.png",
    "T_type": ASSET_PATH / "wall_T_type.png",
}

# 向后兼容的默认墙壁路径
WALL_PATH = WALL_PATHS["horizontal_middle"]
GRASS_PATHS = [
    ASSET_PATH / "grass1.png",
    ASSET_PATH / "grass2.png",
    ASSET_PATH / "grass3.png",
    ASSET_PATH / "grass4.png"
]

# 物品素材路径
GOLD_PATH = ASSET_PATH / "coin.gif"
TRAP_PATH = ASSET_PATH / "trap.png"
BOSS_PATH = ASSET_PATH / "Chicken Sprites.gif"

# 交互对象路径
CHEST_CLOSED_PATH = ASSET_PATH / "chest(close).png"
CHEST_OPEN_PATH = ASSET_PATH / "chest(open).png"
EXIT_CLOSED_PATH = ASSET_PATH / "exit(close).png"
EXIT_OPEN_PATH = ASSET_PATH / "exit(open).png"
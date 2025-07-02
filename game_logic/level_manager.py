# game_logic/level_manager.py
import arcade
import random
import config as cfg
from .interactive_objects import ChestSprite, ExitSprite

def _pos_from_grid(grid_x, grid_y, window_height):
    """将网格坐标转换为屏幕像素坐标。"""
    return (
        grid_x * cfg.TILE_SIZE + cfg.TILE_SIZE / 2,
        window_height - (grid_y * cfg.TILE_SIZE + cfg.TILE_SIZE / 2)
    )

def _get_wall_rotation(maze_grid, row, col):
    """
    根据墙壁周围的邻居情况计算合适的旋转角度
    智能分析连接模式，使墙壁能够自然连接
    
    Args:
        maze_grid: 迷宫网格
        row: 当前墙壁的行位置
        col: 当前墙壁的列位置
    
    Returns:
        float: 旋转角度（度）
    """
    height = len(maze_grid)
    width = len(maze_grid[0]) if height > 0 else 0
    
    # 检查四个方向的直接邻居
    up = row > 0 and maze_grid[row - 1][col] == cfg.WALL
    down = row < height - 1 and maze_grid[row + 1][col] == cfg.WALL
    left = col > 0 and maze_grid[row][col - 1] == cfg.WALL
    right = col < width - 1 and maze_grid[row][col + 1] == cfg.WALL
    
    # 统计连接数量和方向
    horizontal_connections = left + right  # 左右连接数
    vertical_connections = up + down       # 上下连接数
    total_connections = horizontal_connections + vertical_connections
    
    # 判断是否为边界墙
    is_boundary = (row == 0 or row == height - 1 or 
                  col == 0 or col == width - 1)
    
    # 智能旋转逻辑
    if total_connections == 0:
        # 孤立墙壁：根据位置决定默认方向
        if is_boundary:
            # 边界孤立墙：根据边界位置决定
            if row == 0 or row == height - 1:
                return 0.0  # 顶部/底部边界，水平方向
            else:
                return 90.0  # 左右边界，垂直方向
        else:
            return 0.0  # 内部孤立墙，默认水平
    
    elif total_connections == 1:
        # 端点墙壁：根据连接方向决定
        if up or down:
            return 90.0  # 垂直连接
        else:
            return 0.0   # 水平连接
    
    elif total_connections == 2:
        # 两个连接：判断是直线还是转角
        if vertical_connections == 2:
            # 上下都连接：垂直墙
            return 90.0
        elif horizontal_connections == 2:
            # 左右都连接：水平墙
            return 0.0
        else:
            # 转角情况：优先考虑主要连接方向
            # 如果是边界转角，根据边界方向决定
            if is_boundary:
                if row == 0 or row == height - 1:
                    return 0.0  # 顶部/底部边界转角，水平优先
                else:
                    return 90.0  # 左右边界转角，垂直优先
            else:
                # 内部转角：根据迷宫结构趋势决定
                # 检查更远的邻居来判断趋势
                far_up = row > 1 and maze_grid[row - 2][col] == cfg.WALL
                far_down = row < height - 2 and maze_grid[row + 2][col] == cfg.WALL
                far_left = col > 1 and maze_grid[row][col - 2] == cfg.WALL
                far_right = col < width - 2 and maze_grid[row][col + 2] == cfg.WALL
                
                extended_vertical = far_up or far_down
                extended_horizontal = far_left or far_right
                
                if extended_vertical and not extended_horizontal:
                    return 90.0
                elif extended_horizontal and not extended_vertical:
                    return 0.0
                else:
                    # 默认根据第一个连接方向
                    return 90.0 if (up or down) else 0.0
    
    else:
        # 三个或四个连接：十字路口
        # 根据主要连接方向决定
        if vertical_connections >= horizontal_connections:
            return 90.0  # 垂直为主
        else:
            return 0.0   # 水平为主

def setup_level(game_maze, window_height):
    """
    根据迷宫数据模型创建所有关卡精灵。
    返回一个包含所有 SpriteList 的字典。
    """
    sprite_lists = {
        "floor": arcade.SpriteList(),
        "wall": arcade.SpriteList(use_spatial_hash=True),
        "gold": arcade.SpriteList(use_spatial_hash=True),
        "trap": arcade.SpriteList(use_spatial_hash=True),
        "exit": arcade.SpriteList(use_spatial_hash=True),
        "locker": arcade.SpriteList(use_spatial_hash=True),
        "boss": arcade.SpriteList(use_spatial_hash=True),
        "decoration": arcade.SpriteList(),
    }
    
    player_start_pos = (0, 0)

    for r, row in enumerate(game_maze.grid):
        for c, tile_type in enumerate(row):
            pos = _pos_from_grid(c, r, window_height)
            
            # 铺设随机草地
            grass_path = random.choice(cfg.GRASS_PATHS)
            floor = arcade.Sprite(str(grass_path), cfg.PNG_SCALING)
            floor.position = pos
            sprite_lists["floor"].append(floor)

            if tile_type == cfg.WALL:
                # 创建智能墙壁，根据邻居情况调整旋转
                sprite = arcade.Sprite(str(cfg.WALL_PATH), cfg.PNG_SCALING)
                sprite.position = pos
                
                # 计算并应用旋转角度
                rotation_angle = _get_wall_rotation(game_maze.grid, r, c)
                sprite.angle = rotation_angle
                
                sprite_lists["wall"].append(sprite)
            
            elif tile_type == cfg.GOLD:
                # 暂时使用静态纹理替代动画，避免动画错误
                sprite = arcade.Sprite(str(cfg.GOLD_PATH), scale=cfg.GIF_SCALING)
                sprite.position = pos
                sprite_lists["gold"].append(sprite)

            elif tile_type == cfg.TRAP:
                sprite = arcade.Sprite(str(cfg.TRAP_PATH), cfg.PNG_SCALING)
                sprite.position = pos
                sprite_lists["trap"].append(sprite)

            elif tile_type == cfg.BOSS:
                # 暂时使用静态纹理替代动画，避免动画错误
                sprite = arcade.Sprite(str(cfg.BOSS_PATH), scale=cfg.GIF_SCALING)
                sprite.position = pos
                sprite_lists["boss"].append(sprite)
                
            elif tile_type == cfg.LOCKER:
                sprite = ChestSprite(scale=cfg.PNG_SCALING)
                sprite.position = pos
                sprite_lists["locker"].append(sprite)
            
            elif tile_type == cfg.EXIT:
                sprite = ExitSprite(scale=cfg.PNG_SCALING)
                sprite.position = pos
                sprite_lists["exit"].append(sprite)
                
            elif tile_type == cfg.START:
                player_start_pos = pos

    return sprite_lists, player_start_pos 
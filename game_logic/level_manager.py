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

def _get_wall_type_and_rotation(maze_grid, row, col):
    """
    根据墙壁周围的邻居情况选择合适的墙壁类型和旋转角度
    精确分析每种连接模式，选择最佳的墙壁素材
    
    Args:
        maze_grid: 迷宫网格
        row: 当前墙壁的行位置
        col: 当前墙壁的列位置
    
    Returns:
        tuple: (墙壁类型key, 旋转角度)
    """
    height = len(maze_grid)
    width = len(maze_grid[0]) if height > 0 else 0
    
    # 检查四个方向的直接邻居
    up = row > 0 and maze_grid[row - 1][col] == cfg.WALL
    down = row < height - 1 and maze_grid[row + 1][col] == cfg.WALL
    left = col > 0 and maze_grid[row][col - 1] == cfg.WALL
    right = col < width - 1 and maze_grid[row][col + 1] == cfg.WALL
    
    # 统计连接数量
    connection_count = sum([up, down, left, right])
    
    # 根据连接模式精确选择墙壁类型
    if connection_count == 0:
        # 孤立墙壁 - 默认使用水平中段墙
        return "horizontal_middle", 0.0
    
    elif connection_count == 1:
        # 端点墙壁 - 根据连接方向选择合适的端点素材
        if up:
            # 只有上方连接 - 墙壁底部，使用垂直底部墙
            return "vertical_bottom", 0.0
        elif down:
            # 只有下方连接 - 墙壁顶部，使用垂直顶部墙
            return "vertical_top", 0.0
        elif left:
            # 只有左方连接 - 墙壁右端，使用水平中段墙
            return "horizontal_middle", 0.0
        elif right:
            # 只有右方连接 - 墙壁左端，使用水平中段墙
            return "horizontal_middle", 0.0
    
    elif connection_count == 2:
        # 两个连接：直线墙或转角墙
        if up and down:
            # 垂直直线墙 - 使用垂直中段墙
            return "vertical_middle", 0.0
        elif left and right:
            # 水平直线墙 - 使用水平中段墙
            return "horizontal_middle", 0.0
        else:
            # 转角墙 - 每种转角都有专用素材，无需旋转
            if down and left:
                # ┌ 上右转角 - 使用右上转角
                return "right_top", 0.0
            elif down and right:
                # ┐ 上左转角 - 使用左上转角
                return "left_top", 0.0
            elif up and left:
                # └ 下右转角 - 使用右下转角
                return "right_bottom", 0.0
            elif up and right:
                # ┘ 下左转角 - 使用左下转角
                return "left_bottom", 0.0
    
    elif connection_count == 3:
        # T型连接 - 只有缺少上连接的使用专用T型素材，其他保持原逻辑
        if not up:
            # ┬ 缺少上连接，下左右都有 - 使用专用T型素材
            return "T_type", 0.0
        elif not down:
            # ┴ 缺少下连接，上左右都有 - 使用水平主干
            return "horizontal_middle", 0.0
        elif not left:
            # ├ 缺少左连接，上下右都有 - 使用垂直主干
            return "vertical_middle", 0.0
        elif not right:
            # ┤ 缺少右连接，上下左都有 - 使用垂直主干
            return "vertical_middle", 0.0
    
    else:
        # 四个连接：┼ 十字路口 - 使用垂直中段作为主要结构
        return "vertical_middle", 0.0
    
    # 默认情况 - 应该不会到达这里
    return "horizontal_middle", 0.0

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
                # 创建智能墙壁，根据邻居情况选择合适的墙壁类型
                wall_type, rotation_angle = _get_wall_type_and_rotation(game_maze.grid, r, c)
                
                # 获取对应的墙壁素材路径
                wall_path = cfg.WALL_PATHS.get(wall_type, cfg.WALL_PATHS["horizontal_middle"])
                
                # 创建墙壁精灵
                sprite = arcade.Sprite(str(wall_path), cfg.PNG_SCALING)
                sprite.position = pos
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
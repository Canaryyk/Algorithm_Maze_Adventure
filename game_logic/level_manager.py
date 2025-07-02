# game_logic/level_manager.py
import arcade
import random
import config as cfg

def _pos_from_grid(grid_x, grid_y, window_height):
    """将网格坐标转换为屏幕像素坐标。"""
    return (
        grid_x * cfg.TILE_SIZE + cfg.TILE_SIZE / 2,
        window_height - (grid_y * cfg.TILE_SIZE + cfg.TILE_SIZE / 2)
    )

def setup_level(game_maze, window_height):
    """
    根据迷宫数据模型创建所有关卡精灵。
    返回一个包含所有 SpriteList 的字典。
    """
    # 初始化所有 SpriteList
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

    item_paths = {
        cfg.GOLD: "image/sun.png",
        cfg.TRAP: "image/boss.png",
        cfg.EXIT: "image/door(open).png",
        cfg.LOCKER: "image/door(close).png",
        cfg.BOSS: "image/boss.png",
    }
    
    player_start_pos = (0, 0)

    # 遍历模型数据，一次性创建所有精灵
    for r, row in enumerate(game_maze.grid):
        for c, tile_type in enumerate(row):
            pos = _pos_from_grid(c, r, window_height)

            if tile_type == cfg.WALL:
                sprite = arcade.Sprite(
                    "image/wall.png", 
                     scale=cfg.TILE_SCALING
                )
                # 检查每个墙壁精灵，确保它不是一个没有纹理或碰撞箱的"幽灵"精灵
                if sprite.texture is None or sprite.hit_box is None:
                    print(f"严重错误: 位于网格 ({c}, {r}) 的墙壁精灵是一个幽灵精灵，没有有效的纹理或碰撞箱!")
                    
                sprite.position = pos
                sprite_lists["wall"].append(sprite)
            else:
                floor = arcade.Sprite(
                    "Sprout Lands - Sprites - Basic pack/Tilesets/Grass.png", cfg.TILE_SCALING,
                    image_x=0, image_y=0, image_width=16, image_height=16
                )
                floor.position = pos
                sprite_lists["floor"].append(floor)

                if tile_type in item_paths:
                    path = item_paths[tile_type]
                    
                    # 统一简化精灵创建，避免因尺寸参数错误导致无碰撞箱
                    sprite = arcade.Sprite(path, cfg.TILE_SCALING)

                    if tile_type == cfg.GOLD:
                        sprite_lists["gold"].append(sprite)
                    elif tile_type == cfg.TRAP:
                        sprite_lists["trap"].append(sprite)
                    elif tile_type == cfg.EXIT:
                        sprite_lists["exit"].append(sprite)
                    elif tile_type == cfg.LOCKER:
                        sprite_lists["locker"].append(sprite)
                    elif tile_type == cfg.BOSS:
                        sprite_lists["boss"].append(sprite)
                    
                    sprite.position = pos
                elif tile_type == cfg.START:
                    player_start_pos = pos
    
    # 创建装饰
    for wall in sprite_lists["wall"]:
        if random.random() < 0.2:
            decoration_image = random.choice([
                "Sprout Lands - Sprites - Basic pack/Objects/Basic_Plants.png",
                "Sprout Lands - Sprites - Basic pack/Objects/Basic_Grass_Biom_things.png"
            ])
            decoration = arcade.Sprite(decoration_image, scale=cfg.TILE_SCALING * random.uniform(0.8, 1.2))
            decoration.position = wall.position
            sprite_lists["decoration"].append(decoration)

    return sprite_lists, player_start_pos 
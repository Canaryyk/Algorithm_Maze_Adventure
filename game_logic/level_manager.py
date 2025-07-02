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
        cfg.GOLD: "Sprout Lands - Sprites - Basic pack/Objects/Egg_item.png",
        cfg.TRAP: "Sprout Lands - Sprites - Basic pack/Objects/Basic_tools_and_meterials.png",
        cfg.EXIT: "Sprout Lands - Sprites - Basic pack/Tilesets/Doors.png",
        cfg.LOCKER: "Sprout Lands - Sprites - Basic pack/Objects/Chest.png",
        cfg.BOSS: "Sprout Lands - UI Pack - Basic pack/Sprite sheets/Dialouge UI/Emotes/Teemo Basic emote animations sprite sheet.png",
    }
    
    player_start_pos = (0, 0)

    # 遍历模型数据，一次性创建所有精灵
    for r, row in enumerate(game_maze.grid):
        for c, tile_type in enumerate(row):
            pos = _pos_from_grid(c, r, window_height)

            if tile_type == cfg.WALL:
                sprite = arcade.Sprite(
                    "Sprout Lands - Sprites - Basic pack/Tilesets/Wooden_House_Walls_Tilset.png", cfg.TILE_SCALING,
                    image_x=0, image_y=0, image_width=16, image_height=16
                )
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
                    
                    if tile_type == cfg.GOLD:
                        sprite = arcade.Sprite(path, cfg.TILE_SCALING)
                        sprite_lists["gold"].append(sprite)
                    elif tile_type == cfg.TRAP:
                        sprite = arcade.Sprite(path, cfg.TILE_SCALING, image_x=32, image_y=16, image_width=16, image_height=16)
                        sprite_lists["trap"].append(sprite)
                    elif tile_type == cfg.EXIT:
                        sprite = arcade.Sprite(path, cfg.TILE_SCALING, image_x=0, image_y=0, image_width=16, image_height=16)
                        sprite_lists["exit"].append(sprite)
                    elif tile_type == cfg.LOCKER:
                        sprite = arcade.Sprite(path, cfg.TILE_SCALING, image_x=0, image_y=0, image_width=16, image_height=16)
                        sprite_lists["locker"].append(sprite)
                    elif tile_type == cfg.BOSS:
                        sprite = arcade.Sprite(path, cfg.TILE_SCALING, image_x=0, image_y=0, image_width=32, image_height=32)
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
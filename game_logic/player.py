# player.py

import config as cfg
import arcade

class PlayerSprite(arcade.Sprite):
    """
    玩家精灵类，负责处理玩家的视觉呈现和动画
    """
    def __init__(self, start_pos):
        super().__init__(scale=cfg.PLAYER_SCALING)
        
        # 精灵位置
        self.position = start_pos
        
        # 动画属性
        self.walk_textures = {}
        self.idle_textures = {}
        self.direction = "down"
        self.animation_timer = 0
        self.current_frame = 0

        # 加载纹理
        self._load_textures()
        self.texture = self.idle_textures["down"]

    def _load_textures(self):
        """从图集中加载玩家动画纹理"""
        all_frames = arcade.load_spritesheet(
            cfg.PLAYER_SPRITESHEET_PATH,
            sprite_width=cfg.SPRITE_PIXEL_SIZE,
            sprite_height=cfg.SPRITE_PIXEL_SIZE,
            columns=cfg.PLAYER_ANIMATION_FRAMES,
            count=cfg.PLAYER_ANIMATION_FRAMES * 4
        )
        self.walk_textures["down"] = all_frames[cfg.CHAR_ANIM_DOWN*4 : cfg.CHAR_ANIM_DOWN*4 + 4]
        self.walk_textures["left"] = all_frames[cfg.CHAR_ANIM_LEFT*4 : cfg.CHAR_ANIM_LEFT*4 + 4]
        self.walk_textures["right"] = all_frames[cfg.CHAR_ANIM_RIGHT*4 : cfg.CHAR_ANIM_RIGHT*4 + 4]
        self.walk_textures["up"] = all_frames[cfg.CHAR_ANIM_UP*4 : cfg.CHAR_ANIM_UP*4 + 4]
        self.idle_textures["down"] = all_frames[cfg.CHAR_ANIM_DOWN*4]
        self.idle_textures["left"] = all_frames[cfg.CHAR_ANIM_LEFT*4]
        self.idle_textures["right"] = all_frames[cfg.CHAR_ANIM_RIGHT*4]
        self.idle_textures["up"] = all_frames[cfg.CHAR_ANIM_UP*4]

    def update_animation(self, delta_time: float, target_speed_x: float, target_speed_y: float):
        """根据玩家速度和方向更新动画"""
        is_moving = target_speed_x != 0 or target_speed_y != 0

        # 更新方向
        if target_speed_y > 0:
            self.direction = "up"
        elif target_speed_y < 0:
            self.direction = "down"
        elif target_speed_x < 0:
            self.direction = "left"
        elif target_speed_x > 0:
            self.direction = "right"
        
        # 更新动画帧
        if is_moving:
            self.animation_timer += delta_time
            if self.animation_timer > cfg.PLAYER_ANIMATION_SPEED:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % cfg.PLAYER_ANIMATION_FRAMES
                self.texture = self.walk_textures[self.direction][self.current_frame]
        else:
            self.animation_timer = 0
            self.current_frame = 0
            self.texture = self.idle_textures[self.direction]

class Player:
    """
    玩家逻辑类 - 与图形库无关的纯逻辑实现
    负责管理玩家状态、位置和交互逻辑
    """
    def __init__(self, start_x, start_y, maze):
        # 玩家属性
        self.health = cfg.PLAYER_MAX_HEALTH
        self.gold = 0
        
        # 玩家位置（网格坐标）
        self.grid_x = start_x
        self.grid_y = start_y
        
        # 存储迷宫引用，用于碰撞检测和交互
        self.maze = maze

        # 玩家移动状态
        self.change_x = 0
        self.change_y = 0

    def get_pixel_position(self):
        """获取玩家的像素坐标位置"""
        return (
            self.grid_x * cfg.TILE_SIZE + cfg.TILE_SIZE // 2,
            self.grid_y * cfg.TILE_SIZE + cfg.TILE_SIZE // 2
        )

    def set_grid_position(self, grid_x, grid_y):
        """设置玩家的网格坐标位置"""
        self.grid_x = grid_x
        self.grid_y = grid_y

    def update_from_pixel_position(self, pixel_x, pixel_y):
        """从像素坐标更新网格坐标"""
        self.grid_x = int(pixel_x // cfg.TILE_SIZE)
        self.grid_y = int(pixel_y // cfg.TILE_SIZE)

    def is_colliding_with_wall(self, grid_x, grid_y):
        """
        检查给定网格坐标是否与墙壁碰撞
        """
        # 检查边界
        if not (0 <= grid_x < self.maze.width and 0 <= grid_y < self.maze.height):
            return True # 视为与边界墙壁碰撞

        # 检查是否撞墙
        if self.maze.grid[grid_y][grid_x] == cfg.WALL:
            return True
        
        return False

    def can_move_to(self, grid_x, grid_y):
        """检查是否可以移动到指定网格坐标"""
        return not self.is_colliding_with_wall(grid_x, grid_y)

    def handle_interaction(self, grid_x=None, grid_y=None):
        """
        处理玩家与脚下格子的交互事件，返回交互的类型
        """
        if grid_x is None:
            grid_x = self.grid_x
        if grid_y is None:
            grid_y = self.grid_y
            
        tile_type = self.maze.get_tile_type(grid_x, grid_y)

        if tile_type == cfg.GOLD:
            self.gold += cfg.GOLD_VALUE
            self.maze.set_tile_type(grid_x, grid_y, cfg.PATH)
            return cfg.GOLD
        
        elif tile_type == cfg.TRAP:
            self.health -= cfg.TRAP_DAMAGE
            self.maze.set_tile_type(grid_x, grid_y, cfg.PATH)
            return cfg.TRAP
        
        elif tile_type == cfg.LOCKER:
            return cfg.LOCKER
            
        elif tile_type == cfg.BOSS:
            return cfg.BOSS

        elif tile_type == cfg.EXIT:
            return cfg.EXIT

        return None

    def is_dead(self):
        """检查玩家是否死亡"""
        return self.health <= 0

    def reset(self):
        """重置玩家状态"""
        self.health = cfg.PLAYER_MAX_HEALTH
        self.gold = 0
        self.change_x = 0
        self.change_y = 0

    def get_status(self):
        """获取玩家状态信息"""
        return {
            'health': self.health,
            'gold': self.gold,
            'position': (self.grid_x, self.grid_y),
            'pixel_position': self.get_pixel_position()
        }
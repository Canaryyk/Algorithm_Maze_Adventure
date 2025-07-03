"""
玩家模块 - 核心迷宫游戏玩家功能
"""

import arcade
from typing import Dict, Tuple, Optional
import config as cfg


class PlayerSprite(arcade.Sprite):
    """玩家精灵类，负责玩家的视觉呈现"""
    
    def __init__(self, start_pos: Tuple[float, float]):
        """初始化玩家精灵"""
        super().__init__(scale=cfg.GIF_SCALING)
        
        # 加载所有方向的纹理
        self._load_textures()
        
        # 设置初始状态
        self.direction = 'down'
        self.texture = self.walk_textures[self.direction]
        
        # 设置碰撞箱
        self.hit_box = (
            (-cfg.TILE_SIZE * 0.3, -cfg.TILE_SIZE * 0.4),
            (cfg.TILE_SIZE * 0.3, -cfg.TILE_SIZE * 0.4),
            (cfg.TILE_SIZE * 0.3, cfg.TILE_SIZE * 0.2),
            (-cfg.TILE_SIZE * 0.3, cfg.TILE_SIZE * 0.2)
        )
        
        self.position = start_pos
    
    def _load_textures(self) -> None:
        """加载各方向纹理"""
        self.walk_textures: Dict[str, arcade.Texture] = {}
        for direction, path in cfg.PLAYER_ANIM_PATHS.items():
            self.walk_textures[direction] = arcade.load_texture(str(path))
            
    def update_player_animation(self, target_speed_x: float, target_speed_y: float) -> None:
        """根据移动方向切换纹理"""
        is_moving = target_speed_x != 0 or target_speed_y != 0
        
        if not is_moving:
            return
            
        # 判断新方向
        if abs(target_speed_y) > abs(target_speed_x):
            new_direction = "up" if target_speed_y > 0 else "down"
        else:
            new_direction = "right" if target_speed_x > 0 else "left"
            
        # 切换纹理
        if new_direction != self.direction:
            self.direction = new_direction
            self.texture = self.walk_textures[self.direction]


class Player:
    """玩家逻辑类 - 核心迷宫游戏功能"""
    
    def __init__(self, start_x: int, start_y: int, maze):
        """初始化玩家"""
        # 玩家属性
        self.resources = 0 # 初始资源
        
        # 玩家位置（网格坐标）
        self.grid_x = start_x
        self.grid_y = start_y
        
        # 迷宫引用
        self.maze = maze
    
    def set_grid_position(self, grid_x: int, grid_y: int) -> None:
        """设置玩家网格坐标"""
        self.grid_x = grid_x
        self.grid_y = grid_y
    
    def handle_interaction(self, grid_x: Optional[int] = None, grid_y: Optional[int] = None) -> Optional[str]:
        """处理玩家交互事件。返回交互类型字符串，以便触发音效等。"""
        if grid_x is None:
            grid_x = self.grid_x
        if grid_y is None:
            grid_y = self.grid_y
        
        tile_type = self.maze.get_tile_type(grid_x, grid_y)
        
        if tile_type == cfg.RESOURCE_NODE:
            self.add_resources(cfg.RESOURCE_VALUE)
            self.maze.clear_tile(grid_x, grid_y) # 直接修改迷宫数据
            print(f"捡到资源! 当前资源: {self.resources}")
            return cfg.RESOURCE_NODE
        
        elif tile_type == cfg.TRAP:
            self.deduct_resources(cfg.TRAP_PENALTY)
            self.maze.clear_tile(grid_x, grid_y) # 直接修改迷宫数据
            print(f"踩到陷阱! 剩余资源: {self.resources}")
            return cfg.TRAP
        
        elif tile_type in [cfg.LOCKER, cfg.BOSS, cfg.EXIT]:
            # 对于这些复杂交互，只返回类型，由主循环处理
            return tile_type
        
        return None
    
    def add_resources(self, amount: int):
        """增加指定数量的资源"""
        self.resources += amount
        print(f"资源增加: +{amount}, 当前资源: {self.resources}")
    
    def deduct_resources(self, amount: int):
        """扣除指定数量的资源"""
        self.resources -= amount
        print(f"资源扣除: -{amount}, 当前资源: {self.resources}")
    
    def reset(self) -> None:
        """重置玩家状态"""
        self.resources = 100
        self.grid_x = 0
        self.grid_y = 0

    def get_grid_position(self) -> tuple[int, int]:
        """返回玩家当前的网格坐标 (行, 列)"""
        return (self.grid_y, self.grid_x)

    def move(self, dx: int, dy: int) -> bool:
        """
        处理玩家在迷宫网格中的移动。
        """
        # 计算新的网格坐标
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy
        
        # 检查新的网格坐标是否在迷宫范围内
        if 0 <= new_x < self.maze.width and 0 <= new_y < self.maze.height:
            # 检查新的网格坐标是否是路径
            if self.maze.get_tile_type(new_x, new_y) == cfg.PATH:
                # 更新玩家的位置
                self.grid_x = new_x
                self.grid_y = new_y
                return True
        
        return False
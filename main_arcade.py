"""
算法迷宫探险 - 核心迷宫游戏
从起点出发，收集资源、避开陷阱、破解机关、击败BOSS，到达终点
"""

import arcade
import math
from typing import cast, Dict, Optional
import config as cfg
from game_logic.maze import Maze
from game_logic.player import Player, PlayerSprite
from game_logic.level_manager import setup_level
from game_logic.interactive_objects import ChestSprite, ExitSprite
from game_logic.input_handler import InputHandler


class MazeGame(arcade.Window):
    """
    迷宫游戏主窗口类
    核心功能：起点→迷宫→收集→陷阱→机关→BOSS→终点
    """
    
    def __init__(self, width: int, height: int, title: str):
        """初始化游戏窗口"""
        super().__init__(width, height, title)
        
        # 核心组件
        self.input_handler: Optional[InputHandler] = None
        
        # 游戏对象
        self.game_maze: Optional[Maze] = None
        self.player_logic: Optional[Player] = None
        self.player_sprite: Optional[PlayerSprite] = None
        self.physics_engine: Optional[arcade.PhysicsEngineSimple] = None
        
        # 精灵列表
        self.sprite_lists: Dict[str, arcade.SpriteList] = {}
        
        # 游戏状态
        self.animation_timer: float = 0.0
        
        # 设置背景色为黑色
        arcade.set_background_color((0, 0, 0))
    
    def setup(self) -> None:
        """设置游戏资源和初始状态"""
        # 初始化输入处理
        self.input_handler = InputHandler()
        
        # 创建迷宫
        self.game_maze = Maze(cfg.MAZE_WIDTH, cfg.MAZE_HEIGHT, use_generated=False)
        
        # 创建关卡精灵
        self.sprite_lists, player_start_pos = setup_level(self.game_maze, self.height)
        
        # 创建玩家
        start_x, start_y = self.game_maze.get_start_position()
        self.player_logic = Player(start_x, start_y, self.game_maze)
        self.player_sprite = PlayerSprite(start_pos=player_start_pos)
        
        # 设置物理引擎
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, 
            self.sprite_lists["wall"]
        )
    
    def on_draw(self) -> None:
        """绘制游戏画面"""
        arcade.start_render()
        
        # 绘制游戏层（按顺序）
        render_order = ["floor", "wall", "decoration", "gold", "trap", "exit", "locker", "boss"]
        for layer_name in render_order:
            sprite_list = self.sprite_lists.get(layer_name)
            if sprite_list:
                sprite_list.draw()
        
        # 绘制玩家
        if self.player_sprite:
            self.player_sprite.draw()
        
        # 绘制简单HUD
        self._draw_hud()
    
    def _draw_hud(self) -> None:
        """绘制游戏HUD"""
        if not self.player_logic:
            return
            
        # 绘制金币数量
        arcade.draw_text(
            f"金币: {self.player_logic.gold}", 
            10, self.height - 25, 
            cfg.YELLOW, 18
        )
        
        # 绘制生命值
        arcade.draw_text(
            f"生命值: {self.player_logic.health}", 
            150, self.height - 25, 
            cfg.RED, 18
        )
    
    def on_update(self, delta_time: float) -> None:
        """更新游戏逻辑"""
        if not self._validate_game_components():
            return
        
        self.animation_timer += delta_time
        
        # 更新玩家移动
        self._update_player_movement()
        
        # 更新物理引擎
        if self.physics_engine:
            self.physics_engine.update()
        
        # 更新动画
        self._update_animations()
        
        # 处理交互
        self._handle_interactions()
        
        # 检查游戏结束条件
        self._check_game_over()
    
    def on_key_press(self, key: int, modifiers: int) -> None:
        """处理按键按下事件"""
        if self.input_handler:
            self.input_handler.on_key_press(key)
    
    def on_key_release(self, key: int, modifiers: int) -> None:
        """处理按键释放事件"""
        if self.input_handler:
            self.input_handler.on_key_release(key)
    
    def _validate_game_components(self) -> bool:
        """验证游戏核心组件是否已初始化"""
        return all([
            self.physics_engine,
            self.player_sprite,
            self.player_logic,
            self.input_handler
        ])
    
    def _update_player_movement(self) -> None:
        """更新玩家移动"""
        if not self.input_handler or not self.player_sprite:
            return
        
        # 获取移动向量
        target_speed_x, target_speed_y = self.input_handler.get_movement_vector()
        
        # 更新玩家动画纹理
        self.player_sprite.update_player_animation(target_speed_x, target_speed_y)
        
        # 设置速度
        self.player_sprite.change_x = target_speed_x
        self.player_sprite.change_y = target_speed_y
    
    def _update_animations(self) -> None:
        """更新动画效果"""
        # 更新陷阱"呼吸"动画
        breath_scale = cfg.PNG_SCALING + math.sin(self.animation_timer * 4) * (cfg.PNG_SCALING * 0.05)
        trap_list = self.sprite_lists.get("trap")
        
        if trap_list:
            for trap_sprite in trap_list:
                trap_sprite.scale = breath_scale
    
    def _handle_interactions(self) -> None:
        """处理玩家与物品的交互"""
        if not self.player_sprite or not self.player_logic or not self.game_maze:
            return
        
        # 转换为网格坐标
        grid_x = int(self.player_sprite.center_x // cfg.TILE_SIZE)
        grid_y = int((self.height - self.player_sprite.center_y) // cfg.TILE_SIZE)
        
        # 检查坐标有效性
        if not self.game_maze.is_valid_position(grid_x, grid_y):
            return
        
        # 处理交互
        interaction_result = self.player_logic.handle_interaction(grid_x, grid_y)
        
        if interaction_result:
            self._process_interaction_result(interaction_result, grid_x, grid_y)
    
    def _process_interaction_result(self, interaction_type: str, grid_x: int, grid_y: int) -> None:
        """处理交互结果"""
        if interaction_type == cfg.GOLD:
            if self.player_logic:
                print(f"捡到金币! 当前金币: {self.player_logic.gold}")
            self._remove_sprite_at_position(grid_x, grid_y, "gold")
        
        elif interaction_type == cfg.TRAP:
            if self.player_logic:
                print(f"踩到陷阱! 生命值: {self.player_logic.health}")
            self._remove_sprite_at_position(grid_x, grid_y, "trap")
        
        elif interaction_type == cfg.LOCKER:
            print("发现宝箱!")
            chest_sprite = self._find_sprite_at_position(grid_x, grid_y, "locker")
            if chest_sprite:
                typed_chest = cast(ChestSprite, chest_sprite)
                typed_chest.open()
        
        elif interaction_type == cfg.BOSS:
            print("遭遇BOSS! (战斗系统待实现)")
        
        elif interaction_type == cfg.EXIT:
            print("恭喜! 找到出口!")
            exit_sprite = self._find_sprite_at_position(grid_x, grid_y, "exit")
            if exit_sprite:
                typed_exit = cast(ExitSprite, exit_sprite)
                typed_exit.open()
    
    def _find_sprite_at_position(self, grid_x: int, grid_y: int, sprite_list_name: str) -> Optional[arcade.Sprite]:
        """在指定位置查找精灵"""
        sprite_list = self.sprite_lists.get(sprite_list_name)
        if not sprite_list:
            return None
        
        target_pos = self._grid_to_pixel_position(grid_x, grid_y)
        
        for sprite in sprite_list:
            if (abs(sprite.center_x - target_pos[0]) < cfg.TILE_SIZE / 4 and
                abs(sprite.center_y - target_pos[1]) < cfg.TILE_SIZE / 4):
                return sprite
        
        return None
    
    def _remove_sprite_at_position(self, grid_x: int, grid_y: int, sprite_list_name: str) -> bool:
        """移除指定位置的精灵"""
        sprite_list = self.sprite_lists.get(sprite_list_name)
        if not sprite_list:
            return False
        
        target_pos = self._grid_to_pixel_position(grid_x, grid_y)
        
        for sprite in sprite_list:
            if (abs(sprite.center_x - target_pos[0]) < cfg.TILE_SIZE / 4 and
                abs(sprite.center_y - target_pos[1]) < cfg.TILE_SIZE / 4):
                sprite.remove_from_sprite_lists()
                return True
        
        return False
    
    def _grid_to_pixel_position(self, grid_x: int, grid_y: int) -> tuple:
        """将网格坐标转换为像素坐标"""
        return (
            grid_x * cfg.TILE_SIZE + cfg.TILE_SIZE // 2,
            self.height - (grid_y * cfg.TILE_SIZE + cfg.TILE_SIZE // 2)
        )
    
    def _check_game_over(self) -> None:
        """检查游戏结束条件"""
        if self.player_logic and self.player_logic.health <= 0:
            print("游戏结束! 你被击败了...")
            self._restart_game()
    
    def _restart_game(self) -> None:
        """重新开始游戏"""
        self.setup()


def main() -> None:
    """主函数"""
    game = MazeGame(cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT, cfg.GAME_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main() 
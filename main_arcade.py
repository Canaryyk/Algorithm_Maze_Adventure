import arcade
from arcade.key import UP, DOWN, LEFT, RIGHT, W, A, S, D
import config as cfg
from game_logic.maze import Maze
from game_logic.player import Player, PlayerSprite
from game_logic.level_manager import setup_level
import random
import math
import pathlib

# --- 项目根目录 ---
# 这会获取 config.py 文件所在的目录 (即项目根目录)
PROJECT_ROOT = pathlib.Path(__file__).parent.resolve()

# --- Animation Constants ---
# 假设 "Basic Charakter Spritesheet.png" 是一个 4x4 的图集，每个精灵为 16x16 像素
PLAYER_SPRITESHEET_PATH = "Sprout Lands - Sprites - Basic pack/Characters/Basic Charakter Spritesheet.png"
SPRITE_PIXEL_SIZE = 16
PLAYER_ANIMATION_FRAMES = 4
# 图集中的行索引
CHAR_ANIM_DOWN = 0
CHAR_ANIM_LEFT = 1
CHAR_ANIM_RIGHT = 2
CHAR_ANIM_UP = 3
PLAYER_ANIMATION_SPEED = 0.15 # 切换动画帧的秒数

# 常量
TILE_SCALING = cfg.TILE_SIZE / SPRITE_PIXEL_SIZE # 根据精灵原始尺寸调整缩放比例
PLAYER_SCALING = TILE_SCALING
LERP_FACTOR = 0.1 # 缓动系数，值越小移动越平滑但响应越慢

class MazeGame(arcade.Window):
    """
    使用 Arcade 库的迷宫游戏主窗口，采用瓦片地图和精灵。
    """
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        
        # 初始化所有图层 (SpriteList)
        self.floor_list = None
        self.wall_list = None
        self.gold_list = None
        self.trap_list = None
        self.exit_list = None
        self.locker_list = None 
        self.boss_list = None   
        self.decoration_list = None 
        
        # 初始化玩家相关的属性
        self.player_sprite = None
        self.player_logic = None  # 玩家逻辑对象
        self.player_target_speed_x = 0
        self.player_target_speed_y = 0
        self.physics_engine = None

        # 游戏状态
        self.animation_timer = 0 
        self.game_maze = None  # 迷宫数据模型

        # 设置背景色
        arcade.set_background_color(cfg.BLACK)

    def _pos_from_grid(self, grid_x, grid_y):
        """将网格坐标转换为屏幕像素坐标。"""
        return (
            grid_x * cfg.TILE_SIZE + cfg.TILE_SIZE / 2,
            self.height - (grid_y * cfg.TILE_SIZE + cfg.TILE_SIZE / 2)
        )

    def setup(self):
        """
        设置游戏资源。
        """
        # --- 1. 创建迷宫数据模型 ---
        self.game_maze = Maze(cfg.MAZE_WIDTH, cfg.MAZE_HEIGHT)
        
        # --- 2. 创建并加载所有关卡精灵 ---
        sprite_lists, player_start_pos = setup_level(self.game_maze, self.height)
        self.floor_list = sprite_lists["floor"]
        self.wall_list = sprite_lists["wall"]
        self.gold_list = sprite_lists["gold"]
        self.trap_list = sprite_lists["trap"]
        self.exit_list = sprite_lists["exit"]
        self.locker_list = sprite_lists["locker"]
        self.boss_list = sprite_lists["boss"]
        self.decoration_list = sprite_lists["decoration"]

        # --- 3. 创建玩家逻辑和精灵对象 ---
        start_locations = self.game_maze.get_item_locations(cfg.START)
        if start_locations:
            start_x, start_y = start_locations[0]
            self.player_logic = Player(start_x, start_y, self.game_maze)
        else:
            self.player_logic = Player(0, 0, self.game_maze)
        
        self.player_sprite = PlayerSprite(start_pos=player_start_pos)

        # --- 4. 设置物理引擎 ---
        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)
        
        # --- 5. 重置游戏状态 ---
        self.animation_timer = 0
        self.player_target_speed_x = 0
        self.player_target_speed_y = 0

    def on_draw(self):
        arcade.start_render()
        
        # 依次绘制所有图层，确保它们不为None
        if self.floor_list: self.floor_list.draw()
        if self.wall_list: self.wall_list.draw()
        if self.decoration_list: self.decoration_list.draw() # 绘制装饰层
        if self.gold_list: self.gold_list.draw()
        if self.trap_list: self.trap_list.draw()
        if self.exit_list: self.exit_list.draw()
        if self.locker_list: self.locker_list.draw() # 新增
        if self.boss_list: self.boss_list.draw()     # 新增
        if self.player_sprite: self.player_sprite.draw()

        # 绘制HUD - 使用player_logic中的状态
        if self.player_logic:
            arcade.draw_text(f"Gold: {self.player_logic.gold}", 10, self.height - 25, cfg.YELLOW, 18)
            arcade.draw_text(f"Health: {self.player_logic.health}", 150, self.height - 25, cfg.RED, 18)

    def on_update(self, delta_time: float):
        self.animation_timer += delta_time

        if not self.physics_engine or not self.player_sprite or not self.player_logic:
            return
            
        # --- 更新玩家动画 ---
        self.player_sprite.update_animation(delta_time, self.player_target_speed_x, self.player_target_speed_y)

        # --- 平滑移动 ---
        self.player_sprite.change_x += (self.player_target_speed_x - self.player_sprite.change_x) * cfg.LERP_FACTOR
        self.player_sprite.change_y += (self.player_target_speed_y - self.player_sprite.change_y) * cfg.LERP_FACTOR
        self.physics_engine.update()

        # --- "呼吸"动画 ---
        breath_scale = cfg.TILE_SCALING + math.sin(self.animation_timer * 4) * (cfg.TILE_SCALING * 0.05)
        animating_lists = [self.gold_list, self.trap_list, self.exit_list, self.locker_list, self.boss_list]
        for sprite_list in animating_lists:
            if sprite_list:
                for item in sprite_list:
                    item.scale = breath_scale

        # --- 同步玩家逻辑对象的位置 ---
        # 将arcade精灵的位置同步到逻辑对象
        pixel_x = self.player_sprite.center_x
        pixel_y = self.height - self.player_sprite.center_y  # arcade坐标系转换
        
        # --- 使用player_logic处理交互 ---
        self._handle_interactions()

        # --- 检查游戏结束条件 ---
        if self.player_logic.health <= 0:
            print("游戏结束，你被陷阱击败了!")
            self.setup() # 重新开始游戏

    def _handle_interactions(self):
        """处理玩家与物品的交互，分离逻辑与视图"""
        if not self.player_sprite or not self.player_logic or not self.game_maze:
            return
            
        # 将屏幕坐标转换为网格坐标
        grid_x = int(self.player_sprite.center_x // cfg.TILE_SIZE)
        grid_y = int((self.height - self.player_sprite.center_y) // cfg.TILE_SIZE)
        
        # 检查坐标是否有效
        if not (0 <= grid_x < self.game_maze.width and 0 <= grid_y < self.game_maze.height):
            return
            
        # 调用逻辑层处理交互，并获取结果
        interaction_result = self.player_logic.handle_interaction(grid_x, grid_y)

        # 根据交互结果更新视图
        if interaction_result:
            if interaction_result == cfg.GOLD:
                print(f"捡到金币! 当前金币: {self.player_logic.gold}")
                self._remove_item_sprite_at_grid(grid_x, grid_y, self.gold_list)
            
            elif interaction_result == cfg.TRAP:
                print(f"踩到陷阱! 生命值: {self.player_logic.health}")
                self._remove_item_sprite_at_grid(grid_x, grid_y, self.trap_list)
            
            elif interaction_result == cfg.LOCKER:
                print("遇到一个机关! (解谜逻辑待实现)")
                
            elif interaction_result == cfg.BOSS:
                print("遭遇BOSS! (战斗逻辑待实现)")
                
            elif interaction_result == cfg.EXIT:
                print("恭喜你，到达终点!")
                self.setup() # 重新开始游戏

    def _remove_item_sprite_at_grid(self, grid_x, grid_y, sprite_list):
        """移除指定网格位置的精灵"""
        target_pos = self._pos_from_grid(grid_x, grid_y)
        for sprite in sprite_list:
            # 检查精灵是否在目标位置附近（允许小的误差）
            if abs(sprite.center_x - target_pos[0]) < cfg.TILE_SIZE/4 and \
               abs(sprite.center_y - target_pos[1]) < cfg.TILE_SIZE/4:
                sprite.remove_from_sprite_lists()
                break

    def on_key_press(self, key, modifiers):
        if not self.player_sprite:
            return
            
        if key == UP or key == W:
            self.player_target_speed_y = cfg.PLAYER_SPEED
        elif key == DOWN or key == S:
            self.player_target_speed_y = -cfg.PLAYER_SPEED
        elif key == LEFT or key == A:
            self.player_target_speed_x = -cfg.PLAYER_SPEED
        elif key == RIGHT or key == D:
            self.player_target_speed_x = cfg.PLAYER_SPEED

    def on_key_release(self, key, modifiers):
        if not self.player_sprite:
            return

        if key in (UP, W, DOWN, S):
            self.player_target_speed_y = 0
        elif key in (LEFT, A, RIGHT, D):
            self.player_target_speed_x = 0

def main():
    game = MazeGame(cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT, cfg.GAME_TITLE)
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main() 
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
from game_logic.interactive_objects import ChestSprite, ExitSprite, BossSprite, PuzzleChestSprite
from game_logic.input_handler import InputHandler
from game_logic.game_views import PuzzleView
from game_logic.battle_manager import BattleManager
from game_logic.audio_manager import audio_manager


class MazeGame(arcade.View):
    """
    迷宫游戏主视图类
    核心功能：起点→迷宫→收集→陷阱→机关→BOSS→终点
    """
    
    def __init__(self, window: arcade.Window):
        """初始化游戏视图"""
        super().__init__(window)
        
        # --- 游戏状态 ---
        self.is_battle_mode = False
        self.active_boss_sprite: Optional[BossSprite] = None
        self.panel_width = self.window.width // 2 # 战斗面板宽度
        self.is_encounter_animation = False
        self.encounter_timer = 0.0
        self.encounter_duration = 1.0 # 遭遇动画持续时间（加速1.5倍）

        # --- 摄像机 ---
        self.camera = arcade.Camera(self.window.width, self.window.height)
        self.gui_camera = arcade.Camera(self.window.width, self.window.height)

        # 核心组件
        self.input_handler: Optional[InputHandler] = None
        self.battle_manager: BattleManager = BattleManager(self.gui_camera, self.window)
        
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
    
    def on_show_view(self):
        """当视图显示时调用"""
        arcade.set_background_color((0, 0, 0))
        # 重置输入处理器的状态，防止角色在视图切换后继续移动
        if self.input_handler:
            self.input_handler.reset()
    
    def setup(self) -> None:
        """设置游戏资源和初始状态"""
        # 确保UI管理器被启用
        self.battle_manager.ui_manager.enable()

        # 初始化输入处理
        self.input_handler = InputHandler()
        
        # 创建迷宫
        self.game_maze = Maze(cfg.MAZE_WIDTH, cfg.MAZE_HEIGHT, use_generated=False)
        
        # 创建关卡精灵
        self.sprite_lists, player_start_pos = setup_level(self.game_maze, self.window.height)
        
        # 创建玩家
        start_x, start_y = self.game_maze.get_start_position()
        self.player_logic = Player(start_x, start_y, self.game_maze)
        self.player_sprite = PlayerSprite(start_pos=player_start_pos)
        
        # 设置物理引擎
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, 
            self.sprite_lists["wall"]
        )
        
        # 开始播放背景音乐
        audio_manager.play_background_music("background")
    
    def on_resize(self, width: int, height: int):
        """当窗口大小改变时调用。"""
        super().on_resize(width, height)
        self.camera.resize(width, height)
        self.gui_camera.resize(width, height)

        if self.is_battle_mode:
            # 战斗模式下，游戏相机只显示左侧迷宫区域
            self.camera.viewport = (0, 0, width - self.panel_width, height)
        else:
            # 普通模式下，相机覆盖整个窗口
            self.camera.viewport = (0, 0, width, height)

    def on_draw(self) -> None:
        """绘制游戏画面"""
        self.clear()

        # 激活游戏主摄像机
        self.camera.use()

        # 绘制游戏层（按顺序）
        render_order = ["floor", "wall", "decoration", "gold", "trap", "exit", "locker", "boss"]
        for layer_name in render_order:
            sprite_list = self.sprite_lists.get(layer_name)
            if sprite_list:
                sprite_list.draw()
        
        # 绘制玩家
        if self.player_sprite:
            self.player_sprite.draw()

        # 激活GUI摄像机
        self.gui_camera.use()
        
        # 绘制HUD和战斗面板
        self._draw_hud_and_panels()
    
    def _draw_hud_and_panels(self) -> None:
        """根据游戏模式绘制HUD和侧边面板"""
        if self.is_encounter_animation:
            # 绘制遭遇动画
            arcade.draw_lrtb_rectangle_filled(
                left=0, right=self.window.width, top=self.window.height, bottom=0,
                color=(0, 0, 0, 180) # 半透明黑色背景
            )
            arcade.draw_text(
                "遭遇 BOSS！",
                self.window.width / 2,
                self.window.height / 2,
                arcade.color.RED_DEVIL,
                font_size=70,
                font_name="SimHei", # 使用黑体
                bold=True,
                anchor_x="center",
                anchor_y="center"
            )
            return # 遭遇动画时，不绘制其他面板

        if self.is_battle_mode:
            # 绘制战斗面板背景
            arcade.draw_lrtb_rectangle_filled(
                left=self.window.width - self.panel_width,
                right=self.window.width,
                top=self.window.height,
                bottom=0,
                color=(40, 40, 40, 200) # 半透明深灰色
            )
            arcade.draw_text("战斗面板", 
                             self.window.width - self.panel_width / 2, 
                             self.window.height - 40, 
                             arcade.color.WHITE, 
                             font_size=20, 
                             anchor_x="center")
            # 绘制战斗面板内容
            self.battle_manager.on_draw()

        # 绘制通用HUD
        self._draw_hud()
    
    def _draw_hud(self) -> None:
        """绘制游戏HUD"""
        if not self.player_logic:
            return
            
        # 绘制金币数量
        arcade.draw_text(
            f"金币: {self.player_logic.gold}", 
            10, self.window.height - 25, 
            cfg.YELLOW, 18
        )
        
        # 绘制生命值
        arcade.draw_text(
            f"生命值: {self.player_logic.health}", 
            150, self.window.height - 25, 
            cfg.RED, 18
        )
        
        # 绘制音乐控制说明
        arcade.draw_text(
            "M:切换音乐 N:切换音效", 
            10, self.window.height - 50, 
            arcade.color.WHITE, 12
        )
    
    def on_update(self, delta_time: float) -> None:
        """更新游戏逻辑"""
        if self.is_encounter_animation:
            self.encounter_timer += delta_time
            if self.encounter_timer > self.encounter_duration:
                self.is_encounter_animation = False
                self._trigger_real_battle() # 计时结束后，真正开始战斗
            return

        if self.is_battle_mode:
            self.battle_manager.on_update(delta_time)
            return # 战斗时，暂停游戏世界的大部分更新

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
        
        # 根据玩家位置更新摄像机
        # self._center_camera_on_player() # 已禁用
    
    def on_key_press(self, key: int, modifiers: int) -> None:
        """处理按键按下事件"""
        if key == arcade.key.ESCAPE:
            if self.is_battle_mode:
                self.end_battle() # 按ESC结束战斗
            else:
                print("ESC pressed - could open a pause menu.")
        elif key == arcade.key.M:
            # M键切换背景音乐开/关
            audio_manager.toggle_music()
        elif key == arcade.key.N:
            # N键切换音效开/关
            audio_manager.toggle_effects()
        
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
        grid_y = int((self.window.height - self.player_sprite.center_y) // cfg.TILE_SIZE)
        
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
            # 播放捡金币音效
            audio_manager.play_sound_effect("get_gold")
            if self.player_logic:
                print(f"捡到金币! 当前金币: {self.player_logic.gold}")
            self._remove_sprite_at_position(grid_x, grid_y, "gold")
        
        elif interaction_type == cfg.TRAP:
            # 播放踩陷阱音效
            audio_manager.play_sound_effect("step_trap")
            if self.player_logic:
                print(f"踩到陷阱! 生命值: {self.player_logic.health}")
            self._remove_sprite_at_position(grid_x, grid_y, "trap")
        
        elif interaction_type == cfg.LOCKER:
            print("发现宝箱!")
            chest_sprite = self._find_sprite_at_position(grid_x, grid_y, "locker")
            if chest_sprite:
                # 检查是否是谜题宝箱并且已上锁
                if isinstance(chest_sprite, PuzzleChestSprite) and chest_sprite.is_locked:
                    print("这是一个带锁的谜题宝箱，切换到解谜场景...")
                    puzzle_view = PuzzleView(self, chest_sprite) # 传递宝箱精灵
                    self.window.show_view(puzzle_view)
                elif not getattr(chest_sprite, 'is_locked', False):
                    # 如果是普通宝箱或已解锁的谜题宝箱
                    typed_chest = cast(ChestSprite, chest_sprite)
                    if not typed_chest.is_open:
                        # 播放开宝箱音效
                        audio_manager.play_sound_effect("unlock_locker")
                        typed_chest.open()
                        print("宝箱已打开！")
        
        elif interaction_type == cfg.BOSS:
            print("发现BOSS!")
            boss_sprite = self._find_sprite_at_position(grid_x, grid_y, "boss")
            if boss_sprite and isinstance(boss_sprite, BossSprite) and not self.is_battle_mode:
                print("开始战斗...")
                self.start_battle(boss_sprite)
            else:
                if not boss_sprite:
                    print("未找到BOSS精灵")
                elif not isinstance(boss_sprite, BossSprite):
                    print(f"BOSS精灵类型错误: {type(boss_sprite)}")
                elif self.is_battle_mode:
                    print("已经在战斗模式中")
        
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
        """将网格坐标转换为屏幕像素坐标。"""
        return (
            grid_x * cfg.TILE_SIZE + cfg.TILE_SIZE / 2,
            self.window.height - (grid_y * cfg.TILE_SIZE + cfg.TILE_SIZE / 2)
        )
    
    def start_battle(self, boss_sprite: BossSprite):
        """开始战斗模式 - 现在只触发遭遇动画"""
        print("遭遇Boss，开始播放动画...")
        # 切换到战斗音乐
        audio_manager.play_background_music("boss_battle")
        self.is_encounter_animation = True
        self.encounter_timer = 0.0
        self.active_boss_sprite = boss_sprite
        
        # 从迷宫中移除BOSS标记，避免重复触发
        if self.game_maze and self.player_sprite:
            self.game_maze.set_tile_type(int(self.player_sprite.center_x // cfg.TILE_SIZE), 
                                         int((self.window.height - self.player_sprite.center_y) // cfg.TILE_SIZE), 
                                         cfg.PATH)

    def _trigger_real_battle(self):
        """遭遇动画结束后，真正设置战斗模式"""
        print("动画结束，正式进入战斗！")
        self.is_battle_mode = True
        
        # 拓宽窗口
        self.window.set_size(cfg.SCREEN_WIDTH + self.panel_width, cfg.SCREEN_HEIGHT)
        
        if self.active_boss_sprite:
            self.battle_manager.setup_battle(self.active_boss_sprite)

    def end_battle(self):
        """结束战斗模式"""
        print("战斗结束。")
        # 切换回背景音乐
        audio_manager.play_background_music("background")
        self.is_battle_mode = False
        
        # 移除已经击败的Boss
        if self.active_boss_sprite:
            self.active_boss_sprite.remove_from_sprite_lists()
            self.active_boss_sprite = None

        self.battle_manager.clear()
        
        # 恢复窗口到原始尺寸
        self.window.set_size(cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)

    def _check_game_over(self) -> None:
        """检查游戏是否结束"""
        if self.player_logic and self.player_logic.health <= 0:
            print("游戏结束! 按 R 重新开始。")
            # 这里可以显示一个游戏结束视图
    
    def _restart_game(self) -> None:
        """重新开始游戏"""
        print("重新开始游戏...")
        # 确保切换回背景音乐
        audio_manager.play_background_music("background")
        self.setup()


def main() -> None:
    """游戏主函数"""
    window = arcade.Window(
        width=cfg.SCREEN_WIDTH,
        height=cfg.SCREEN_HEIGHT,
        title=cfg.GAME_TITLE
    )
    game_view = MazeGame(window)
    game_view.setup()
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main() 
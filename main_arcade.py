"""
算法迷宫探险 - 核心迷宫游戏
从起点出发，收集资源、避开陷阱、破解机关、击败BOSS，到达终点
"""

import arcade
import arcade.color
import arcade.key
import math
import threading
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
from algorithms.pathfinding import find_maze_path
from game_logic.ai_agent import AIAgent, find_shortest_path as ai_find_path # 导入 AIAgent 类和寻路函数


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
        self.is_game_finished = False # 新增：游戏结束状态
        self.last_battle_rounds = 0 # 新增：记录上一场战斗的回合数

        # --- 寻路功能属性 ---
        self.optimal_path = []
        self.is_showing_path = False
        self.is_calculating_path = False # 新增：标记是否正在计算路径
        self.path_calculation_result: Optional[tuple] = None # 新增：存储线程计算结果
        self.path_target_index = 0
        self.path_sprites: Optional[arcade.SpriteList] = None

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
        
        # AI 代理逻辑
        self.ai_agent: Optional[AIAgent] = None
        self.is_ai_control_active = False

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
        
        # 初始化路径精灵列表
        self.path_sprites = arcade.SpriteList()

        # 创建玩家
        start_x_grid, start_y_grid = self.game_maze.get_start_position() # 获取迷宫起始点的网格坐标
        self.player_logic = Player(start_x_grid, start_y_grid, self.game_maze)
        self.player_sprite = PlayerSprite(start_pos=player_start_pos) # player_start_pos 是玩家精灵的像素坐标

        # 设置 AI 代理逻辑 (无状态)
        self.ai_agent = AIAgent()
        
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
        # 相机尺寸会由窗口自动管理
        self.camera.resize(width, height)
        self.gui_camera.resize(width, height)

    def on_draw(self) -> None:
        """绘制游戏画面"""
        self.clear()

        # 激活游戏主摄像机
        self.camera.use()

        # 绘制游戏层（按顺序）
        render_order = ["floor", "wall", "decoration", "resources", "trap", "exit", "locker", "boss"]
        for layer_name in render_order:
            sprite_list = self.sprite_lists.get(layer_name)
            if sprite_list:
                sprite_list.draw()
        
        # 绘制路径
        if self.path_sprites:
            self.path_sprites.draw()
        
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

        if self.is_game_finished:
            arcade.draw_lrtb_rectangle_filled(
                left=0, right=self.window.width, top=self.window.height, bottom=0,
                color=(0, 0, 0, 180)
            )
            arcade.draw_text(
                "游戏结束",
                self.window.width / 2, self.window.height / 2 + 50,
                arcade.color.WHITE, font_size=50, anchor_x="center", font_name="SimHei"
            )
            if self.player_logic:
                arcade.draw_text(
                    f"最终剩余资源: {self.player_logic.resources}",
                    self.window.width / 2, self.window.height / 2 - 20,
                    cfg.YELLOW, font_size=30, anchor_x="center", font_name="SimHei"
                )
            return

        if self.is_calculating_path:
            arcade.draw_text(
                "正在计算路径...",
                self.window.width / 2, self.window.height / 2,
                arcade.color.WHITE, font_size=40,
                anchor_x="center"
            )
            
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
            
        # 绘制资源数量
        arcade.draw_text(
            f"资源: {self.player_logic.resources}", 
            10, self.window.height - 25, 
            cfg.YELLOW, 18
        )
        
        # 绘制音乐控制说明
        arcade.draw_text(
            "M:切换音乐 N:切换音效", 
            10, self.window.height - 50, 
            arcade.color.WHITE, 12
        )

        # 绘制 AI 状态
        ai_status = "激活" if self.is_ai_control_active else "禁用"
        arcade.draw_text(
            f"AI: {ai_status} (I)",
            10, self.window.height - 75,
            arcade.color.CYAN, 12
        )
    
    def on_update(self, delta_time: float) -> None:
        """更新游戏逻辑"""
        # 新增：游戏结束后暂停更新
        if self.is_game_finished:
            return

        # 检查玩家路径计算是否完成 (这是玩家的自动寻路，与AI代理独立)
        if self.is_calculating_path:
            if self.path_calculation_result is not None:
                self._on_path_found(self.path_calculation_result)
                self.path_calculation_result = None # 消费结果
            return # 计算时暂停游戏更新

        if self.is_encounter_animation:
            self.encounter_timer += delta_time
            if self.encounter_timer > self.encounter_duration:
                self.is_encounter_animation = False
                self._trigger_real_battle() # 计时结束后，真正开始战斗
            return

        if self.is_battle_mode:
            # 新增：检查战斗是否结束
            if self.battle_manager.is_battle_finished:
                self.end_battle()
                return

            self.battle_manager.on_update(delta_time)
            return # 战斗时，暂停游戏世界的大部分更新

        if not self._validate_game_components():
            return
        
        self.animation_timer += delta_time
        
        # 如果 AI 控制激活，则更新 AI 逻辑
        if self.is_ai_control_active and self.ai_agent and self.player_logic and self.game_maze and not self.is_showing_path:
            current_pos_grid = self.player_logic.get_grid_position()
            
            # 1. 让AI大脑决定下一个目标
            target_pos = self.ai_agent.decide_next_target(current_pos_grid, self.game_maze.grid)
            
            # 2. 如果AI没有给出短期目标，则将最终出口作为目标
            if target_pos is None:
                exit_pos_xy = self.game_maze.get_exit_position()
                if exit_pos_xy:
                    # 关键修正：将 (x, y) 转换为 (row, col)，即 (y, x)
                    target_pos = (exit_pos_xy[1], exit_pos_xy[0]) 
                else:
                    self.optimal_path = [] # 没有出口，清空路径
                    return

            # 3. 如果有目标，则规划路径并开始移动
            if target_pos:
                path = ai_find_path(self.game_maze.grid, current_pos_grid, target_pos)
                
                # 关键修正：实现真正的"贪心"，只走路径的第一步
                if path and len(path) > 1:
                    # AI不再执行完整路径，而是只向目标走一步，然后在下一帧重新决策
                    self.optimal_path = [path[0], path[1]] 
                    self.path_target_index = 1
                    self.is_showing_path = True
                    # 路径只有一步，不需要绘制精灵，避免闪烁
                    if self.path_sprites:
                        self.path_sprites.clear()
        
        # 更新玩家移动（已整合手动和自动寻路）
        self._update_player_movement()

        # 更新物理引擎
        if self.physics_engine:
            self.physics_engine.update()

        # 更新动画
        self._update_animations()
        
        # 处理交互
        self._handle_interactions()

        # 检查玩家的游戏结束条件
        self._check_game_over()
        
        # 根据玩家位置更新摄像机 (已禁用，保留为注释)
        # self._center_camera_on_player()
    
    def on_key_press(self, key: int, modifiers: int) -> None:
        """当按键按下时调用"""
        if self.input_handler:
            self.input_handler.on_key_press(key)
            
        # 音乐控制
        if key == arcade.key.M:
            audio_manager.toggle_music()
        elif key == arcade.key.N:
            audio_manager.toggle_effects()
            
        # 重置游戏
        elif key == arcade.key.R:
            self._restart_game()
        
        # 切换路径可视化
        elif key == arcade.key.P:
            self.toggle_pathfinding_visualization()

        # 新增：切换 AI 控制
        elif key == arcade.key.I:
            self.toggle_ai_control()
            
    def on_key_release(self, key: int, modifiers: int) -> None:
        """处理按键释放事件"""
        # 只有当 AI 未激活时，才允许玩家的输入处理器工作
        if self.input_handler and not self.is_showing_path and not self.is_ai_control_active:
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
        """根据游戏模式（手动或自动寻路）更新玩家移动"""
        if not self.player_sprite:
            return

        if self.is_showing_path:
            # 自动寻路模式 (玩家或AI)
            self._update_pathfinding_movement()
        else:
            # 手动控制模式 (玩家)
            if not self.input_handler:
                return
            target_speed_x, target_speed_y = self.input_handler.get_movement_vector()
            self.player_sprite.change_x = target_speed_x
            self.player_sprite.change_y = target_speed_y
        
        # 对两种模式都更新玩家动画纹理
        self.player_sprite.update_player_animation(
            self.player_sprite.change_x, 
            self.player_sprite.change_y
        )
    
    def _update_animations(self) -> None:
        """更新动画效果"""
        # 更新陷阱"呼吸"动画
        breath_scale = cfg.PNG_SCALING + math.sin(self.animation_timer * 4) * (cfg.PNG_SCALING * 0.05)
        trap_list = self.sprite_lists.get("trap")
        
        if trap_list:
            for trap_sprite in trap_list:
                trap_sprite.scale = breath_scale
    
    def _handle_interactions(self) -> None:
        """处理玩家与环境的交互。"""
        if not self.player_logic or not self.player_sprite or not self.game_maze:
            return
        
        # 转换为网格坐标
        grid_x = int(self.player_sprite.center_x // cfg.TILE_SIZE)
        grid_y = int((self.window.height - self.player_sprite.center_y) // cfg.TILE_SIZE)
        
        # 检查坐标有效性
        if not self.game_maze.is_valid_position(grid_x, grid_y):
            return
        
        # 核心交互逻辑已移至Player类，这里只调用并获取结果
        interaction_type = self.player_logic.handle_interaction(grid_x, grid_y)
        
        # 根据交互结果，更新视觉和音效
        if interaction_type:
            self._update_visuals_after_interaction(interaction_type, grid_x, grid_y)

    def _update_visuals_after_interaction(self, interaction_type: str, grid_x: int, grid_y: int) -> None:
        """根据交互结果更新游戏状态（主要是视觉和音效）。"""
        if interaction_type == cfg.RESOURCE_NODE:
            audio_manager.play_sound_effect("get_gold")
            resource_sprite = self._find_sprite_at_position(grid_x, grid_y, "resources")
            if resource_sprite:
                resource_sprite.remove_from_sprite_lists()
 
        elif interaction_type == cfg.TRAP:
            audio_manager.play_sound_effect("step_trap")
            trap_sprite = self._find_sprite_at_position(grid_x, grid_y, "trap")
            if trap_sprite:
                trap_sprite.remove_from_sprite_lists()

        elif interaction_type == cfg.LOCKER:
            locker_sprite = self._find_sprite_at_position(grid_x, grid_y, "locker")
            if not locker_sprite:
                return

            # 检查是否是带锁的谜题宝箱
            if isinstance(locker_sprite, PuzzleChestSprite) and locker_sprite.is_locked:
                print("这是一个带锁的谜题宝箱，切换到解谜场景...")
                puzzle_view = PuzzleView(self, locker_sprite) # 传递游戏视图和宝箱精灵
                self.window.show_view(puzzle_view)
            else:
                # 如果是普通宝箱或已解锁的宝箱
                # 需要确认宝箱类型以安全地调用open
                if isinstance(locker_sprite, ChestSprite) and not locker_sprite.is_open:
                    locker_sprite.open()
                    print("宝箱已打开！")
                    # 假设打开普通宝箱会获得固定资源
                    if self.player_logic:
                        self.player_logic.add_resources(50)
                    # 交互完成后，从地图上移除，防止重复触发
                    if self.game_maze:
                        self.game_maze.clear_tile(grid_x, grid_y)

        elif interaction_type == cfg.BOSS:
            # BOSS战的触发逻辑比较复杂，保留在这里
            boss_sprite = self._find_sprite_at_position(grid_x, grid_y, "boss")
            if boss_sprite and isinstance(boss_sprite, BossSprite):
                self.active_boss_sprite = cast(BossSprite, boss_sprite)
                self.start_battle(self.active_boss_sprite)
                # BOSS交互后，也将其从地图上移除，防止重复触发
                if self.game_maze:
                   self.game_maze.clear_tile(grid_x, grid_y)

        elif interaction_type == cfg.EXIT:
            self.is_game_finished = True
            if self.player_sprite:
                self.player_sprite.change_x = 0
                self.player_sprite.change_y = 0
            
            exit_sprite = self._find_sprite_at_position(grid_x, grid_y, "exit")
            if exit_sprite:
                typed_exit = cast(ExitSprite, exit_sprite)
                if not typed_exit.is_open:
                    typed_exit.open()
                    audio_manager.play_sound_effect("exit")
    
    def _find_sprite_at_position(self, grid_x: int, grid_y: int, sprite_list_name: str) -> Optional[arcade.Sprite]:
        """在指定的精灵列表中，根据网格坐标查找精灵。"""
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
        
        if self.active_boss_sprite and self.player_logic:
            # 设置战斗并记录回合数，但不在此处扣除资源
            self.last_battle_rounds = self.battle_manager.setup_battle(self.active_boss_sprite)
            print(f"任务 5: BOSS战开始，AI测算最少回合数为 {self.last_battle_rounds}。")

    def end_battle(self):
        """结束战斗模式"""
        print("战斗结束。")
        
        # 任务5：在战斗结束后，根据回合数扣除资源
        if self.player_logic:
            print(f"任务 5: 根据回合数 {self.last_battle_rounds} 扣除资源。")
            self.player_logic.deduct_resources(self.last_battle_rounds)

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
        if self.player_logic and self.player_logic.resources < 0:
            print("资源耗尽! 按 R 重新开始。")
            # 这里可以显示一个游戏结束视图
    
    def _restart_game(self) -> None:
        """重新开始游戏"""
        print("重新开始游戏...")
        # 确保切换回背景音乐
        audio_manager.play_background_music("background")
        self.setup()

    def toggle_pathfinding_visualization(self):
        """切换玩家路径可视化和自动移动"""
        if self.is_showing_path:
            # 关闭路径显示
            self.is_showing_path = False
            if self.path_sprites:
                self.path_sprites.clear()
            self.optimal_path = []
            if self.player_sprite:
                self.player_sprite.change_x = 0
                self.player_sprite.change_y = 0
        elif not self.is_calculating_path:
            # 在后台线程中开始路径计算
            if self.game_maze:
                print("在后台线程中计算最优路径...")
                self.is_calculating_path = True
                self.path_calculation_result = None
                
                # 为线程创建一个网格副本，以确保线程安全
                grid_copy = [row[:] for row in self.game_maze.grid]
                
                thread = threading.Thread(
                    target=self._calculate_path_thread,
                    args=(grid_copy,),
                    daemon=True
                )
                thread.start()

    def _calculate_path_thread(self, grid):
        """在工作线程中运行的函数，用于计算路径"""
        score, path, steps = find_maze_path(grid)
        self.path_calculation_result = (score, path, steps)

    def _on_path_found(self, result: tuple):
        """当路径计算完成时在主线程中调用的回调函数"""
        self.is_calculating_path = False
        score, path, steps = result
        
        if path:
            print(f"路径已找到！得分: {score}, 步数: {steps}")
            self.optimal_path = path
            self.is_showing_path = True
            # 从路径的第二个点开始，因为第一个点是玩家当前位置
            self.path_target_index = 1 
            self._create_path_sprites()
        else:
            print("未找到路径。")

    def _create_path_sprites(self):
        """创建用于可视化路径的精灵"""
        if not self.path_sprites or not self.optimal_path:
            return
        
        self.path_sprites.clear()
        
        # 为路径上的每个点创建一个更显眼的标记
        for r, c in self.optimal_path:
            pos_x, pos_y = self._grid_to_pixel_position(c, r)
            marker = arcade.SpriteCircle(
                radius=cfg.TILE_SIZE // 3,       # 增大半径
                color=(64, 224, 208, 120) # 半透明青绿色
            )
            marker.position = (pos_x, pos_y)
            self.path_sprites.append(marker)

    def _update_pathfinding_movement(self):
        """在自动寻路模式下更新玩家速度向量"""
        if not self.player_sprite or not self.optimal_path:
            self.is_showing_path = False
            return

        # 检查是否已到达路径终点
        if self.path_target_index >= len(self.optimal_path):
            self.is_showing_path = False
            if self.player_sprite:
                self.player_sprite.change_x = 0
                self.player_sprite.change_y = 0
            if self.path_sprites: # 路径走完后清除标记
                self.path_sprites.clear()
            return

        # 获取下一个目标点
        target_r, target_c = self.optimal_path[self.path_target_index]
        target_x, target_y = self._grid_to_pixel_position(target_c, target_r)

        # 计算到目标点的向量和距离
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx**2 + dy**2)

        # 如果接近目标点，则移动到下一个目标点
        if distance < cfg.PLAYER_SPEED * 1.5: # 使用1.5倍速度作为缓冲
            self.player_sprite.position = (target_x, target_y)
            
            # 更新玩家的逻辑位置，使其与精灵位置同步
            if self.player_logic:
                self.player_logic.grid_x = target_c
                self.player_logic.grid_y = target_r

            # 移除已经过的路径点的标记
            if self.path_sprites and len(self.path_sprites) > 0:
                self.path_sprites[0].remove_from_sprite_lists()

            self.path_target_index += 1
        else:
            # 朝目标点移动
            self.player_sprite.change_x = (dx / distance) * cfg.PLAYER_SPEED
            self.player_sprite.change_y = (dy / distance) * cfg.PLAYER_SPEED

    def toggle_ai_control(self):
        """切换 AI 是否接管玩家控制"""
        self.is_ai_control_active = not self.is_ai_control_active
        
        # 停止玩家的所有当前活动
        self.is_showing_path = False
        self.optimal_path = []
        if self.path_sprites:
            self.path_sprites.clear()
        if self.player_sprite:
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
            
        status = "激活" if self.is_ai_control_active else "禁用"
        print(f"AI 控制已{status}")


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
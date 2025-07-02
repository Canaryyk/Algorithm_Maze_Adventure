import arcade
import arcade.gui
import arcade.color
from typing import Optional, List, Dict, Any

from game_logic.interactive_objects import BossSprite
from algorithms.boss_battle_solver import optimize_boss_fight
import config as cfg


class BattleManager:
    """
    负责管理右侧战斗面板的UI、状态和动画。
    """
    def __init__(self, gui_camera: arcade.Camera, window: arcade.Window):
        self.camera = gui_camera
        self.window = window
        self.ui_manager = arcade.gui.UIManager(window)
        
        # --- 战斗状态 ---
        self.active_boss_data: Optional[BossSprite] = None
        self.battle_log: List[str] = []
        self.skill_sequence: List[int] = []
        self.skill_map: Dict[int, str] = {}
        self.current_turn = 0
        self.turn_timer = 0.0
        self.turn_duration = 2.0  # 每回合持续2秒（加速1.5倍）

        # --- 精灵和动画 ---
        self.player_sprite: Optional[arcade.Sprite] = None
        self.boss_sprite: Optional[arcade.Sprite] = None
        self.character_sprites = arcade.SpriteList()
        self.player_hp = cfg.PLAYER_MAX_HEALTH
        self.boss_hps: List[int] = []
        self.current_boss_idx = 0
        self.projectiles = arcade.SpriteList()

    def setup_battle(self, boss_data: BossSprite):
        """
        准备战斗UI和数据。
        """
        print("BattleManager: Setting up battle...")
        self._reset_state()
        self.active_boss_data = boss_data

        # --- 准备战斗数据 ---
        if not self.active_boss_data:
            self.battle_log.append("错误：无效的Boss对象。")
            return

        # 确保active_boss_data不为None后才访问其属性
        assert self.active_boss_data is not None
        self.boss_hps = list(self.active_boss_data.boss_hps)
        skills = self.active_boss_data.player_skills
        self.skill_map = {i: f"技能{i+1} (D:{s[0]},C:{s[1]})" for i, s in enumerate(skills)}
        self.skill_map[-1] = "等待"

        # --- 创建精灵 ---
        self._create_sprites()
        
        # --- 调用算法 ---
        input_data = {"B": self.boss_hps, "PlayerSkills": skills}
        sequence, error = optimize_boss_fight(input_data)
        
        if error:
            self.battle_log.append(f"错误: {error}")
            return
            
        self.skill_sequence = sequence
        self.battle_log.append("战斗开始！")

    def _create_sprites(self):
        """创建战斗中的玩家和Boss精灵"""
        panel_width = self.window.width // 3
        panel_x_center = self.window.width - panel_width / 2

        # 创建玩家精灵
        self.player_sprite = arcade.Sprite(str(cfg.PLAYER_ANIM_PATHS["down"]), scale=cfg.GIF_SCALING)
        self.player_sprite.center_x = panel_x_center
        self.player_sprite.center_y = self.window.height * 0.5
        self.character_sprites.append(self.player_sprite)
        
        # 创建Boss精灵
        self.boss_sprite = arcade.Sprite(str(cfg.BOSS_PATH), scale=cfg.GIF_SCALING)
        self.boss_sprite.center_x = panel_x_center
        self.boss_sprite.center_y = self.window.height * 0.8
        self.character_sprites.append(self.boss_sprite)

    def on_draw(self):
        """
        绘制战斗面板的所有UI元素。
        """
        self.ui_manager.draw()
        panel_width = self.window.width // 3
        panel_x_start = self.window.width - panel_width

        # --- 绘制角色和HP ---
        self.character_sprites.draw()
        
        if self.player_sprite:
            arcade.draw_text(f"玩家 HP: {self.player_hp}", 
                             self.player_sprite.center_x, 
                             self.player_sprite.center_y - 60, 
                             arcade.color.WHITE, 12, anchor_x="center")

        if self.boss_sprite:
            if self.current_boss_idx < len(self.boss_hps):
                arcade.draw_text(f"Boss {self.current_boss_idx + 1} HP: {self.boss_hps[self.current_boss_idx]}", 
                                 self.boss_sprite.center_x, 
                                 self.boss_sprite.center_y - 60, 
                                 arcade.color.WHITE, 12, anchor_x="center")
            else:
                 arcade.draw_text("所有Boss已被击败", 
                                  self.boss_sprite.center_x, 
                                  self.boss_sprite.center_y, 
                                  arcade.color.GREEN, 16, anchor_x="center")
        
        # --- 绘制动画 ---
        self.projectiles.draw()

        # --- 绘制战斗日志 ---
        log_start_y = self.window.height * 0.3
        for i, text in enumerate(self.battle_log[-7:]): # 最多显示最近7条
            arcade.draw_text(text, panel_x_start + 20, log_start_y - i * 20, arcade.color.WHITE, 12)

    def on_update(self, delta_time: float):
        """
        更新战斗动画和逻辑。
        """
        self.turn_timer += delta_time
        self.projectiles.update()
        self.character_sprites.update_animation(delta_time)

        # 检查飞行物是否击中Boss
        if self.boss_sprite:
            hit_list = arcade.check_for_collision_with_list(self.boss_sprite, self.projectiles)
            for projectile in hit_list:
                projectile.remove_from_sprite_lists()
                # 在这里可以添加击中特效，比如一个小的爆炸动画

        if self.turn_timer > self.turn_duration and self.current_turn < len(self.skill_sequence):
            self.turn_timer = 0.0
            self._execute_turn()

    def _execute_turn(self):
        """执行当前回合的逻辑。"""
        skill_id = self.skill_sequence[self.current_turn]
        skill_name = self.skill_map.get(skill_id, "未知技能")
        log_entry = f"回合 {self.current_turn + 1}: 使用 {skill_name}"
        self.battle_log.append(log_entry)
        print(log_entry)

        if skill_id != -1 and self.current_boss_idx < len(self.boss_hps) and self.active_boss_data:
            # 执行攻击
            skill_damage = self.active_boss_data.player_skills[skill_id][0]
            self.boss_hps[self.current_boss_idx] -= skill_damage

            # 创建攻击动画
            self._create_projectile_animation()

            # 检查Boss是否被击败
            if self.boss_hps[self.current_boss_idx] <= 0:
                self.boss_hps[self.current_boss_idx] = 0
                self.current_boss_idx += 1
                self.battle_log.append(f"Boss {self.current_boss_idx} 被击败!")
                # 在这里可以添加切换下一个Boss精灵的逻辑
        
        self.current_turn += 1

        if self.current_turn >= len(self.skill_sequence):
            self.battle_log.append("战斗结束！按 ESC 返回。")

    def _create_projectile_animation(self):
        """创建一个从玩家飞向Boss的飞行物。"""
        if not self.player_sprite or not self.boss_sprite:
            return

        # 暂时使用axe.png, 如果不存在会报错，请确保文件存在
        try:
            projectile = arcade.Sprite(str(cfg.ASSET_PATH / "axe.png"), 0.5)
        except FileNotFoundError:
            print("警告: 'axe.png' 未找到，使用默认圆形代替。")
            projectile = arcade.SpriteCircle(10, arcade.color.LIGHT_YELLOW)

        projectile.position = self.player_sprite.position
        
        # 计算飞向Boss的方向和速度
        dest_y = self.boss_sprite.center_y
        delta_y = dest_y - self.player_sprite.center_y
        
        # 将速度设置为一个固定的、较慢的值（加速1.5倍）
        projectile.change_y = delta_y / 20  # 60帧, 即大约1.0秒飞到
        self.projectiles.append(projectile)

    def _reset_state(self):
        """重置所有战斗相关的状态。"""
        self.ui_manager.clear()
        self.active_boss_data = None
        self.battle_log.clear()
        self.skill_sequence.clear()
        self.skill_map.clear()
        self.current_turn = 0
        self.turn_timer = 0.0
        self.boss_hps.clear()
        self.current_boss_idx = 0
        self.projectiles.clear()
        self.character_sprites.clear()
        self.player_sprite = None
        self.boss_sprite = None

    def clear(self):
        """清理战斗管理器状态（供外部调用）"""
        self._reset_state() 
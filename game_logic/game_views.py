import arcade
import sys
import os
import json
import tempfile
import subprocess
from typing import Optional, TYPE_CHECKING
import arcade.color
import arcade.key


# 确保能从根目录导入
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if TYPE_CHECKING:
    from main_arcade import MazeGame

from game_logic.interactive_objects import BossSprite, PuzzleChestSprite
from algorithms.puzzle_solver import solve_from_data
import config as cfg


class PuzzleView(arcade.View):
    """
    处理解谜的视图。
    先播放视频，再显示谜题线索、解谜结果和资源惩罚。
    """
    def __init__(self, game_view: "MazeGame", puzzle_chest: PuzzleChestSprite):
        super().__init__()
        self.game_view = game_view
        self.puzzle_chest = puzzle_chest
        
        # --- 视频播放器 ---
        self.video_player: Optional[VideoPlayer] = None
        self.is_video_done = False
        try:
            self.video_player = VideoPlayer()
            self.video_player.load(str(cfg.PUZZLE_VIDEO_PATH))
        except Exception as e:
            print(f"错误：无法加载视频 {cfg.PUZZLE_VIDEO_PATH}: {e}")
            self.is_video_done = True # 如果视频加载失败，直接跳过

        # --- AI自动解谜 ---
        self.password = None
        self.attempts = 0
        self.solve_puzzle()

    def solve_puzzle(self):
        """调用解谜算法，处理结果"""
        print("开始自动解谜...")
        puzzle_data = {
            "C": self.puzzle_chest.puzzle_constraints,
            "L": self.puzzle_chest.puzzle_hash
        }
        
        result, attempts, method = solve_from_data(puzzle_data)
        
        self.attempts = attempts
        resource_penalty = max(0, self.attempts - 1)

        if result:
            self.password = "".join(map(str, result))
            print(f"解谜成功! 密码: {self.password}, 尝试次数: {self.attempts}, 资源惩罚: {resource_penalty}")
            if self.game_view.player_logic:
                self.game_view.player_logic.deduct_resources(resource_penalty)
            self.puzzle_chest.unlock()
        else:
            print(f"解谜失败。尝试次数: {self.attempts}, 资源惩罚: {resource_penalty}")
            if self.game_view.player_logic:
                self.game_view.player_logic.deduct_resources(resource_penalty)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        if self.video_player:
            self.video_player.play()

    def on_hide_view(self):
        if self.video_player:
            self.video_player.pause()

    def on_update(self, delta_time: float):
        if self.video_player and self.video_player.source and not self.video_player.playing:
            self.is_video_done = True
            
    def on_draw(self):
        self.clear()
        
        if not self.is_video_done and self.video_player:
            video_texture = self.video_player.texture
            if video_texture:
                arcade.draw_texture_rectangle(
                    center_x=self.window.width / 2,
                    center_y=self.window.height / 2,
                    width=self.window.width,
                    height=self.window.height,
                    texture=video_texture,
                )
            return

        arcade.draw_text("任务 4: 解锁密码", 
                         self.window.width / 2, 
                         self.window.height * 0.9, 
                         arcade.color.WHITE, 
                         font_size=40,
                         font_name="SimHei",
                         anchor_x="center")
        
        arcade.draw_text(f"线索 (C): {self.puzzle_chest.puzzle_constraints}",
                         self.window.width / 2,
                         self.window.height * 0.75,
                         arcade.color.WHITE,
                         font_size=18,
                         anchor_x="center")

        if self.password:
            resource_penalty = max(0, self.attempts - 1)
            arcade.draw_text(f"AI 已解出密码: {self.password}", 
                             self.window.width / 2, 
                             self.window.height * 0.55, 
                             arcade.color.LIGHT_GREEN, 
                             font_size=30,
                             font_name="SimHei",
                             anchor_x="center")
            arcade.draw_text(f"尝试次数: {self.attempts}",
                             self.window.width / 2,
                             self.window.height * 0.45,
                             arcade.color.WHITE,
                             font_size=20,
                             anchor_x="center")
            arcade.draw_text(f"资源扣除: -{resource_penalty}",
                             self.window.width / 2,
                             self.window.height * 0.4,
                             cfg.RED,
                             font_size=20,
                             anchor_x="center")
        else:
            arcade.draw_text("AI 解谜失败!", 
                             self.window.width / 2, 
                             self.window.height * 0.55, 
                             arcade.color.RED_DEVIL, 
                             font_size=30, 
                             anchor_x="center")

        arcade.draw_text("按 Esc 返回迷宫", 
                         self.window.width / 2, 
                         self.window.height * 0.1, 
                         arcade.color.WHITE, 
                         font_size=20, 
                         anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.game_view) 
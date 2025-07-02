import arcade
import sys
import os
import json
import tempfile
import subprocess
from typing import Optional
from game_logic.interactive_objects import BossSprite, PuzzleChestSprite
import config as cfg

class PuzzleView(arcade.View):
    """
    处理解谜的视图。
    将显示谜题线索和输入框。
    """
    def __init__(self, game_view: arcade.View, puzzle_chest: PuzzleChestSprite):
        super().__init__()
        self.game_view = game_view
        self.puzzle_chest = puzzle_chest

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE)

    def on_draw(self):
        self.clear()
        arcade.draw_text("解谜场景", 
                         self.window.width / 2, 
                         self.window.height / 2, 
                         arcade.color.WHITE, 
                         font_size=30, 
                         anchor_x="center")

        arcade.draw_text(f"线索: {self.puzzle_chest.puzzle_constraints}", 
                         self.window.width / 2, 
                         self.window.height / 2 - 50, 
                         arcade.color.YELLOW, 
                         font_size=20, 
                         anchor_x="center")
        
        arcade.draw_text("按 Esc 返回", 
                         self.window.width / 2, 
                         self.window.height / 2 - 100, 
                         arcade.color.WHITE, 
                         font_size=20, 
                         anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            # 暂时直接解锁并返回
            self.puzzle_chest.unlock()
            self.window.show_view(self.game_view) 
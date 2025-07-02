"""
输入处理器 - 核心移动控制
"""

from arcade.key import UP, DOWN, LEFT, RIGHT, W, A, S, D
from typing import Tuple
import config as cfg


class InputHandler:
    """输入处理管理器，处理玩家移动输入"""
    
    def __init__(self):
        # 按键映射到移动方向
        self.key_mappings = {
            UP: (0, 1), W: (0, 1),      # 上
            DOWN: (0, -1), S: (0, -1),  # 下
            LEFT: (-1, 0), A: (-1, 0),  # 左
            RIGHT: (1, 0), D: (1, 0),   # 右
        }
        
        # 当前按下的键
        self.pressed_keys = set()
    
    def on_key_press(self, key: int) -> None:
        """处理按键按下"""
        if key in self.key_mappings:
            self.pressed_keys.add(key)
    
    def on_key_release(self, key: int) -> None:
        """处理按键释放"""
        if key in self.key_mappings:
            self.pressed_keys.discard(key)
    
    def get_movement_vector(self) -> Tuple[int, int]:
        """获取当前移动向量"""
        speed_x = 0
        speed_y = 0
        
        # 计算移动方向
        for key in self.pressed_keys:
            if key in self.key_mappings:
                dx, dy = self.key_mappings[key]
                speed_x += dx
                speed_y += dy
        
        # 应用移动速度
        return (speed_x * cfg.PLAYER_SPEED, speed_y * cfg.PLAYER_SPEED) 
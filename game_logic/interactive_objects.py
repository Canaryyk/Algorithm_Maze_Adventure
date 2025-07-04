# game_logic/interactive_objects.py
import arcade
import json
import config as cfg
from .audio_manager import audio_manager

class ChestSprite(arcade.Sprite):
    """
    宝箱精灵，负责管理自己的状态和外观（关闭、打开、动画）
    """
    def __init__(self, scale: float = 1.0, **kwargs):
        self.is_open = False
        
        # 加载静态纹理
        self.closed_texture = arcade.load_texture(str(cfg.CHEST_CLOSED_PATH))
        self.open_texture = arcade.load_texture(str(cfg.CHEST_OPEN_PATH))
        
        # 初始化为关闭状态
        super().__init__(texture=self.closed_texture, scale=scale, **kwargs)
    
    def open(self):
        """打开宝箱，切换到打开纹理"""
        if not self.is_open:
            self.is_open = True
            self.texture = self.open_texture
            self.scale = cfg.PNG_SCALING

class PuzzleChestSprite(ChestSprite):
    """
    带谜题的宝箱。需要解谜才能打开。
    """
    def __init__(self, scale: float = 1.0, **kwargs):
        super().__init__(scale=scale, **kwargs)
        self.is_locked = True
        # 从test.json文件加载谜题数据
        self.puzzle_constraints, self.puzzle_hash = self._load_puzzle_data()

    def _load_puzzle_data(self):
        """从test.json文件加载谜题的约束和哈希值"""
        try:
            with open(cfg.PROJECT_ROOT / "test.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 从 'C' 和 'L' 键加载数据
            constraints = data.get("C", [])
            target_hash = data.get("L", "")
            
            print(f"从test.json加载谜题数据:")
            print(f"  约束 (C): {constraints}")
            print(f"  哈希 (L): {target_hash}")
            
            return constraints, target_hash
            
        except FileNotFoundError:
            print("警告: test.json文件未找到，使用默认谜题数据")
            return [[-1, -1], [1, 0]], "c1606491763321ac3149620026e9532c524354247883204950529454845b42d7"
        except json.JSONDecodeError:
            print("警告: test.json文件格式错误，使用默认谜题数据")
            return [[-1, -1], [1, 0]], "c1606491763321ac3149620026e9532c524354247883204950529454845b42d7"
        except Exception as e:
            print(f"警告: 加载test.json时发生错误: {e}，使用默认谜题数据")
            return [[-1, -1], [1, 0]], "c1606491763321ac3149620026e9532c524354247883204950529454845b42d7"

    def unlock(self):
        """解锁宝箱"""
        if self.is_locked:
            self.is_locked = False
            print("宝箱已解锁！")
            audio_manager.play_sound_effect("unlock_locker")  # 在这里播放音效
            self.open()

class BossSprite(arcade.Sprite):
    """
    Boss精灵，保存战斗需要的数据。
    """
    def __init__(self, scale: float = 1.0, **kwargs):
        # 使用cfg中已有的BOSS路径
        texture = str(cfg.BOSS_PATH)
        super().__init__(texture, scale=scale, **kwargs)
        
        # 从test.json文件加载Boss战斗数据
        self.boss_hps, self.player_skills = self._load_battle_data()
    
    def _load_battle_data(self):
        """从test.json文件加载BOSS HP和玩家技能数据"""
        try:
            with open(cfg.PROJECT_ROOT / "test.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            boss_hps = data.get("B", [150, 200])  # 默认值作为后备
            player_skills = data.get("PlayerSkills", [[20, 2], [50, 5], [10, 0]])  # 默认值作为后备
            
            print(f"从test.json加载BOSS数据:")
            print(f"  BOSS HP: {boss_hps}")
            print(f"  玩家技能: {player_skills}")
            
            return boss_hps, player_skills
            
        except FileNotFoundError:
            print("警告: test.json文件未找到，使用默认BOSS数据")
            return [150, 200], [[20, 2], [50, 5], [10, 0]]
        except json.JSONDecodeError:
            print("警告: test.json文件格式错误，使用默认BOSS数据")
            return [150, 200], [[20, 2], [50, 5], [10, 0]]
        except Exception as e:
            print(f"警告: 加载test.json时发生错误: {e}，使用默认BOSS数据")
            return [150, 200], [[20, 2], [50, 5], [10, 0]]

class ExitSprite(arcade.Sprite):
    """
    出口精灵，负责管理自己的状态和外观（关闭、打开、动画）
    """
    def __init__(self, scale: float = 1.0, **kwargs):
        self.is_open = False
        
        # 加载静态纹理
        self.closed_texture = arcade.load_texture(str(cfg.EXIT_CLOSED_PATH))
        self.open_texture = arcade.load_texture(str(cfg.EXIT_OPEN_PATH))
        
        # 初始化为关闭状态
        super().__init__(texture=self.closed_texture, scale=scale, **kwargs)

    def open(self):
        """打开出口，切换到打开纹理"""
        if not self.is_open:
            self.is_open = True
            self.texture = self.open_texture
            self.scale = cfg.PNG_SCALING
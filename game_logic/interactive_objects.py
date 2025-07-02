# game_logic/interactive_objects.py
import arcade
import config as cfg

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
        # 示例谜题数据 (之后可以从关卡文件加载)
        self.puzzle_constraints = [[-1, -1], [1, 0]] 
        self.puzzle_hash = "c1606491763321ac3149620026e9532c524354247883204950529454845b42d7" # 密码是 720

    def unlock(self):
        """解锁宝箱"""
        self.is_locked = False
        print("宝箱已解锁！")
        self.open()

class BossSprite(arcade.Sprite):
    """
    Boss精灵，保存战斗需要的数据。
    """
    def __init__(self, scale: float = 1.0, **kwargs):
        # 使用cfg中已有的BOSS路径
        texture = str(cfg.BOSS_PATH)
        super().__init__(texture, scale=scale, **kwargs)
        
        # 示例Boss战斗数据 (之后可以从关卡文件加载)
        self.boss_hps = [150, 200]
        self.player_skills = [[20, 2], [50, 5], [10, 0]]

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
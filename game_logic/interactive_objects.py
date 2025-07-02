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
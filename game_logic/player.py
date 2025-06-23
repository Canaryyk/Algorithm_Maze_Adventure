 # player.py

import pygame
import config as cfg
from game_logic.maze import Maze

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, maze):
        """
        初始化玩家对象
        :param x: 初始x像素坐标 (中心点)
        :param y: 初始y像素坐标 (中心点)
        :param maze: 传入Maze对象，用于碰撞检测
        """
        super().__init__()
        self.maze = maze # 保存对迷宫对象的引用
        
        # 创建玩家的图像 (一个简单的矩形)
        self.image = pygame.Surface([cfg.TILE_SIZE // 2, cfg.TILE_SIZE // 2])
        self.image.fill(cfg.PLAYER_COLOR)
        self.rect = self.image.get_rect()
        
        # 玩家的位置使用浮点数，可以实现更平滑的移动
        self.x = float(x)
        self.y = float(y)
        # rect.center 需要整数，不能直接用float
        self.rect.center = (round(self.x), round(self.y))
        
        # 移动向量
        self.vx = 0
        self.vy = 0

    def get_input(self):
        """处理键盘输入，改变玩家的移动向量"""
        self.vx, self.vy = 0, 0
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -cfg.PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = cfg.PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vy = -cfg.PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vy = cfg.PLAYER_SPEED
            
        # 防止斜向移动速度过快 (可选，但推荐)
        if self.vx != 0 and self.vy != 0:
            self.vx /= 1.414 # 根号2
            self.vy /= 1.414

    def update(self):
        """
        每帧更新玩家状态，包括移动和碰撞检测
        """
        self.get_input()
        
        # 移动前先记录当前位置
        last_rect = self.rect.copy()

        # 分别处理x和y方向的移动和碰撞
        # 这样可以实现在撞墙时，角色可以沿着墙壁滑动，而不是完全卡住
        
        # X方向移动
        self.x += self.vx
        self.rect.centerx = round(self.x)
        if self.check_collision('x'):
            self.rect.centerx = last_rect.centerx # 如果碰撞，则撤销移动
            self.x = self.rect.centerx

        # Y方向移动
        self.y += self.vy
        self.rect.centery = round(self.y)
        if self.check_collision('y'):
            self.rect.centery = last_rect.centery # 如果碰撞，则撤销移动
            self.y = self.rect.centery

    def check_collision(self, direction):
        """
        检查玩家是否与墙壁发生碰撞
        :param direction: 'x' 或 'y'，用于分别检测
        :return: 如果碰撞，返回True
        """
        # 使用玩家矩形的四个角点进行检测
        corners_to_check = [
            self.rect.topleft, self.rect.topright,
            self.rect.bottomleft, self.rect.bottomright
        ]
        
        for corner in corners_to_check:
            if self.maze.is_wall(corner[0], corner[1]):
                return True
                
        return False

    def draw(self, surface):
        """
        在给定的surface上绘制玩家
        """
        surface.blit(self.image, self.rect)
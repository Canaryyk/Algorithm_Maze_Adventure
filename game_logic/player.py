# player.py

import pygame
import config as cfg
#from maze import Maze

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, maze):
        super().__init__()
        self.maze = maze
        self.image = pygame.Surface([cfg.TILE_SIZE // 2, cfg.TILE_SIZE // 2])
        self.image.fill(cfg.PLAYER_COLOR)
        self.rect = self.image.get_rect()
        
        # 玩家状态属性
        self.health = cfg.PLAYER_MAX_HEALTH
        self.gold = 0
        
        self.x = float(x)
        self.y = float(y)
        # rect.center 需要整数坐标，进行类型转换
        self.rect.center = (int(self.x), int(self.y))
        self.vx = 0
        self.vy = 0

    def get_input(self):
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
        if self.vx != 0 and self.vy != 0:
            self.vx /= 1.414
            self.vy /= 1.414

    def update(self):
        """每帧更新玩家状态"""
        self.get_input()
        
        # 移动和碰撞检测
        self.move()
        
        # 处理与脚下格子的交互
        self.handle_interaction()

    def move(self):
        """处理移动和墙壁碰撞"""
        last_rect = self.rect.copy()
        
        # X方向
        self.x += self.vx
        self.rect.centerx = round(self.x)
        if self.check_collision():
            self.x = last_rect.centerx
            self.rect.centerx = last_rect.centerx

        # Y方向
        self.y += self.vy
        self.rect.centery = round(self.y)
        if self.check_collision():
            self.y = last_rect.centery
            self.rect.centery = last_rect.centery
            
    def check_collision(self):
        """检查玩家是否与墙壁碰撞"""
        return self.maze.is_wall(self.rect.centerx, self.rect.centery)

    def handle_interaction(self):
        """处理玩家与脚下格子的交互事件"""
        grid_x = int(self.rect.centerx // cfg.TILE_SIZE)
        grid_y = int(self.rect.centery // cfg.TILE_SIZE)
        
        tile_type = self.maze.get_tile_type(grid_x, grid_y)

        if tile_type == cfg.GOLD:
            self.gold += cfg.GOLD_VALUE
            print(f"捡到金币! 当前金币: {self.gold}")
            self.maze.set_tile_type(grid_x, grid_y, cfg.PATH) # 将金币格子变回通路
        
        elif tile_type == cfg.TRAP:
            self.health -= cfg.TRAP_DAMAGE
            print(f"踩到陷阱! 生命值: {self.health}")
            self.maze.set_tile_type(grid_x, grid_y, cfg.PATH) # 陷阱触发后消失
        
        elif tile_type == cfg.LOCKER:
            # 这里是为成员C预留的接口
            print("遇到一个机关! (解谜逻辑待实现)")
            # 成员C的解谜模块被调用后，如果成功，可以把这个格子变成PATH
            # self.maze.set_tile_type(grid_x, grid_y, cfg.PATH)

        elif tile_type == cfg.BOSS:
            # 这里是为成员C预留的接口
            print("遭遇BOSS! (战斗逻辑待实现)")

        elif tile_type == cfg.EXIT:
            # 游戏结束逻辑
            print("恭喜你，到达终点!")
            # 可以在这里触发游戏结束状态

    def draw(self, surface):
        surface.blit(self.image, self.rect)
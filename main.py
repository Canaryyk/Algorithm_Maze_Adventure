# main.py (示例)
import pygame
import config as cfg
from game_logic.maze import Maze
from game_logic.player import Player

def draw_hud(surface, player):
    """在屏幕上绘制HUD信息"""
    # 绘制HUD背景
    hud_rect = pygame.Rect(0, cfg.SCREEN_HEIGHT - cfg.HUD_HEIGHT, cfg.SCREEN_WIDTH, cfg.HUD_HEIGHT)
    pygame.draw.rect(surface, cfg.HUD_BG_COLOR, hud_rect)
    
    # 设置字体
    font = pygame.font.Font(None, cfg.HUD_FONT_SIZE)
    
    # 显示生命值
    health_text = font.render(f"Health: {player.health}", True, cfg.WHITE)
    surface.blit(health_text, (20, cfg.SCREEN_HEIGHT - cfg.HUD_HEIGHT + 15))
    
    # 显示金币
    gold_text = font.render(f"Gold: {player.gold}", True, cfg.YELLOW)
    surface.blit(gold_text, (200, cfg.SCREEN_HEIGHT - cfg.HUD_HEIGHT + 15))

def main():
    pygame.init()
    screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
    pygame.display.set_caption(cfg.GAME_TITLE)
    clock = pygame.time.Clock()

    game_maze = Maze(15, 11)
    start_pos = game_maze.get_start_pos()
    player = Player(start_pos[0], start_pos[1], game_maze)

    game_over = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        if not game_over:
            # 更新
            player.update()

            # 检查游戏结束条件
            if player.health <= 0:
                print("游戏结束，你被陷阱击败了!")
                game_over = True
            
            grid_x = int(player.rect.centerx // cfg.TILE_SIZE)
            grid_y = int(player.rect.centery // cfg.TILE_SIZE)
            if game_maze.get_tile_type(grid_x, grid_y) == cfg.EXIT:
                game_over = True


        # 绘制
        screen.fill(cfg.BLACK)
        game_maze.draw(screen)
        player.draw(screen)
        draw_hud(screen, player) # 绘制HUD
        
        pygame.display.flip()

        clock.tick(cfg.FPS)

    pygame.quit()

if __name__ == '__main__':
    main()
 # main.py (示例)
import pygame
import config as cfg
from game_logic.maze import Maze
from game_logic.player import Player

def main():
    pygame.init()
    screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
    pygame.display.set_caption(cfg.GAME_TITLE)
    clock = pygame.time.Clock()

    # 1. 创建迷宫
    # 注意，这里的尺寸是临时的，最终应由你的算法生成逻辑决定
    game_maze = Maze(10, 10) 

    # 2. 创建玩家，并将其放置在迷宫的起点
    start_pos = game_maze.get_start_pos()
    player = Player(start_pos[0], start_pos[1], game_maze)

    running = True
    while running:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 更新
        player.update()

        # 绘制
        screen.fill(cfg.BLACK) # 清屏
        game_maze.draw(screen)
        player.draw(screen)
        pygame.display.flip() # 更新显示

        # 控制帧率
        clock.tick(cfg.FPS)

    pygame.quit()

if __name__ == '__main__':
    main()
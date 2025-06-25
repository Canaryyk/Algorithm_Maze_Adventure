# game_logic/ai_agent.py (最终重构版 - 智能返回)

import pygame
import numpy as np
import heapq
import config as cfg


def find_shortest_path(grid_data, start_node, end_node):
    grid = np.array(grid_data)
    rows, cols = grid.shape
    open_set = [(0, start_node)]
    came_from = {}
    g_score = { (r,c): float('inf') for r in range(rows) for c in range(cols) }
    g_score[start_node] = 0
    f_score = { (r,c): float('inf') for r in range(rows) for c in range(cols) }
    f_score[start_node] = _heuristic(start_node, end_node)
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == end_node:
            return _reconstruct_path(came_from, current)
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (current[0] + dr, current[1] + dc)
            if not (0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols): continue
            if grid[neighbor] == cfg.WALL: continue
            tentative_g_score = g_score[current] + 1
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + _heuristic(neighbor, end_node)
                if neighbor not in [i[1] for i in open_set]:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return []

def _heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def _reconstruct_path(came_from, current):
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)
    total_path.reverse()
    return total_path


class AIAgent:
    def __init__(self, x, y, maze):
        self.maze = maze
        self.image = pygame.Surface([cfg.TILE_SIZE // 2, cfg.TILE_SIZE // 2])
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.health = cfg.PLAYER_MAX_HEALTH
        self.gold = 0
        self.path_taken_for_interaction = {self.get_grid_pos()}

        self.state = 'CALCULATING_MAIN_PATH'
        self.main_path = []
        self.main_path_index = 0
        self.side_quest_path = [] # 用于存储所有支线任务的路径

    def get_grid_pos(self):
        return (int(self.rect.centery // cfg.TILE_SIZE), int(self.rect.centerx // cfg.TILE_SIZE))

    def update(self):
        """状态机的驱动器，根据不同状态执行不同逻辑"""
        if self.state == 'CALCULATING_MAIN_PATH':
            self._calculate_main_path()
        elif self.state == 'FOLLOWING_PATH':
            self._execute_follow_path()
        elif self.state == 'DETOURING_FOR_GOLD':
            self._execute_side_quest()
        elif self.state == 'RETURNING_TO_PATH':
            self._execute_side_quest() # 返回也是一种支线任务
        
        self.handle_interaction()

    def _calculate_main_path(self):
        """在游戏开始时计算主路径"""
        print("AI: 正在计算主路径...")
        grid = np.array(self.maze.grid)
        start_node = self.get_grid_pos()
        end_node = tuple(np.argwhere(grid == cfg.EXIT)[0])
        self.main_path = find_shortest_path(self.maze.grid, start_node, end_node)
        if self.main_path:
            self.main_path_index = 0
            self.state = 'FOLLOWING_PATH'
            print("AI: 主路径计算完毕。")
        else:
            self.state = 'IDLE'
            print("AI: 无法计算主路径！")

    def _execute_follow_path(self):
        """状态：沿主路行走，并随时寻找可行的支线任务"""
        gold_pos = self._find_gold_nearby()
        if gold_pos:
            detour_path = find_shortest_path(self.maze.grid, self.get_grid_pos(), gold_pos)
            if detour_path:
                print(f"AI: 发现金币于 {gold_pos}，规划支线...")
                self.state = 'DETOURING_FOR_GOLD'
                self.side_quest_path = detour_path
                self.side_quest_path.pop(0) # 移除路径中的当前位置
                return # 切换状态后，将逻辑交由下一帧的update处理

        # 如果没有支线任务，继续沿主路前进
        if self.main_path and self.main_path_index < len(self.main_path) - 1:
            self.main_path_index += 1
            self._move_along_path(self.main_path, self.main_path_index)
        else:
            self.state = 'FINISHED'
            print("AI: 已到达终点附近，任务完成。")

    def _execute_side_quest(self):
        """(全新) 通用的支线任务执行逻辑"""
        if not self.side_quest_path:
            # 当前支线路径已走完
            if self.state == 'DETOURING_FOR_GOLD':
                print("AI: 金币到手，准备返回主路。")
                self.state = 'RETURNING_TO_PATH'
                self._plan_return_path() # 立即计算返回路径
            elif self.state == 'RETURNING_TO_PATH':
                print("AI: 已返回主路，继续主线任务。")
                self.state = 'FOLLOWING_PATH'
            return

        # 如果支线路径还未走完，继续走
        self._move_along_path(self.side_quest_path)

    def _plan_return_path(self):
        """(全新) 规划返回到最近主路径节点的路线"""
        nearest_node, new_index = self._find_nearest_node_on_main_path()
        if nearest_node is None:
            self.state = 'IDLE'
            print("AI: 警告！找不到可返回的主路径节点！")
            return
            
        print(f"AI: 找到最近主路节点 {nearest_node}，正在规划返回路线...")
        return_path = find_shortest_path(self.maze.grid, self.get_grid_pos(), nearest_node)
        
        if return_path:
            self.side_quest_path = return_path
            self.side_quest_path.pop(0)
            self.main_path_index = new_index # (重要) 更新主路径的进度
            print("AI: 返回路线规划成功。")
        else:
            self.state = 'IDLE'
            print("AI: 警告！无法规划返回路线！")

    def _find_nearest_node_on_main_path(self):
        """(全新) 寻找距离当前位置最近的主路径节点"""
        if not self.main_path: return None, -1
        current_pos = self.get_grid_pos()
        distances = [_heuristic(current_pos, node) for node in self.main_path]
        min_distance_index = np.argmin(distances)
        return self.main_path[min_distance_index], min_distance_index

    def _move_along_path(self, path, index=0):
        """(全新) 智能移动：根据路径列表移动一步"""
        if not path: return
        target_pos = path[index]
        current_pos = self.get_grid_pos()
        dr = target_pos[0] - current_pos[0]
        dc = target_pos[1] - current_pos[1]
        
        self.rect.y += dr * cfg.TILE_SIZE
        self.rect.x += dc * cfg.TILE_SIZE
        
        # 如果是走支线任务，走完一步后就从任务列表中移除
        if path == self.side_quest_path:
            path.pop(0)

    def _find_gold_nearby(self):
        current_row, current_col = self.get_grid_pos()
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                check_row, check_col = current_row + dr, current_col + dc
                if 0 <= check_row < self.maze.height and 0 <= check_col < self.maze.width:
                    if self.maze.get_tile_type(check_col, check_row) == cfg.GOLD:
                        return (check_row, check_col)
        return None

    def handle_interaction(self):
        row, col = self.get_grid_pos()
        if (row, col) in self.path_taken_for_interaction: return
        self.path_taken_for_interaction.add((row, col))
        tile_type = self.maze.get_tile_type(col, row)
        if tile_type == cfg.GOLD:
            self.gold += cfg.GOLD_VALUE
            self.maze.set_tile_type(col, row, cfg.PATH)
        elif tile_type == cfg.TRAP:
            self.health -= cfg.TRAP_DAMAGE
            self.maze.set_tile_type(col, row, cfg.PATH)
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)
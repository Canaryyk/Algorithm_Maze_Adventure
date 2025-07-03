# game_logic/ai_agent.py (最终重构版 - 智能返回)
import numpy as np
import heapq
import config as cfg

def find_shortest_path(grid_data, start_node, end_node):
    """
    【诊断版】A*算法，会打印出详细的执行过程。
    """
    print(f"\n--- A* 寻路算法启动 ---")
    print(f"起点(行,列): {start_node}, 终点(行,列): {end_node}")

    grid = np.array(grid_data)
    rows, cols = grid.shape
    
    open_set = [(0, start_node)]
    came_from = {}
    g_score = { (r,c): float('inf') for r in range(rows) for c in range(cols) }
    g_score[start_node] = 0
    f_score = { (r,c): float('inf') for r in range(rows) for c in range(cols) }
    f_score[start_node] = _heuristic(start_node, end_node)
    
    open_set_hash = {start_node}
    
    step_count = 0
    while open_set:
        step_count += 1
        if step_count > 3000: # 安全阀
            print("!!! A* 错误: 搜索步数超过3000，可能陷入死循环或地图无解。")
            return []

        _, current = heapq.heappop(open_set)
        open_set_hash.remove(current)

        if current == end_node:
            print(f"--- A* 成功: 在 {step_count} 步后找到终点！ ---")
            return _reconstruct_path(came_from, current)

        # print(f"探索中: {current}") # 打开此行可跟踪每一步

        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (current[0] + dr, current[1] + dc)
            
            if not (0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols):
                continue

            # 修正：只要邻居不是墙壁，就认为是可通行的
            if grid[neighbor[0], neighbor[1]] != cfg.WALL:
                tentative_g_score = g_score[current] + 1
            
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + _heuristic(neighbor, end_node)
                    if neighbor not in open_set_hash:
                        # print(f"  -> 发现到 {neighbor} 的更优路径, f_score: {f_score[neighbor]:.2f}")
                        heapq.heappush(open_set, (int(f_score[neighbor]), neighbor))
                        open_set_hash.add(neighbor)
    
    print(f"--- A* 失败: 在 {step_count} 步后仍然没有找到通往 {end_node} 的路径！ ---")
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
    """
    AI 代理逻辑控制器 (无状态决策者)。
    只负责根据当前游戏状态决定下一个最优目标。
    """
    def __init__(self):
        # AI现在是无状态的，不需要构造函数参数
        pass

    def decide_next_target(self, current_pos_grid, grid_data):
        """
        任务3: 贪心算法 - 在3×3视野内选择最优目标。

        贪心策略：
        - 扫描3x3视野范围。
        - 为每个格子根据其内容（资源, 陷阱）赋予一个基础价值。
        - BOSS和宝箱不再具有短期收益值，因为它们在主路径上。
        - 选择价值最高的格子作为短期目标。
        - 如果视野内没有发现任何有正收益的目标，则返回 None。
          此时，主游戏逻辑会引导AI走向最终出口。
        
        评分标准 (基础价值):
        - 资源点: +50 (cfg.RESOURCE_VALUE)
        - 陷阱: -30 (cfg.TRAP_PENALTY)
        """
        grid = np.array(grid_data)
        current_row, current_col = current_pos_grid
        
        best_target = None
        max_score = 0

        # 扫描3×3视野
        for r in range(max(0, current_row - 1), min(grid.shape[0], current_row + 2)):
            for c in range(max(0, current_col - 1), min(grid.shape[1], current_col + 2)):
                if r == current_row and c == current_col:
                    continue  # 不把自己作为目标

                if grid[r, c] == cfg.WALL:
                    continue # 不考虑墙壁

                tile_type = grid[r, c]
                score = 0

                if tile_type == cfg.BOSS:
                    score = 0 # BOSS在必经之路上，不计入短期贪心收益
                elif tile_type == cfg.LOCKER:
                    score = 0 # 宝箱在必经之路上，不计入短期贪心收益
                elif tile_type == cfg.RESOURCE_NODE:
                    score = cfg.RESOURCE_VALUE
                elif tile_type == cfg.TRAP:
                    score = -cfg.TRAP_PENALTY # 陷阱是负收益
                
                if score > max_score:
                    max_score = score
                    best_target = (r, c)
        
        if best_target:
            print(f"AI决策: 在3×3视野内发现最优目标 {best_target} (价值: {max_score})")
            return best_target
        
        # 如果视野内没有正收益目标，则返回None，按主路径前进
        print("AI决策: 3×3视野内无正收益目标，按主路径前进。")
        return None

# 移除所有旧的、复杂的、基于索引的状态管理方法
# _execute_follow_path, _execute_side_quest, _plan_return_path, 
# _find_nearest_node_on_main_path, _find_gold_nearby 均被新的update逻辑取代。
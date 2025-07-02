'''
import heapq
import pygame
import numpy as np
import sys
import time

# --- 算法核心部分 (与之前相同) ---

# 定义迷宫中不同元素的符号及其对应的资源价值
CELL_VALUES = {
    'S': 0, 'E': 0, ' ': 0, 'L': 0, 'B': 0,
    'G': 5, 'T': -3
}
WALL = '#'


class OptimalPathfinderWithRepeats:
    # ... (此处代码与上一版完全相同，为简洁起见，将其折叠)
    # 您可以将上一版中的 OptimalPathfinderWithRepeats 类完整地复制到这里
    """
    大战略家 (V2 - 允许重复路径)

    使用Dijkstra算法的变体（在状态图上进行最佳优先搜索），计算在允许重复走路径，
    但每个资源/陷阱只能收集/触发一次的规则下的最优路径。
    """

    def __init__(self, grid):
        """初始化寻路器"""
        if not grid or not grid[0]:
            raise ValueError("迷宫网格不能为空。")
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])

        # 1. 查找特殊点位并建立物品地图
        self.start_pos = None
        self.end_pos = None
        self.item_locations = []
        self.item_map = {}  # (r, c) -> item_index
        self.item_values = []

        for r in range(self.rows):
            for c in range(self.cols):
                char = self.grid[r][c]
                if char == 'S':
                    self.start_pos = (r, c)
                elif char == 'E':
                    self.end_pos = (r, c)
                elif char in ('G', 'T'):
                    item_index = len(self.item_locations)
                    self.item_locations.append((r, c))
                    self.item_map[(r, c)] = item_index
                    self.item_values.append(CELL_VALUES[char])

        if self.start_pos is None or self.end_pos is None:
            raise ValueError("迷宫必须包含一个起点 'S' 和一个终点 'E'。")

        self.num_items = len(self.item_locations)

    def _reconstruct_path(self, predecessor, best_final_state):
        """根据前驱字典回溯路径"""
        path = []
        curr_state = best_final_state
        while curr_state is not None:
            r, c, mask = curr_state
            # 为了让动画更平滑，如果移动是跳跃的，我们在这里插入中间步骤
            # （在这个四向移动的网格中，这通常不是问题，但这是个好习惯）
            path.append((r, c))
            curr_state = predecessor.get(curr_state)
        path.reverse()
        return path

    def calculate_optimal_path(self):
        """
        主函数：使用基于优先队列的Dijkstra变体计算最优路径和最大分值。
        """
        pq = []
        max_scores = {}
        predecessor = {}

        start_r, start_c = self.start_pos
        initial_mask = 0
        initial_score = 0

        if (start_r, start_c) in self.item_map:
            item_index = self.item_map[(start_r, start_c)]
            initial_mask = 1 << item_index
            initial_score = self.item_values[item_index]

        start_state = (start_r, start_c, initial_mask)
        heapq.heappush(pq, (-initial_score, start_r, start_c, initial_mask))
        max_scores[start_state] = initial_score
        predecessor[start_state] = None

        while pq:
            neg_score, r, c, mask = heapq.heappop(pq)
            score = -neg_score

            if score < max_scores.get((r, c, mask), -float('inf')):
                continue

            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc

                if not (0 <= nr < self.rows and 0 <= nc < self.cols and self.grid[nr][nc] != WALL):
                    continue

                new_score = score
                new_mask = mask

                if (nr, nc) in self.item_map:
                    item_index = self.item_map[(nr, nc)]
                    if not (mask & (1 << item_index)):
                        new_mask = mask | (1 << item_index)
                        new_score = score + self.item_values[item_index]

                new_state = (nr, nc, new_mask)

                if new_score > max_scores.get(new_state, -float('inf')):
                    max_scores[new_state] = new_score
                    predecessor[new_state] = (r, c, mask)
                    heapq.heappush(pq, (-new_score, nr, nc, new_mask))

        best_score = -float('inf')
        best_final_state = None

        for (r, c, mask), score in max_scores.items():
            if (r, c) == self.end_pos and score > best_score:
                best_score = score
                best_final_state = (r, c, mask)

        if best_final_state is None:
            return -1, []

        optimal_path = self._reconstruct_path(predecessor, best_final_state)

        return best_score, optimal_path


# --- Pygame 可视化部分 ---

class MazeVisualizer:
    def __init__(self, grid, cell_size=40):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.cell_size = cell_size
        self.width = self.cols * self.cell_size
        self.height = self.rows * self.cell_size

        # 定义颜色
        self.COLORS = {
            'BG': (20, 20, 40),
            'WALL': (130, 130, 150),
            'PATH': (50, 50, 80),
            'START': (0, 255, 0),
            'END': (255, 0, 0),
            'GOLD': (255, 223, 0),
            'TRAP': (160, 0, 80),
            'AGENT': (50, 150, 255)
        }

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("大战略家 - 最优路径可视化")
        self.font = pygame.font.SysFont('Arial', self.cell_size // 3)

    def _draw_grid(self, collected_items_mask=0, item_map=None):
        """绘制迷宫的静态背景"""
        self.screen.fill(self.COLORS['BG'])
        for r in range(self.rows):
            for c in range(self.cols):
                rect = pygame.Rect(c * self.cell_size, r * self.cell_size, self.cell_size, self.cell_size)
                char = self.grid[r][c]

                # 绘制背景色
                if char == WALL:
                    pygame.draw.rect(self.screen, self.COLORS['WALL'], rect)
                else:
                    pygame.draw.rect(self.screen, self.COLORS['PATH'], rect)

                # 绘制物品和特殊点
                if char == 'S':
                    pygame.draw.circle(self.screen, self.COLORS['START'], rect.center, self.cell_size // 3)
                elif char == 'E':
                    pygame.draw.circle(self.screen, self.COLORS['END'], rect.center, self.cell_size // 3)
                elif char in ('G', 'T'):
                    # 只有未被收集的物品才显示
                    is_collected = False
                    if item_map and (r, c) in item_map:
                        item_index = item_map[(r, c)]
                        if (collected_items_mask >> item_index) & 1:
                            is_collected = True

                    if not is_collected:
                        color = self.COLORS['GOLD'] if char == 'G' else self.COLORS['TRAP']
                        pygame.draw.circle(self.screen, color, rect.center, self.cell_size // 4)

    def _get_path_trace_colors(self, num_steps):
        """生成从冷到暖的颜色渐变列表"""
        start_color = np.array([0, 0, 255])  # Blue
        end_color = np.array([255, 255, 0])  # Yellow
        colors = []
        for i in range(num_steps):
            interp = np.sqrt(i / (num_steps - 1)) if num_steps > 1 else 1.0  # sqrt for non-linear feel
            color = start_color + (end_color - start_color) * interp
            colors.append(tuple(color.astype(int)))
        return colors

    def run_visualization(self, path, item_map):
        """主可视化循环，动画展示路径"""
        if not path:
            print("无路径可供可视化。")
            return

        clock = pygame.time.Clock()
        path_len = len(path)
        trace_colors = self._get_path_trace_colors(path_len)

        animating = True
        current_step = 0

        # 初始收集状态
        collected_mask = 0
        initial_score = 0
        start_pos = path[0]
        if start_pos in item_map:
            item_index = item_map[start_pos]
            collected_mask |= (1 << item_index)
            initial_score += CELL_VALUES[self.grid[start_pos[0]][start_pos[1]]]

        # 动画速度控制
        last_update_time = time.time()
        animation_speed = 0.08  # 秒/步

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            # 更新动画
            if animating and time.time() - last_update_time > animation_speed:
                if current_step < path_len - 1:
                    current_step += 1
                    # 更新收集状态
                    pos = path[current_step]
                    if pos in item_map:
                        item_index = item_map[pos]
                        if not ((collected_mask >> item_index) & 1):
                            collected_mask |= (1 << item_index)
                else:
                    animating = False  # 动画结束
                last_update_time = time.time()

            # --- 绘图 ---
            self._draw_grid(collected_mask, item_map)

            # 绘制路径轨迹
            for i in range(current_step):
                start_pos_px = (path[i][1] * self.cell_size + self.cell_size // 2,
                                path[i][0] * self.cell_size + self.cell_size // 2)
                end_pos_px = (path[i + 1][1] * self.cell_size + self.cell_size // 2,
                              path[i + 1][0] * self.cell_size + self.cell_size // 2)
                pygame.draw.line(self.screen, trace_colors[i], start_pos_px, end_pos_px, 3)

            # 绘制代理（玩家）
            agent_pos = path[current_step]
            agent_rect = pygame.Rect(agent_pos[1] * self.cell_size, agent_pos[0] * self.cell_size, self.cell_size,
                                     self.cell_size)
            pygame.draw.circle(self.screen, self.COLORS['AGENT'], agent_rect.center, self.cell_size // 3)

            # 更新显示
            pygame.display.flip()
            clock.tick(60)  # 限制最高帧率

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    import json
    # 从 JSON 文件中读取迷宫数据
    with open('json/result_maze_15_15_2_formatted.json', 'r', encoding='utf-8') as f:
        maze_data = json.load(f)

    grid = maze_data["maze"]

    print("正在计算最优路径，请稍候...")
    pathfinder = OptimalPathfinderWithRepeats(grid)
    max_score, optimal_path = pathfinder.calculate_optimal_path()

    if optimal_path:
        print(f"计算完成！最大得分: {max_score}, 路径长度: {len(optimal_path)}步。")
        print("启动可视化...")

        # 创建并运行可视化
        visualizer = MazeVisualizer(grid, cell_size=35)
        visualizer.run_visualization(optimal_path, pathfinder.item_map)
    else:
        print("计算失败：无法从起点找到通往终点的路径。")
'''
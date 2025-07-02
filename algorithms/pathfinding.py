import heapq
import json

# --- 算法核心部分 (V3 - 分数优先，步数次之) ---

# 定义迷宫中不同元素的符号及其对应的资源价值
CELL_VALUES = {
    'S': 0, 'E': 0, ' ': 0, 'L': 0, 'B': 0,
    'G': 5, 'T': -3
}
WALL = '#'


class OptimalPathfinderWithRepeats:
    """
    大战略家 (V3 - 分数优先，步数次之)

    使用Dijkstra算法的变体，在允许重复路径的规则下，
    计算最优路径。当存在多条路径得分相同时，选择步数最短的一条。
    """

    def __init__(self, grid):
        if not grid or not grid[0]:
            raise ValueError("迷宫网格不能为空。")
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])

        self.start_pos = None
        self.end_pos = None
        self.item_locations = []
        self.item_map = {}
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
        path = []
        curr_state = best_final_state
        while curr_state is not None:
            r, c, mask = curr_state
            path.append((r, c))
            curr_state = predecessor.get(curr_state)
        path.reverse()
        return path

    def calculate_optimal_path(self):
        """
        主函数：计算最优路径（分数优先，步数次之）。
        """
        # 优先队列: (-score, steps, r, c, mask)
        pq = []
        # 记录到达每个状态 (r, c, mask) 的信息: (score, steps)
        best_records = {}
        # 记录路径回溯的前驱节点
        predecessor = {}

        # 初始化起点状态
        if self.start_pos is None:
            raise ValueError("迷宫中未找到起点 'S'。")
        start_r, start_c = self.start_pos
        initial_mask = 0
        initial_score = 0
        initial_steps = 0

        if (start_r, start_c) in self.item_map:
            item_index = self.item_map[(start_r, start_c)]
            initial_mask = 1 << item_index
            initial_score = self.item_values[item_index]

        start_state = (start_r, start_c, initial_mask)
        heapq.heappush(pq, (-initial_score, initial_steps, start_r, start_c, initial_mask))
        best_records[start_state] = (initial_score, initial_steps)
        predecessor[start_state] = None

        # 主循环
        while pq:
            neg_score, steps, r, c, mask = heapq.heappop(pq)
            score = -neg_score

            # 如果有更优路径到达当前状态，则跳过
            current_best_score, current_best_steps = best_records.get((r, c, mask), (-float('inf'), float('inf')))
            if score < current_best_score or (score == current_best_score and steps > current_best_steps):
                continue

            # 探索邻居
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc

                if not (0 <= nr < self.rows and 0 <= nc < self.cols and self.grid[nr][nc] != WALL):
                    continue

                # 计算新状态
                new_score = score
                new_mask = mask
                new_steps = steps + 1

                if (nr, nc) in self.item_map:
                    item_index = self.item_map[(nr, nc)]
                    if not (mask & (1 << item_index)):
                        new_mask = mask | (1 << item_index)
                        new_score = score + self.item_values[item_index]

                new_state = (nr, nc, new_mask)

                # 如果发现了更优的路径
                new_best_score, new_best_steps = best_records.get(new_state, (-float('inf'), float('inf')))
                if new_score > new_best_score or (new_score == new_best_score and new_steps < new_best_steps):
                    best_records[new_state] = (new_score, new_steps)
                    predecessor[new_state] = (r, c, mask)
                    heapq.heappush(pq, (-new_score, new_steps, nr, nc, new_mask))

        # 查找终点的最优解
        best_score = -float('inf')
        min_steps = float('inf')
        best_final_state = None

        for (r, c, mask), (score, steps) in best_records.items():
            if (r, c) == self.end_pos:
                if score > best_score or (score == best_score and steps < min_steps):
                    best_score = score
                    min_steps = steps
                    best_final_state = (r, c, mask)

        if best_final_state is None:
            return -1, [], -1

        optimal_path = self._reconstruct_path(predecessor, best_final_state)
        return best_score, optimal_path, min_steps


# --- 主程序接口 ---

def find_maze_path(grid):
    """
    接收一个迷宫网格，计算并返回最优路径信息。

    Args:
        grid (list[list[str]]): 表示迷宫的二维列表。

    Returns:
        tuple: 一个包含三个元素的元组 (score, path, steps)。
               - score (int): 获得的最大分数。
               - path (list[tuple]): 最优路径的坐标列表，例如 [(r1, c1), (r2, c2), ...]。
               - steps (int): 走完最优路径所需的步数。
               如果找不到路径，则返回 (-1, [], -1)。
    """
    try:
        pathfinder = OptimalPathfinderWithRepeats(grid)
        max_score, optimal_path, min_steps = pathfinder.calculate_optimal_path()
        return max_score, optimal_path, min_steps
    except ValueError as e:
        print(f"处理迷宫时发生错误: {e}")
        return -1, [], -1


if __name__ == "__main__":
    # --- 输入接口 ---
    # 示例: 从 JSON 文件中读取迷宫数据。
    # 用户可以修改此部分以提供不同的迷宫输入。
    input_grid = None
    try:
        # 尝试从文件加载迷宫
        with open('json/maze_15_15_2.json', 'r', encoding='utf-8') as f:
            maze_data = json.load(f)
        input_grid = maze_data["maze"]
    except FileNotFoundError:
        print("警告: 未找到 'json/maze_15_15_2.json' 文件。将使用一个内置的示例迷宫。")
        # 提供一个备用迷宫，以防文件不存在
        input_grid = [
            ["S", " ", " ", "#", "G"],
            [" ", "#", " ", "#", "T"],
            [" ", "#", " ", " ", " "],
            [" ", " ", "#", "E", " "],
            ["G", " ", " ", " ", "G"]
        ]
    except Exception as e:
        print(f"读取文件时出错: {e}")


    # --- 核心处理 ---
    if input_grid:
        print("迷宫输入:")
        for row in input_grid:
            print("".join(row))
        print("\n正在计算最优路径 (分数优先，步数次之)...")

        # 调用核心功能
        score, path, steps = find_maze_path(input_grid)

        # --- 输出接口 ---
        print("\n--- 计算结果 ---")
        if path:
            print(f"最大得分: {score}")
            print(f"最短步数: {steps}")
            # 路径长度比步数多1，因为包含了起点
            print(f"路径长度: {len(path)}")
            print(f"最优路径坐标: {path}")
        else:
            print("计算失败：无法从起点找到通往终点的路径。")
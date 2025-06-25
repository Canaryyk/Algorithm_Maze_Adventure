from heapq import heappush, heappop
import math
import copy
import itertools

def get_available_skills(state, skills):
    return [s for s in skills if state["skill_cooldowns"].get(s["id"], 0) == 0]

def apply_skill(state, skill, skills):
    new_state = {
        "boss_hps": state["boss_hps"].copy(),
        "skill_cooldowns": state["skill_cooldowns"].copy(),
        "turns_elapsed": state["turns_elapsed"] + 1,
        "current_boss": state["current_boss"]
    }

    # 对当前 Boss 造成伤害
    if new_state["current_boss"] < len(new_state["boss_hps"]):
        new_state["boss_hps"][new_state["current_boss"]] -= skill["damage"]
        while (new_state["current_boss"] < len(new_state["boss_hps"]) and 
               new_state["boss_hps"][new_state["current_boss"]] <= 0):
            new_state["current_boss"] += 1

    # 设置该技能冷却
    new_state["skill_cooldowns"][skill["id"]] = skill["cooldown"]
    return new_state

def compute_avg_damage(state, skills):
    available = get_available_skills(state, skills)
    if not available: return 1.0
    total = sum(s["damage"] for s in available)
    return total / len(available) if total > 0 else 1.0

def optimize_boss_fight(input_data):
    boss_hps = input_data["B"]
    player_skills = [
        {"id": i, "damage": s[0], "cooldown": s[1]}
        for i, s in enumerate(input_data["PlayerSkills"])
    ]
    if not boss_hps: return []

    initial_state = {
        "boss_hps": boss_hps.copy(),
        "skill_cooldowns": {s["id"]: 0 for s in player_skills},
        "turns_elapsed": 0,
        "current_boss": 0
    }

    counter = itertools.count()
    pq = [(compute_avg_damage(initial_state, player_skills), 0, next(counter), initial_state, [])]
    best_solution_turns = float('inf')
    best_skill_sequence = None

    visited = {}

    while pq:
        f_n, turns_elapsed, _, state, skill_sequence = heappop(pq)

        # 剪枝
        key = (tuple(state["boss_hps"]), tuple(state["skill_cooldowns"].items()), state["current_boss"])
        if key in visited and visited[key] <= turns_elapsed:
            continue
        visited[key] = turns_elapsed

        if f_n >= best_solution_turns:
            continue

        if state["current_boss"] >= len(state["boss_hps"]):
            if turns_elapsed < best_solution_turns:
                best_solution_turns = turns_elapsed
                best_skill_sequence = skill_sequence
            continue

        # 冷却统一减1（回合开始时）
        current_state = copy.deepcopy(state)
        for skill_id in current_state["skill_cooldowns"]:
            if current_state["skill_cooldowns"][skill_id] > 0:
                current_state["skill_cooldowns"][skill_id] -= 1

        for skill in get_available_skills(current_state, player_skills):
            new_state = apply_skill(current_state, skill, player_skills)
            new_turns = turns_elapsed + 1
            new_sequence = skill_sequence + [skill["id"]]

            remaining_hp = sum(hp for hp in new_state["boss_hps"][new_state["current_boss"]:] if hp > 0)
            h_n = math.ceil(remaining_hp / compute_avg_damage(new_state, player_skills))
            new_f_n = new_turns + h_n

            if new_f_n < best_solution_turns:
                heappush(pq, (new_f_n, new_turns, next(counter), new_state, new_sequence))

    return best_skill_sequence if best_skill_sequence else []


def visualize_battle(input_data, sequence):
    skills = [{"id": i, "damage": s[0], "cooldown": s[1]} for i, s in enumerate(input_data["PlayerSkills"])]

    state = {
        "boss_hps": input_data["B"].copy(),
        "skill_cooldowns": {s["id"]: 0 for s in skills},
        "turns_elapsed": 0,
        "current_boss": 0
    }
    print()

    for turn, skill_id in enumerate(sequence, 1):
        # 回合开始冷却减 1
        for k in state["skill_cooldowns"]:
            if state["skill_cooldowns"][k] > 0:
                state["skill_cooldowns"][k] -= 1


        skill = skills[skill_id]
        state = apply_skill(state, skill, skills)

        # 打印当前 BOSS 状态
        """print(f"Boss HPs: {state['boss_hps']}")
        print("Skill cooldowns:")
        for sid in sorted(state["skill_cooldowns"]):
            print(f"  Skill {sid}: {state['skill_cooldowns'][sid]} turn(s) left")
        print()"""

# ---------------------------
#  测试 + 可视化
# ---------------------------

def run_test_case():
    input_data = {
        "B": [30, 50, 40],
        "PlayerSkills": [
            [20, 2],  # Skill 0
            [9, 1],   # Skill 1
            [32, 3]   # Skill 2
        ]
    }

    sequence = optimize_boss_fight(input_data)

    print("Skill Use Sequence:", sequence)
    print(f"Total Turns: {len(sequence)}\n")

    visualize_battle(input_data, sequence)

# 运行测试
if __name__ == "__main__":
    run_test_case()
 
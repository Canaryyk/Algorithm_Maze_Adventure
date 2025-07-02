import math
import copy
import itertools
from heapq import heappush, heappop

# -------------------------------
# 技能释放与估值逻辑 (核心算法)
# -------------------------------

def get_available_skills(state, skills):
    return [s for s in skills if state["skill_cooldowns"].get(s["id"], 0) == 0]

def apply_skill(state, skill, skills):
    new_state = {
        "boss_hps": state["boss_hps"].copy(),
        "skill_cooldowns": state["skill_cooldowns"].copy(),
        "turns_elapsed": state["turns_elapsed"] + 1,
        "current_boss": state["current_boss"]
    }

    if new_state["current_boss"] < len(new_state["boss_hps"]):
        new_state["boss_hps"][new_state["current_boss"]] -= skill["damage"]
        while (new_state["current_boss"] < len(new_state["boss_hps"]) and 
               new_state["boss_hps"][new_state["current_boss"]] <= 0):
            new_state["current_boss"] += 1

    new_state["skill_cooldowns"][skill["id"]] = skill["cooldown"] + 1
    return new_state

def compute_avg_damage(state, skills):
    cooldowns = state["skill_cooldowns"]
    total_weighted_dmg = 0
    total_weight = 0

    for skill in skills:
        cid = skill["id"]
        cooldown = cooldowns.get(cid, 0)
        weight = 1.0 / (cooldown + 1)
        total_weighted_dmg += skill["damage"] * weight
        total_weight += weight

    return total_weighted_dmg / total_weight if total_weight > 0 else 1.0

def optimize_boss_fight(input_data):
    boss_hps = input_data["B"]
    player_skills = [
        {"id": i, "damage": s[0], "cooldown": s[1]}
        for i, s in enumerate(input_data["PlayerSkills"])
    ]
    if not boss_hps or not player_skills: return [], "输入数据不足"

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
    
    # 增加一个迭代次数限制，防止无限循环
    max_iterations = 200000 
    iterations = 0

    while pq and iterations < max_iterations:
        iterations += 1
        f_n, turns_elapsed, _, state, skill_sequence = heappop(pq)

        key = (
            tuple(state["boss_hps"]),
            tuple(sorted(state["skill_cooldowns"].items())),
            state["current_boss"]
        )
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

        current_state = copy.deepcopy(state)
        for skill_id in current_state["skill_cooldowns"]:
            if current_state["skill_cooldowns"][skill_id] > 0:
                current_state["skill_cooldowns"][skill_id] -= 1

        available_skills = get_available_skills(current_state, player_skills)
        if not available_skills: # 如果没有可用技能，则必须等待
             new_state = copy.deepcopy(current_state)
             new_state["turns_elapsed"] += 1
             new_turns = turns_elapsed + 1
             new_sequence = skill_sequence + [-1] # -1 代表等待
             
             remaining_hp = sum(hp for hp in new_state["boss_hps"][new_state["current_boss"]:] if hp > 0)
             if remaining_hp > 0:
                 avg_dmg = compute_avg_damage(new_state, player_skills)
                 h_n = math.ceil(remaining_hp / avg_dmg) if avg_dmg > 0 else float('inf')
                 new_f_n = new_turns + h_n
                 if new_f_n < best_solution_turns:
                    heappush(pq, (new_f_n, new_turns, next(counter), new_state, new_sequence))
        else:
            for skill in available_skills:
                new_state = apply_skill(current_state, skill, player_skills)
                new_turns = turns_elapsed + 1
                new_sequence = skill_sequence + [skill["id"]]

                remaining_hp = sum(hp for hp in new_state["boss_hps"][new_state["current_boss"]:] if hp > 0)
                
                if remaining_hp > 0:
                    avg_dmg = compute_avg_damage(new_state, player_skills)
                    h_n = math.ceil(remaining_hp / avg_dmg) if avg_dmg > 0 else float('inf')
                    new_f_n = new_turns + h_n
                    if new_f_n < best_solution_turns:
                        heappush(pq, (new_f_n, new_turns, next(counter), new_state, new_sequence))
                else: # Boss已被击败
                    if new_turns < best_solution_turns:
                         best_solution_turns = new_turns
                         best_skill_sequence = new_sequence
                    # 提前结束循环的一个分支
                    heappush(pq, (new_turns, new_turns, next(counter), new_state, new_sequence))


    if best_skill_sequence is None:
        return [], f"在 {max_iterations} 次迭代内未找到解。"

    return best_skill_sequence, None

import os
import json
import hashlib
import random

def is_prime(d):
    return d in {2, 3, 5, 7}

def parse_constraints(C):
    constraints = {
        "prime_and_unique": False,
        "position_even_odd": {},
        "fixed_digit": {}
    }
    for clue in C:
        if len(clue) == 2:
            if clue == [-1, -1]:
                constraints["prime_and_unique"] = True
            else:
                a, val = clue
                if 1 <= a <= 3 and val in (0, 1):
                    constraints["position_even_odd"][a] = val
        elif len(clue) == 3:
            for i in range(3):
                if clue[i] != -1:
                    constraints["fixed_digit"][i + 1] = clue[i]
    return constraints

def is_valid_choice(digit, current_password, constraints):
    pos = len(current_password) + 1
    if pos in constraints["fixed_digit"] and digit != constraints["fixed_digit"][pos]:
        return False
    if pos in constraints["position_even_odd"]:
        if constraints["position_even_odd"][pos] == 0 and digit % 2 != 0:
            return False
        if constraints["position_even_odd"][pos] == 1 and digit % 2 != 1:
            return False
    if constraints["prime_and_unique"]:
        if not is_prime(digit) or digit in current_password:
            return False
    return True

def satisfies_constraints(password, constraints):
    if len(password) != 3:
        return False
    if constraints["prime_and_unique"]:
        if not all(is_prime(d) for d in password):
            return False
        if len(set(password)) != 3:
            return False
    return True

def sha256_of_pwd(pwd):
    s = ''.join(str(x) for x in pwd)
    salt = b'\xb2S"e}\xdf\xb0\xfe\x9c\xde\xde\xfe\xf3\x1d\xdc>'
    return hashlib.sha256(salt + s.encode('utf-8')).hexdigest()

def solve_password(current_password, constraints, digits=range(10), counter=None):
    if counter is None:
        counter = {"attempts": 0}
    if len(current_password) == 3:
        counter["attempts"] += 1
        if satisfies_constraints(current_password, constraints):
            if sha256_of_pwd(current_password) == constraints["target_hash"]:
                return current_password
        return None
    for d in digits:
        if is_valid_choice(d, current_password, constraints):
            result = solve_password(current_password + [d], constraints, digits, counter)
            if result:
                return result
    return None

def method_a(constraints):
    counter = {"attempts": 0}
    result = solve_password([], constraints, digits=range(10), counter=counter)
    return result, counter["attempts"]

def method_b(constraints):
    prime_first = [2,3,5,7] + [d for d in range(10) if d not in {2,3,5,7}]
    counter = {"attempts": 0}
    result = solve_password([], constraints, digits=prime_first, counter=counter)
    return result, counter["attempts"]

def method_c(constraints):
    digits_all = list(range(10))
    random.shuffle(digits_all)  # 随机顺序尝试
    counter = {"attempts": 0}
    result = solve_password([], constraints, digits=digits_all, counter=counter)
    return result, counter["attempts"]

def try_all_methods(data):
    C = data.get("C", [])
    L = data.get("L", "")
    constraints = parse_constraints(C)
    constraints["target_hash"] = L

    res_a, att_a = method_a(constraints)
    res_b, att_b = method_b(constraints)
    res_c, att_c = method_c(constraints)

    candidates = []
    if res_a:
        candidates.append(("A", res_a, att_a))
    if res_b:
        candidates.append(("B", res_b, att_b))
    if res_c:
        candidates.append(("C", res_c, att_c))

    if not candidates:
        return None, max(att_a, att_b, att_c), "None"

    # 选择尝试次数最少的
    best = min(candidates, key=lambda x: x[2])
    return best[1], best[2], best[0]

def crack_all_files_in_folder(folder_path):
    files = sorted(f for f in os.listdir(folder_path) if f.endswith(".json"))

    total_a, total_b, total_c = 0, 0, 0

    for fname in files:
        path = os.path.join(folder_path, fname)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        C = data.get("C", [])
        L = data.get("L", "")
        constraints = parse_constraints(C)
        constraints["target_hash"] = L

        # 分别运行三种方法
        res_a, att_a = method_a(constraints)
        res_b, att_b = method_b(constraints)
        res_c, att_c = method_c(constraints)

        total_a += att_a
        total_b += att_b
        total_c += att_c

        # 输出当前样例的最优结果
        options = []
        if res_a:
            options.append(("A", res_a, att_a))
        if res_b:
            options.append(("B", res_b, att_b))
        if res_c:
            options.append(("C", res_c, att_c))

        if not options:
            print(f"[{fname}]  Not found by any method")
        else:
            best = min(options, key=lambda x: x[2])
            print(f"[{fname}]  Password: {''.join(str(d) for d in best[1])}, Attempts: {best[2]}, Method: {best[0]}")

    # 输出三种方法的总尝试次数
    print("\n Total attempts for each method:")
    print(f"  Method A: {total_a}")
    print(f"  Method B: {total_b}")
    print(f"  Method C: {total_c}")
    print(f" Final selected total = min({total_a}, {total_b}, {total_c}) = {min(total_a, total_b, total_c)}")


if __name__ == "__main__":
    crack_all_files_in_folder(r"C:\Users\35883\Desktop\test")

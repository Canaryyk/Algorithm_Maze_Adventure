import hashlib

# 判断是否是质数（在 0~9 范围内）
def is_prime(digit):
    return digit in {2, 3, 5, 7}

# 解析线索格式
def parse_constraints(C):
    constraints = {
        "prime_and_unique": False,
        "position_even_odd": {},   # {1:0, 2:1, ...}
        "fixed_digit": {}          # {1: b, 2: b, 3: b}
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

# 单位判断是否合法
def is_valid_choice(digit, current_password, constraints):
    pos = len(current_password) + 1  # 1-based

    if pos in constraints["fixed_digit"]:
        if digit != constraints["fixed_digit"][pos]:
            return False

    if pos in constraints["position_even_odd"]:
        expected = constraints["position_even_odd"][pos]
        if expected == 0 and digit % 2 != 0:
            return False
        if expected == 1 and digit % 2 != 1:
            return False

    if constraints["prime_and_unique"]:
        if not is_prime(digit):
            return False
        if digit in current_password:
            return False

    return True

# 整体密码判断
def satisfies_constraints(password, constraints):
    if len(password) != 3:
        return False

    if constraints["prime_and_unique"]:
        if not all(is_prime(d) for d in password):
            return False
        if len(set(password)) != 3:
            return False

    return True

# 计算哈希
def sha256_hex(password_digits):
    s = ''.join(str(d) for d in password_digits)
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

# 添加 solve_password 的计数器版本
def solve_password(current_password, constraints, digits=range(10), counter=None):
    if counter is None:
        counter = {"attempts": 0}

    if len(current_password) == 3:
        counter["attempts"] += 1
        if satisfies_constraints(current_password, constraints):
            h = sha256_hex(current_password)
            if h == constraints["target_hash"]:
                return current_password
        return None

    for d in digits:
        if is_valid_choice(d, current_password, constraints):
            res = solve_password(current_password + [d], constraints, digits, counter)
            if res:
                return res
    return None


def crack_password_from_input(input_data):
    #改为输入样例的文件名
    C = input_data.get("C", [])
    L = input_data.get("L", "")

    constraints = parse_constraints(C)
    constraints["target_hash"] = L

    counter = {"attempts": 0}
    password = solve_password([], constraints, counter=counter)

    if password:
        print("正确密码:", ''.join(str(d) for d in password))
    else:
        print("未找到符合条件的密码")
# “print("尝试次数:", counter["attempts"])”密码求解次数
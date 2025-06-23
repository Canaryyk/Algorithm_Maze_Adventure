constraints = {
    "prime_only": True,           # ÿλ����������
    "no_repetition": True         # �������ظ�����
}

def is_prime(digit):
    #Helper function to check if a digit is prime.
    return digit in {2, 3, 5, 7}

def is_valid_choice(digit, current_password, constraints):
    # ���ƣ���ǰ���ֱ���������
    if constraints.get("prime_only", False):
        if not is_prime(digit):
            return False

    # ���ƣ���ǰ���ֲ����ظ�
    if constraints.get("no_repetition", False):
        if digit in current_password:
            return False

    return True


def satisfies_constraints(password, constraints):
    # ��鳤��Ϊ3�������������ѱ�֤��Ҳ���������飩
    if len(password) != 3:
        return False

    # ���ƣ��������ֱ���������
    if constraints.get("prime_only", False):
        for digit in password:
            if not is_prime(digit):
                return False

    # ���ƣ��������ֱ���Ψһ
    if constraints.get("no_repetition", False):
        if len(set(password)) != len(password):
            return False

    return True

def solve_password(current_password, constraints, digits=[0,1,2,3,4,5,6,7,8,9]):
    # Base case: Complete password formed
    if len(current_password) == 3:
        if satisfies_constraints(current_password, constraints):
            return current_password
        return None
    
    # Recursive step: Try each possible digit
    for digit in digits:
        # Pruning: Check constraints (e.g., prime, no repetition)
        if is_valid_choice(digit, current_password, constraints):
            # Explore: Add digit and recurse
            result = solve_password(current_password + [digit], constraints, digits)
            if result:
                return result
            # Backtrack: Implicitly handled by not modifying current_password permanently
    return None

def crack_password(constraints):
    # Entry point: Start with empty password
    return solve_password([], constraints)  
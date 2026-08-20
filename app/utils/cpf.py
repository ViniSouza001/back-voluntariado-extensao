def normalize_cpf(cpf: str) -> str:
    return "".join(caractere for caractere in cpf if caractere.isdigit())

def valid_cpf(cpf: str) -> bool:
    normalized = normalize_cpf(cpf)
    if len(normalized) != 11 or normalized == normalized[0] * 11:
        return False

    first_sum = sum(int(normalized[index]) * (10 - index) for index in range(9))
    first_remainder = first_sum % 11
    first_digit = 0 if first_remainder < 2 else 11 - first_remainder

    if int(normalized[9]) != first_digit:
        return False

    second_sum = sum(int(normalized[index]) * (11 - index) for index in range(10))
    second_remainder = second_sum % 11
    second_digit = 0 if second_remainder < 2 else 11 - second_remainder
    return int(normalized[10]) == second_digit

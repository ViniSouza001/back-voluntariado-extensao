def normalizar_cpf(cpf: str) -> str:
    return "".join(caractere for caractere in cpf if caractere.isdigit())


def cpf_valido(cpf: str) -> bool:
    normalizado = normalizar_cpf(cpf)
    if len(normalizado) != 11 or normalizado == normalizado[0] * 11:
        return False

    primeira_soma = sum(int(normalizado[indice]) * (10 - indice) for indice in range(9))
    primeiro_resto = primeira_soma % 11
    primeiro_digito = 0 if primeiro_resto < 2 else 11 - primeiro_resto
    if int(normalizado[9]) != primeiro_digito:
        return False

    segunda_soma = sum(int(normalizado[indice]) * (11 - indice) for indice in range(10))
    segundo_resto = segunda_soma % 11
    segundo_digito = 0 if segundo_resto < 2 else 11 - segundo_resto
    return int(normalizado[10]) == segundo_digito

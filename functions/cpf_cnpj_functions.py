from fastapi import HTTPException

def verificar_cpf(cpf):
    # Remove caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, cpf))
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        raise HTTPException(status_code=400, detail="CPF deve ter 11 dígitos")
    
    # Verifica se todos os dígitos são iguais (CPFs inválidos conhecidos)
    if cpf == cpf[0] * 11:
        raise HTTPException(status_code=400, detail="CPF não pode ser somente números iguais")
    
    # Calcula o primeiro dígito verificador (posição 9)
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    # Verifica o primeiro dígito verificador
    if int(cpf[9]) != digito1:
        return False
    
    # Calcula o segundo dígito verificador (posição 10)
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    # Verifica o segundo dígito verificador
    if int(cpf[10]) != digito2:
        return False
    
    return True

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import date

class EntidadeSchema(BaseModel):
    nome: str = Field(min_length=3, max_length=100)
    nome_usuario: str = Field(min_length=3, max_length=50)
    ramo: str
    descricao: str
    cidade: str
    uf: str
    # criado_em: date = date.today()
    
    # para o python não reconhecer esse Schema como um dicionário
    class Config:
        from_mode = True
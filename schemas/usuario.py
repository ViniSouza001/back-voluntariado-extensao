from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class UsuarioSchema(BaseModel):
    nome: str
    email: str
    senha: str
    data_nasc: date
    cidade: str
    uf: str
    admin: Optional[bool]

    # para o python não reconhecer esse Schema como um dicionário
    class Config:
        from_attributes = True
    


    
# class UsuarioResponseSchema(BaseModel):
#     id: int
#     nome: str
#     email: str
#     data_nasc: date

#     class Config:
#         from_attributes = True
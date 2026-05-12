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
    confirmado: Optional[bool] = False
    admin: Optional[bool] = False

    # para o python não reconhecer esse Schema como um dicionário
    class Config:
        orm_mode = True
    


    
# class UsuarioResponseSchema(BaseModel):
#     id: int
#     nome: str
#     email: str
#     data_nasc: date

#     class Config:
#         from_attributes = True
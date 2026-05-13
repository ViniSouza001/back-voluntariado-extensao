from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import date

class UsuarioSchema(BaseModel):
    nome: str = Field(min_length=3, max_length=100)
    email: EmailStr
    senha: str = Field(min_length=6)
    data_nasc: date
    cidade: str
    uf: str
    admin: Optional[bool] = False

    # para o python não reconhecer esse Schema como um dicionário
    class Config:
        orm_mode = True

class LoginSchema(BaseModel):
    email: EmailStr
    senha: str

    class Config:
        from_attributes = True

    
# class UsuarioResponseSchema(BaseModel):
#     id: int
#     nome: str
#     email: str
#     data_nasc: date

#     class Config:
#         from_attributes = True
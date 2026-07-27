from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class CriacaoEntidade(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nome: str = Field(min_length=3, max_length=100)
    nome_usuario: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")
    setor: str = Field(min_length=2, max_length=100)
    descricao: str = Field(min_length=3, max_length=2000)
    cidade: str = Field(min_length=2, max_length=100)
    uf: str = Field(pattern=r"^[a-zA-Z]{2}$")


class RespostaEntidade(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    nome_usuario: str
    setor: str
    descricao: str
    cidade: str
    uf: str
    criado_em: date

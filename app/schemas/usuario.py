from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RespostaUsuario(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    cpf: str
    email: str
    data_nascimento: date
    cidade: str
    uf: str
    email_confirmado: bool
    url_foto_perfil: str | None


class AtualizacaoUsuario(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nome: str | None = Field(default=None, min_length=3, max_length=100)
    data_nascimento: date | None = None
    cidade: str | None = Field(default=None, min_length=2, max_length=100)
    uf: str | None = Field(default=None, pattern=r"^[a-zA-Z]{2}$")

    @field_validator("data_nascimento")
    @classmethod
    def data_nascimento_deve_estar_no_passado(cls, valor: date | None) -> date | None:
        if valor is not None and valor >= date.today():
            raise ValueError("A data de nascimento deve estar no passado")
        return valor


class AlteracaoSenha(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    senha_atual: str = Field(min_length=1, max_length=72)
    nova_senha: str = Field(min_length=6, max_length=72)
    confirmacao_nova_senha: str = Field(min_length=6, max_length=72)

from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class CadastroUsuario(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nome: str = Field(min_length=3, max_length=100)
    cpf: str = Field(min_length=11, max_length=14)
    email: EmailStr
    senha: str = Field(min_length=6, max_length=72)
    data_nascimento: date
    cidade: str = Field(min_length=2, max_length=100)
    uf: str = Field(pattern=r"^[a-zA-Z]{2}$")

    @field_validator("data_nascimento")
    @classmethod
    def data_nascimento_deve_estar_no_passado(cls, valor: date) -> date:
        if valor >= date.today():
            raise ValueError("A data de nascimento deve estar no passado")
        return valor


class SolicitacaoLogin(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    senha: str = Field(min_length=1, max_length=72)


class RespostaToken(BaseModel):
    usuario: str
    token_acesso: str
    tipo_token: str = "bearer"


class RespostaCadastro(BaseModel):
    mensagem: str
    email_confirmacao_enviado: bool


class SolicitacaoReenvioConfirmacao(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr

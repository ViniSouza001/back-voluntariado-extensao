# API da Plataforma de Voluntariado

Backend em FastAPI para uma plataforma de voluntariado. O sistema oferece cadastro de contas,
confirmação de e-mail, autenticação com JWT, gerenciamento de perfil e criação de entidades.

## Requisitos

- Python 3.12 ou mais recente
- É recomendado utilizar um ambiente virtual

## Configuração local

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Substitua `CHAVE_SECRETA` no `.env` por um valor aleatório longo. Preencha as configurações de
e-mail e altere `EMAIL_HABILITADO=true` somente quando o SMTP estiver configurado.

Crie ou atualize o banco local:

```powershell
alembic upgrade head
```

Inicie a API:

```powershell
uvicorn app.principal:aplicacao --reload
```

A documentação interativa fica em <http://localhost:8000/docs> e a verificação de saúde em
<http://localhost:8000/saude>.

## Endpoints principais

| Método | Caminho | Finalidade |
|---|---|---|
| `POST` | `/api/v1/autenticacao/cadastro` | Criar uma conta |
| `POST` | `/api/v1/autenticacao/entrar` | Obter um token JWT |
| `GET` | `/api/v1/autenticacao/confirmar-email/{token}` | Confirmar o e-mail |
| `POST` | `/api/v1/autenticacao/reenviar-confirmacao` | Reenviar a confirmação |
| `GET` | `/api/v1/usuarios/eu` | Consultar o próprio perfil |
| `PATCH` | `/api/v1/usuarios/eu` | Atualizar o próprio perfil |
| `PATCH` | `/api/v1/usuarios/eu/senha` | Alterar a senha |
| `DELETE` | `/api/v1/usuarios/eu` | Excluir a própria conta |
| `POST` | `/api/v1/entidades` | Criar uma entidade |

Os endpoints protegidos esperam o cabeçalho `Authorization: Bearer <token>`.

## Estrutura do projeto

```text
app/api/           Rotas HTTP e dependências do FastAPI
app/core/          Configurações, segurança e exceções
app/db/            Motor, sessões e base do SQLAlchemy
app/models/        Mapeamento das tabelas do banco
app/repositories/  Consultas reutilizáveis ao banco
app/schemas/       Validação das entradas e respostas
app/services/      Regras de negócio e transações
app/utils/         Funções puras de validação e formatação
alembic/           Histórico versionado do banco
data/              Banco SQLite local, não versionado
docs/              Documentação de desenvolvimento
tests/             Testes unitários e de integração
uploads/           Arquivos enviados em execução, não versionados
```

Consulte [docs/ARQUITETURA.md](docs/ARQUITETURA.md) para entender as regras
entre as camadas.

## Verificações de qualidade

```powershell
python -m pytest
python -m ruff check .
python -m ruff format --check .
alembic check
```

## Observações sobre nomes externos

Alguns nomes permanecem em inglês porque pertencem às bibliotecas ou aos protocolos usados,
como `FastAPI`, `BaseModel`, `Session`, `upgrade()`, `downgrade()`, `Authorization` e `Bearer`.
Todo identificador que pertence ao projeto foi escrito em português.

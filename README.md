# Volunteer Platform API

FastAPI backend for a volunteer platform. It supports account registration, email
confirmation, JWT authentication, profile management and organization creation.

## Requirements

- Python 3.12 or newer
- A virtual environment is strongly recommended

## Local setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Replace `SECRET_KEY` in `.env` with a long random value. Configure the mail variables and set
`EMAIL_ENABLED=true` only when SMTP delivery is ready.

Create or update the local database:

```powershell
alembic upgrade head
```

Start the API:

```powershell
uvicorn app.main:app --reload
```

Interactive documentation is available at <http://localhost:8000/docs> and the health check
is available at <http://localhost:8000/health>.

## Main endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Create an account |
| `POST` | `/api/v1/auth/login` | Obtain a JWT access token |
| `GET` | `/api/v1/auth/confirm-email/{token}` | Confirm an email address |
| `POST` | `/api/v1/auth/resend-confirmation` | Request a new confirmation email |
| `GET` | `/api/v1/users/me` | Read the authenticated profile |
| `PATCH` | `/api/v1/users/me` | Update the authenticated profile |
| `PATCH` | `/api/v1/users/me/password` | Change the password |
| `DELETE` | `/api/v1/users/me` | Delete the authenticated account |
| `POST` | `/api/v1/organizations` | Create an organization |

All protected endpoints expect `Authorization: Bearer <token>`.

## Project structure

```text
app/api/           HTTP routes and FastAPI dependencies
app/core/          settings, security and application exceptions
app/db/            SQLAlchemy engine, sessions and declarative base
app/models/        database table mappings
app/repositories/  reusable database queries
app/schemas/       API request and response validation
app/services/      business use cases and transaction boundaries
app/utils/         pure validation and formatting functions
alembic/           versioned database migrations
database/          local runtime database (not committed)
docs/              architecture and development documentation
tests/             unit and API integration tests
uploads/           runtime user uploads (not committed)
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the responsibility rules between layers.

## Quality checks

```powershell
python -m unittest discover -s tests -v
ruff check .
alembic check
```

## API migration notes

The previous Portuguese and mixed-language paths were replaced by the versioned English API.
The most relevant changes are:

- `/auth/*` became `/api/v1/auth/*`.
- `/user/me/{token}` became `/api/v1/users/me`; the token belongs in the authorization header.
- `/entity/entidade` became `/api/v1/organizations`.
- Unauthenticated `POST /auth/delete/{id}` was replaced by authenticated
  `DELETE /api/v1/users/me`.

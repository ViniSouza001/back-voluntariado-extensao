# Arquitetura

O backend utiliza uma arquitetura simples em camadas. As dependências seguem esta direção:

```text
Rotas HTTP -> Serviços -> Repositórios -> Modelos SQLAlchemy -> Banco de dados
                  |-> e-mail, segurança e utilitários puros
```

## Regras das camadas

- `api/routes` recebe e devolve dados HTTP, sem concentrar regras de negócio.
- `services` implementa casos de uso completos e controla as transações.
- `repositories` contém consultas reutilizáveis ao banco.
- `models` representa as tabelas e seus relacionamentos.
- `schemas` valida o conteúdo recebido e devolvido pela API.
- `core` concentra configurações, segurança e exceções da aplicação.
- `utils` contém funções puras, sem dependência do banco ou do FastAPI.

Evite criar pastas genéricas como `funcoes` ou `ajudantes`. Um código novo deve ficar na camada
responsável pelo seu comportamento. Quando um módulo ficar grande, divida-o por assunto do
domínio, mantendo nomes claros em português.

# Architecture

The backend uses a small layered architecture. Dependencies point inward in this order:

```text
HTTP routes -> services -> repositories -> SQLAlchemy models -> database
                    |-> email, security and pure utilities
```

## Layer rules

- `api/routes` handles HTTP input and output only.
- `services` implements complete business use cases and transaction boundaries.
- `repositories` contains reusable database queries.
- `models` maps Python classes to database tables.
- `schemas` validates API request and response payloads.
- `core` owns configuration, security primitives and application exceptions.
- `utils` contains pure functions with no database or web-framework dependency.

Do not create a generic `functions` or `helpers` module. Put new code in the layer that owns
its responsibility. Create a new module named after the domain when a current module becomes
too large.

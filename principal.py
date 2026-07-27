"""Ponto de entrada compatível para ``uvicorn principal:aplicacao``."""

from app.principal import aplicacao, criar_aplicacao

__all__ = ["aplicacao", "criar_aplicacao"]

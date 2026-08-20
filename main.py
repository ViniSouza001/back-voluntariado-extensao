""" Compatiby entry point for ``python -m uvicorn app.main:app --reload`` """

from app.main import app, create_application

__all__ = ["app", "create_application"]
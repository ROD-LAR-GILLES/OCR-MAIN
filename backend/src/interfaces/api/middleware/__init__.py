"""
Middleware personalizado para FastAPI.
"""
from .error_handler import ErrorHandlerMiddleware

__all__ = ['ErrorHandlerMiddleware']
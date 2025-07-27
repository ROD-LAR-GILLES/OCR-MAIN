"""
Middleware personalizado para manejo de errores.
"""
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import traceback
from datetime import datetime

from interfaces.api.models.responses import ErrorResponse

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware para capturar y manejar errores globalmente."""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
            
        except Exception as exc:
            logger.error(f"Error no manejado en {request.method} {request.url.path}: {str(exc)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Determinar tipo de error y código de estado
            if isinstance(exc, ValueError):
                status_code = 400
                error_type = "ValueError"
            elif isinstance(exc, FileNotFoundError):
                status_code = 404
                error_type = "FileNotFoundError"
            elif isinstance(exc, PermissionError):
                status_code = 403
                error_type = "PermissionError"
            elif isinstance(exc, TimeoutError):
                status_code = 408
                error_type = "TimeoutError"
            else:
                status_code = 500
                error_type = "InternalServerError"
            
            # Crear respuesta de error estructurada
            error_response = ErrorResponse(
                error=error_type,
                message=str(exc),
                details={
                    "method": request.method,
                    "path": str(request.url.path),
                    "query_params": dict(request.query_params)
                },
                timestamp=datetime.now()
            )
            
            return JSONResponse(
                status_code=status_code,
                content=error_response.dict()
            )
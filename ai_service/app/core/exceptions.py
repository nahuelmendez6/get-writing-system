from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import logger


class AIServiceException(Exception):
    """Base exception for AI Service errors."""

    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class LLMTimeoutError(AIServiceException):
    def __init__(
        self,
        message: str = "Tiempo de espera agotado al consultar el modelo de IA.",
    ) -> None:
        super().__init__(
            error_code="LLM_TIMEOUT",
            message=message,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        )


class LLMProviderError(AIServiceException):
    def __init__(
        self,
        message: str = "Error en el proveedor de LLM.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            error_code="LLM_PROVIDER_ERROR",
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details,
        )


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup standardized JSON error handlers."""

    @app.exception_handler(AIServiceException)
    async def ai_service_exception_handler(
        request: Request, exc: AIServiceException
    ) -> JSONResponse:
        logger.warning(
            "AI Service exception: %s (code=%s)",
            exc.message,
            exc.error_code,
            extra={"path": request.url.path, "details": exc.details},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": {
                    "error_code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        error_code = (
            "NOT_FOUND" if exc.status_code == 404 else f"HTTP_{exc.status_code}"
        )
        msg = (
            exc.detail if isinstance(exc.detail, str) else "Error en la solicitud HTTP"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": {
                    "error_code": error_code,
                    "message": msg,
                    "details": {},
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning(
            "Validation error at %s: %s",
            request.url.path,
            str(exc.errors()),
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": {
                    "error_code": "VALIDATION_ERROR",
                    "message": "Error de validación en la carga útil enviada.",
                    "details": {"errors": exc.errors()},
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error(
            "Unhandled exception in ai_service at %s: %s",
            request.url.path,
            str(exc),
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": {
                    "error_code": "INTERNAL_SERVER_ERROR",
                    "message": "Ha ocurrido un error interno en el servicio de IA.",
                    "details": {},
                }
            },
        )

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import logger
from app.schemas.health import ErrorDetail, StandardErrorResponse


class AppException(Exception):
    """Base application exception with standardized error structure."""

    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(AppException):
    def __init__(
        self,
        message: str = "Recurso no encontrado",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            error_code="RESOURCE_NOT_FOUND",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class DatabaseConnectionError(AppException):
    def __init__(
        self,
        message: str = "Error de conexión con la base de datos",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            error_code="DATABASE_CONNECTION_ERROR",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
        )


def setup_exception_handlers(app: FastAPI) -> None:
    """Register uniform exception handlers complying with API standards."""

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        logger.warning(
            "Application error: %s",
            exc.message,
            extra={"error_code": exc.error_code, "path": request.url.path},
        )
        payload = StandardErrorResponse(
            detail=ErrorDetail(
                error_code=exc.error_code,
                message=exc.message,
                details=exc.details,
            )
        )
        return JSONResponse(status_code=exc.status_code, content=payload.model_dump())

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        code_mapping = {
            status.HTTP_404_NOT_FOUND: "NOT_FOUND",
            status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
            status.HTTP_403_FORBIDDEN: "FORBIDDEN",
            status.HTTP_405_METHOD_NOT_ALLOWED: "METHOD_NOT_ALLOWED",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "INTERNAL_SERVER_ERROR",
            status.HTTP_503_SERVICE_UNAVAILABLE: "SERVICE_UNAVAILABLE",
        }
        error_code = code_mapping.get(exc.status_code, f"HTTP_{exc.status_code}")
        message = (
            exc.detail
            if isinstance(exc.detail, str)
            else "Error HTTP procesando la solicitud."
        )

        logger.warning(
            "HTTP error %d at %s: %s",
            exc.status_code,
            request.url.path,
            message,
        )
        payload = StandardErrorResponse(
            detail=ErrorDetail(
                error_code=error_code,
                message=message,
                details={},
            )
        )
        return JSONResponse(status_code=exc.status_code, content=payload.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning(
            "Validation error at %s: %s",
            request.url.path,
            str(exc.errors()),
        )
        payload = StandardErrorResponse(
            detail=ErrorDetail(
                error_code="VALIDATION_ERROR",
                message="Error de validación en los datos de la petición.",
                details={"errors": exc.errors()},
            )
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=payload.model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error(
            "Unhandled server exception at %s: %s",
            request.url.path,
            str(exc),
            exc_info=True,
        )
        # Never leak internal traces, connection strings, or credentials to client
        payload = StandardErrorResponse(
            detail=ErrorDetail(
                error_code="INTERNAL_SERVER_ERROR",
                message="Ha ocurrido un error inesperado.",
                details={},
            )
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=payload.model_dump(),
        )

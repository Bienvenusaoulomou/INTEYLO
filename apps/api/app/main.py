"""Point d'entrée FastAPI d'INTEYLO."""

import json
import logging
import sys
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import get_settings
from app.core.db import check_database_role, get_session_factory
from app.core.errors import ApiError, ErrorCode
from app.core.messages_fr import message_for, translate_validation_error
from app.modules.identity.router import router as auth_router
from app.modules.organizations.invitations_public import router as invitations_router
from app.modules.organizations.router import router as org_router
from app.modules.platform.router import router as platform_router

CLIENT_HEADER = "x-inteylo-client"
_UNSAFE = {"POST", "PUT", "PATCH", "DELETE"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("request_id", "method", "path", "status", "duration_ms"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def _configure_logging(level: str) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger("inteylo")
    root.handlers = [handler]
    root.setLevel(level)
    root.propagate = False


def error_response(
    code: ErrorCode, status: int, details: list[dict[str, str]] | None = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "error": {"code": code.value, "message": message_for(code), "details": details or []}
        },
    )


def create_app() -> FastAPI:
    settings = get_settings()
    _configure_logging(settings.log_level)
    log = logging.getLogger("inteylo.http")
    docs = settings.environment in ("development", "test")
    app = FastAPI(
        title="API INTEYLO",
        version="0.1.0",
        docs_url="/docs" if docs else None,
        redoc_url=None,
        openapi_url="/openapi.json" if docs else None,
    )

    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
            allow_headers=["content-type", CLIENT_HEADER],
        )

    @app.middleware("http")
    async def protect(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
        start = time.perf_counter()
        # Protection CSRF : un formulaire d'un autre site ne peut pas poser cet en-tête
        # sans requête préalable CORS, refusée pour les origines non autorisées.
        if (
            request.method in _UNSAFE
            and request.url.path.startswith("/v1/")
            and request.headers.get(CLIENT_HEADER) != "web"
        ):
            response: Response = error_response(ErrorCode.CSRF_HEADER_MISSING, 403)
        else:
            response = await call_next(request)
        response.headers["x-request-id"] = request_id
        response.headers["x-content-type-options"] = "nosniff"
        response.headers["referrer-policy"] = "no-referrer"
        response.headers["cache-control"] = "no-store"
        log.info(
            "request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round((time.perf_counter() - start) * 1000, 1),
            },
        )
        return response

    @app.exception_handler(ApiError)
    async def api_error(_: Request, exc: ApiError) -> JSONResponse:
        return error_response(exc.code, exc.status_code, exc.details)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        errors = exc.errors()
        if any(e.get("type") == "json_invalid" for e in errors):
            return error_response(ErrorCode.MALFORMED_REQUEST, 400)
        return error_response(
            ErrorCode.VALIDATION_ERROR, 422, [translate_validation_error(dict(e)) for e in errors]
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        mapping = {404: ErrorCode.NOT_FOUND, 405: ErrorCode.METHOD_NOT_ALLOWED}
        code = mapping.get(exc.status_code, ErrorCode.MALFORMED_REQUEST)
        return error_response(code, exc.status_code)

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logging.getLogger("inteylo.error").exception(
            "unhandled error", extra={"path": request.url.path}
        )
        return error_response(ErrorCode.INTERNAL_ERROR, 500)

    @app.get("/health/live", tags=["santé"])
    def live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready", tags=["santé"])
    def ready() -> JSONResponse:
        try:
            with get_session_factory()() as db:
                db.execute(text("select 1"))
                problems = check_database_role(db)
        except Exception:
            logging.getLogger("inteylo.health").exception("database not ready")
            return error_response(ErrorCode.SERVICE_UNAVAILABLE, 503)
        if problems:
            logging.getLogger("inteylo.health").error("unsafe database role: %s", problems)
            return error_response(ErrorCode.SERVICE_UNAVAILABLE, 503)
        return JSONResponse({"status": "ok"})

    app.include_router(auth_router)
    app.include_router(org_router)
    app.include_router(invitations_router)
    app.include_router(platform_router)
    return app


app = create_app()

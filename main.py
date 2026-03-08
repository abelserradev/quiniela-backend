import logging
import re
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.endpoints import auth, partidos, predicciones, puntuacion, tabla, users
from app.core.config import get_settings
from app.core.database import Base, engine
from app.services.actualizacion_resultados import ejecutar_actualizacion_resultados
from scripts.seed_partidos_mundial_2026 import run as seed_partidos

settings = get_settings()

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Cabeceras de seguridad para mitigar ataques comunes."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        if not settings.debug:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description or "",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        },
    }
    for path, path_item in openapi_schema.get("paths", {}).items():
        for method in ("get", "post", "put", "delete", "patch"):
            op = path_item.get(method)
            if op and op.get("security"):
                op["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def job_actualizacion_resultados():
    """Tarea programada: actualiza resultados y recalcula puntuación."""
    try:
        resultado = ejecutar_actualizacion_resultados()
        logger.info(
            "CRON actualizacion_resultados: partidos=%s, predicciones=%s",
            resultado["partidos_actualizados"],
            resultado["predicciones_actualizadas"],
        )
    except Exception as e:
        logger.exception("Error en CRON actualizacion_resultados: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_partidos()
    scheduler.add_job(
        job_actualizacion_resultados,
        "interval",
        minutes=10,
        id="actualizacion_resultados",
    )
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True},
)

app.openapi = custom_openapi
app.add_middleware(SecurityHeadersMiddleware)


def _get_cors_config() -> dict:
    if settings.environment != "development" and not settings.debug:
        return {"allow_origins": []}
    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    origins = origins or ["http://localhost:3000", "http://127.0.0.1:3000"]
    return {
        "allow_origins": origins,
        "allow_origin_regex": r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    }


cors_config = _get_cors_config()
cors_kwargs: dict = {
    "allow_origins": cors_config["allow_origins"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
    "expose_headers": ["*"],
}
if cors_config.get("allow_origin_regex"):
    cors_kwargs["allow_origin_regex"] = cors_config["allow_origin_regex"]
app.add_middleware(CORSMiddleware, **cors_kwargs)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Asegura que las respuestas 500 incluyan cabeceras CORS."""
    if isinstance(exc, HTTPException):
        raise exc
    logger.exception("Error no controlado: %s", exc)
    origin = request.headers.get("origin", "")
    origins = cors_config["allow_origins"]
    regex = cors_config.get("allow_origin_regex")
    allowed = origin in origins or (
        bool(regex and origin and re.fullmatch(regex, origin))
    )
    body = {"detail": "Error interno del servidor"}
    response = JSONResponse(status_code=500, content=body)
    if allowed:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(partidos.router, prefix="/api")
app.include_router(predicciones.router, prefix="/api")
app.include_router(puntuacion.router, prefix="/api")
app.include_router(tabla.router, prefix="/api")
"""Schemas Pydantic para validación de request/response."""
from app.schemas.auth import LoginRequest, RegistroRequest, TokenResponse
from app.schemas.partido import PartidoResponse
from app.schemas.prediccion import PrediccionRequest, PrediccionResponse
from app.schemas.puntuacion import RecalcularResponse
from app.schemas.tabla import PosicionResponse
from app.schemas.user import PerfilResponse

__all__ = [
    "RegistroRequest",
    "LoginRequest",
    "TokenResponse",
    "PerfilResponse",
    "PartidoResponse",
    "PrediccionRequest",
    "PrediccionResponse",
    "PosicionResponse",
    "RecalcularResponse",
]

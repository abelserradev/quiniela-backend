"""Validación de API key con hash SHA256.
El token nunca se almacena en texto plano; solo su hash en .env.
"""
import hashlib
import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.core.config import get_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def _hash_token(token: str) -> str:
    """Hash SHA256 del token para comparación segura."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verificar_api_key(
    api_key: Annotated[str | None, Depends(api_key_header)],
) -> bool:
    """Valida el API key contra el hash almacenado.
    Usa comparación constante para evitar ataques de timing.
    """
    settings = get_settings()
    stored_hash = getattr(settings, "api_key_hash", None)
    if not stored_hash:
        return True
    if not api_key or not api_key.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acceso no autorizado",
        )
    incoming_hash = _hash_token(api_key.strip())
    if not secrets.compare_digest(incoming_hash, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acceso no autorizado",
        )
    return True

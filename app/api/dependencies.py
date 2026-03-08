from typing import Annotated

from fastapi import Cookie, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decodificar_token
from app.models.usuario import Usuario


def _extraer_token(
    authorization: Annotated[str | None, Header()] = None,
    access_token: Annotated[str | None, Cookie(alias="access_token")] = None,
) -> str | None:
    """Token desde cookie (preferido) o header Authorization: Bearer <token>."""
    if access_token:
        return access_token
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:].strip()
    return None


def obtener_usuario_actual(
    token: Annotated[str | None, Depends(_extraer_token)],
    db: Annotated[Session, Depends(get_db)],
) -> Usuario:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decodificar_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error de autenticación",
        )
    usuario_id = int(payload["sub"])
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


def obtener_usuario_opcional(
    token: Annotated[str | None, Depends(_extraer_token)],
    db: Annotated[Session, Depends(get_db)],
) -> Usuario | None:
    if not token:
        return None
    payload = decodificar_token(token)
    if not payload or "sub" not in payload:
        return None
    usuario_id = int(payload["sub"])
    return db.get(Usuario, usuario_id)
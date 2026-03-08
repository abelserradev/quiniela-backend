from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import crear_access_token, hashear_password, verificar_password
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, LoginResponse, RegistroRequest, RegistroResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/registro", response_model=RegistroResponse)
def registrar_usuario(
    body: RegistroRequest,
    db: Session = Depends(get_db),
):
    stmt = select(Usuario).where(Usuario.usuario == body.usuario)
    if db.execute(stmt).scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Usuario no disponible")
    stmt = select(Usuario).where(Usuario.email == body.email)
    if db.execute(stmt).scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Usuario no disponible")
    usuario = Usuario(
        usuario=body.usuario,
        nombre=body.nombre,
        apellido=body.apellido,
        email=body.email,
        password_hash=hashear_password(body.password),
    )
    db.add(usuario)
    db.flush()
    return RegistroResponse()


def _establecer_cookie_sesion(response: Response, token: str) -> None:
    """Establece cookie HttpOnly con el token. No expone el token en el body."""
    settings = get_settings()
    max_age = settings.jwt_expiration_minutes * 60
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        max_age=max_age,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
        path="/",
    )


@router.post("/login", response_model=LoginResponse)
def login(
    body: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    stmt = select(Usuario).where(Usuario.email == body.email)
    usuario = db.execute(stmt).scalar_one_or_none()
    if not usuario or not verificar_password(body.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Error de ingreso")
    token = crear_access_token(usuario.id)
    _establecer_cookie_sesion(response, token)
    return LoginResponse()


@router.post("/logout", response_model=LoginResponse)
def logout(response: Response):
    """Cierra sesión eliminando la cookie HttpOnly."""
    settings = get_settings()
    response.delete_cookie(
        key=settings.auth_cookie_name,
        path="/",
    )
    return LoginResponse(mensaje="sesión cerrada")
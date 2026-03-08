from fastapi import APIRouter, Depends

from app.api.dependencies import obtener_usuario_actual
from app.models.usuario import Usuario
from app.schemas.user import PerfilResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=PerfilResponse)
def obtener_perfil(usuario: Usuario = Depends(obtener_usuario_actual)):
    return PerfilResponse(
        id=usuario.id,
        usuario=usuario.usuario,
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        email=usuario.email,
        total_puntos=usuario.total_puntos,
    )
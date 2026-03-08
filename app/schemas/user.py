"""Schemas para usuario/perfil."""
from pydantic import BaseModel


class PerfilResponse(BaseModel):
    id: int
    usuario: str
    nombre: str
    apellido: str
    email: str
    total_puntos: int

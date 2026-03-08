"""Schemas para tabla de posiciones."""
from pydantic import BaseModel


class PosicionResponse(BaseModel):
    posicion: int
    usuario_id: int
    usuario: str
    nombre: str
    apellido: str
    total_puntos: int
    partidos_exactos: int
    partidos_tendencia: int

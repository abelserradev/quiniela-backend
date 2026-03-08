"""Schemas para partidos."""
from datetime import datetime

from pydantic import BaseModel


class PartidoResponse(BaseModel):
    id: int
    equipo_local: str
    equipo_visitante: str
    fecha_hora: datetime
    goles_local: int | None
    goles_visitante: int | None
    estado: str
    fase: str | None

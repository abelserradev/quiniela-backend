"""Schemas para puntuación."""
from pydantic import BaseModel


class RecalcularResponse(BaseModel):
    partidos_procesados: int
    predicciones_actualizadas: int

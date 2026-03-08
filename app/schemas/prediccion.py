"""Schemas para predicciones de quiniela."""
from pydantic import BaseModel, Field


class PrediccionRequest(BaseModel):
    partido_id: int
    prediccion_local: int = Field(..., ge=0, le=20)
    prediccion_visitante: int = Field(..., ge=0, le=20)


class PrediccionResponse(BaseModel):
    id: int
    partido_id: int
    prediccion_local: int
    prediccion_visitante: int
    puntos_obtenidos: int

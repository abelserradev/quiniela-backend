from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import obtener_usuario_actual
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.puntuacion import RecalcularResponse
from app.services.calculo_puntos import procesar_partidos_finalizados

router = APIRouter(prefix="/puntuacion", tags=["puntuacion"])


@router.post("/recalcular", response_model=RecalcularResponse)
def recalcular_puntuacion(
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    # TODO: Proteger con rol admin en producción
    partidos_procesados, predicciones_actualizadas = procesar_partidos_finalizados(db)
    return RecalcularResponse(
        partidos_procesados=partidos_procesados,
        predicciones_actualizadas=predicciones_actualizadas,
    )
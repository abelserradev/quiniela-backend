from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import obtener_usuario_actual
from app.core.database import get_db
from app.models.partido import Partido
from app.models.prediccion import Prediccion
from app.models.usuario import Usuario
from app.schemas.prediccion import PrediccionRequest, PrediccionResponse

router = APIRouter(prefix="/predicciones", tags=["predicciones"])


def _partido_ya_inicio(partido: Partido) -> bool:
    return partido.estado in ("en_vivo", "finalizado") or (
        partido.fecha_hora.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc)
    )


@router.post("", response_model=PrediccionResponse)
def crear_prediccion(
    body: PrediccionRequest,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    partido = db.get(Partido, body.partido_id)
    if not partido:
        raise HTTPException(status_code=404, detail="Partido no encontrado")
    if _partido_ya_inicio(partido):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El partido ya inició o finalizó, no se puede modificar la predicción",
        )
    stmt = select(Prediccion).where(
        Prediccion.usuario_id == usuario.id,
        Prediccion.partido_id == body.partido_id,
    )
    prediccion = db.execute(stmt).scalar_one_or_none()
    if prediccion:
        prediccion.prediccion_local = body.prediccion_local
        prediccion.prediccion_visitante = body.prediccion_visitante
        db.flush()
    else:
        prediccion = Prediccion(
            usuario_id=usuario.id,
            partido_id=body.partido_id,
            prediccion_local=body.prediccion_local,
            prediccion_visitante=body.prediccion_visitante,
        )
        db.add(prediccion)
        db.flush()
    return PrediccionResponse(
        id=prediccion.id,
        partido_id=prediccion.partido_id,
        prediccion_local=prediccion.prediccion_local,
        prediccion_visitante=prediccion.prediccion_visitante,
        puntos_obtenidos=prediccion.puntos_obtenidos,
    )


@router.get("", response_model=list[PrediccionResponse])
def listar_mis_predicciones(
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    stmt = select(Prediccion).where(Prediccion.usuario_id == usuario.id)
    predicciones = db.execute(stmt).scalars().all()
    return [
        PrediccionResponse(
            id=p.id,
            partido_id=p.partido_id,
            prediccion_local=p.prediccion_local,
            prediccion_visitante=p.prediccion_visitante,
            puntos_obtenidos=p.puntos_obtenidos,
        )
        for p in predicciones
    ]
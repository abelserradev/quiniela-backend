from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.partido import Partido
from app.schemas.partido import PartidoResponse

router = APIRouter(prefix="/partidos", tags=["partidos"])


@router.get("", response_model=list[PartidoResponse])
def listar_partidos(
    estado: Literal["pendiente", "en_vivo", "finalizado"] | None = None,
    fase: str | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(Partido).order_by(Partido.fecha_hora)
    if estado:
        stmt = stmt.where(Partido.estado == estado)
    if fase:
        stmt = stmt.where(Partido.fase == fase)
    partidos = db.execute(stmt).scalars().all()
    return [
        PartidoResponse(
            id=p.id,
            equipo_local=p.equipo_local,
            equipo_visitante=p.equipo_visitante,
            fecha_hora=p.fecha_hora,
            goles_local=p.goles_local,
            goles_visitante=p.goles_visitante,
            estado=p.estado,
            fase=p.fase,
        )
        for p in partidos
    ]


@router.get("/{partido_id}", response_model=PartidoResponse)
def obtener_partido(
    partido_id: int,
    db: Session = Depends(get_db),
):
    partido = db.get(Partido, partido_id)
    if not partido:
        raise HTTPException(status_code=404, detail="Partido no encontrado")
    return PartidoResponse(
        id=partido.id,
        equipo_local=partido.equipo_local,
        equipo_visitante=partido.equipo_visitante,
        fecha_hora=partido.fecha_hora,
        goles_local=partido.goles_local,
        goles_visitante=partido.goles_visitante,
        estado=partido.estado,
        fase=partido.fase,
    )
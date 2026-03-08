from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.prediccion import Prediccion
from app.models.usuario import Usuario
from app.schemas.tabla import PosicionResponse

router = APIRouter(prefix="/tabla", tags=["tabla"])


@router.get("", response_model=list[PosicionResponse])
def obtener_tabla(
    limite: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    stmt = (
        select(Usuario)
        .order_by(Usuario.total_puntos.desc())
        .limit(limite)
    )
    usuarios = db.execute(stmt).scalars().all()
    resultado = []
    for pos, u in enumerate(usuarios, start=1):
        exactos = db.execute(
            select(func.count(Prediccion.id)).where(
                Prediccion.usuario_id == u.id,
                Prediccion.puntos_obtenidos == 3,
            )
        ).scalar() or 0
        tendencia = db.execute(
            select(func.count(Prediccion.id)).where(
                Prediccion.usuario_id == u.id,
                Prediccion.puntos_obtenidos == 1,
            )
        ).scalar() or 0
        resultado.append(
            PosicionResponse(
                posicion=pos,
                usuario_id=u.id,
                usuario=u.usuario,
                nombre=u.nombre,
                apellido=u.apellido,
                total_puntos=u.total_puntos,
                partidos_exactos=exactos,
                partidos_tendencia=tendencia,
            )
        )
    return resultado
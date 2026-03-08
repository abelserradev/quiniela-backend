from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.historial_puntos import HistorialPuntos
from app.models.partido import Partido
from app.models.prediccion import Prediccion
from app.models.usuario import Usuario

PUNTOS_EXACTO = 3
PUNTOS_TENDENCIA = 1


def calcular_puntos(
    goles_local: int,
    goles_visitante: int,
    pred_local: int,
    pred_visitante: int,
) -> int:
    """Calcula puntos según resultado real vs predicción.
    Acierto exacto: mismo marcador.
    Acierto tendencia: mismo ganador/empate.
    """
    if goles_local == pred_local and goles_visitante == pred_visitante:
        return PUNTOS_EXACTO
    resultado_real = (goles_local > goles_visitante) - (goles_local < goles_visitante)
    resultado_pred = (pred_local > pred_visitante) - (pred_local < pred_visitante)
    if resultado_real == resultado_pred:
        return PUNTOS_TENDENCIA
    return 0


def procesar_partido_finalizado(
    db: Session,
    partido: Partido,
) -> int:
    """Procesa un partido finalizado: actualiza predicciones, usuarios e historial.
    Retorna cantidad de predicciones actualizadas.
    """
    if partido.goles_local is None or partido.goles_visitante is None:
        return 0
    stmt = select(Prediccion).where(Prediccion.partido_id == partido.id)
    predicciones = db.execute(stmt).scalars().all()
    actualizadas = 0
    for pred in predicciones:
        if pred.puntos_obtenidos > 0:
            continue
        pts = calcular_puntos(
            partido.goles_local,
            partido.goles_visitante,
            pred.prediccion_local,
            pred.prediccion_visitante,
        )
        pred.puntos_obtenidos = pts
        actualizadas += 1
        usuario = db.get(Usuario, pred.usuario_id)
        if usuario:
            usuario.total_puntos += pts
        db.add(
            HistorialPuntos(
                usuario_id=pred.usuario_id,
                partido_id=partido.id,
                puntos=pts,
            )
        )
    db.flush()
    return actualizadas


def procesar_partidos_finalizados(db: Session) -> tuple[int, int]:
    """Procesa todos los partidos finalizados pendientes de puntuación.
    Retorna (partidos_procesados, predicciones_actualizadas).
    """
    stmt = select(Partido).where(Partido.estado == "finalizado")
    partidos = db.execute(stmt).scalars().all()
    total_preds = 0
    for partido in partidos:
        total_preds += procesar_partido_finalizado(db, partido)
    return len(partidos), total_preds
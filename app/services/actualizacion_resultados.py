#toca revisar la logica de este cron para saber si se usa api externa o no
import logging
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.partido import Partido
from app.services.calculo_puntos import procesar_partido_finalizado, procesar_partidos_finalizados

logger = logging.getLogger(__name__)


def _obtener_partidos_api() -> list[dict[str, Any]]:
    """Consulta API-Football (o similar) por partidos finalizados.
    TODO: Adaptar a la API real; estructura de ejemplo.
    """
    settings = get_settings()
    api_key = getattr(settings, "api_football_key", None)
    if not api_key:
        logger.debug("api_football_key no configurada, omitiendo fetch externo")
        return []
    base_url = getattr(settings, "api_football_base_url", "https://v3.football.api-sports.io")
    url = f"{base_url}/fixtures"
    params = {"league": 1, "season": 2026}
    headers = {"x-apisports-key": api_key}
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", [])
    except Exception as e:
        logger.warning("Error al consultar API externa: %s", e)
        return []


def _mapear_resultado_api(fixture: dict[str, Any]) -> dict[str, Any] | None:
    """Extrae equipo_local, equipo_visitante, goles, fecha de un fixture.
    Adaptar según estructura real de la API.
    """
    try:
        teams = fixture.get("teams", {})
        goals = fixture.get("goals", {})
        goles_local = goals.get("home")
        goles_visitante = goals.get("away")
        if goles_local is None or goles_visitante is None:
            return None
        return {
            "equipo_local": teams.get("home", {}).get("name", ""),
            "equipo_visitante": teams.get("away", {}).get("name", ""),
            "goles_local": int(goles_local),
            "goles_visitante": int(goles_visitante),
            "fecha": fixture.get("fixture", {}).get("date"),
        }
    except (TypeError, ValueError, KeyError):
        return None


def _actualizar_partido_desde_api(db: Session, partido: Partido, datos: dict[str, Any]) -> bool:
    """Actualiza un partido con resultado de la API si coincide."""
    partido.goles_local = datos["goles_local"]
    partido.goles_visitante = datos["goles_visitante"]
    partido.estado = "finalizado"
    db.flush()
    return True


def ejecutar_actualizacion_resultados() -> dict[str, int]:
    """Flujo completo: fetch API → actualizar partidos → recalcular puntos.
    Pensado para CRON. Retorna estadísticas.
    """
    db = SessionLocal()
    try:
        partidos_api = _obtener_partidos_api()
        partidos_actualizados = 0
        predicciones_actualizadas = 0
        if partidos_api:
            for fixture in partidos_api:
                datos = _mapear_resultado_api(fixture)
                if not datos:
                    continue
                stmt = select(Partido).where(
                    Partido.equipo_local == datos["equipo_local"],
                    Partido.equipo_visitante == datos["equipo_visitante"],
                )
                partido = db.execute(stmt).scalar_one_or_none()
                if partido and partido.estado != "finalizado":
                    _actualizar_partido_desde_api(db, partido, datos)
                    partidos_actualizados += 1
                    predicciones_actualizadas += procesar_partido_finalizado(db, partido)
        else:
            partidos, preds = procesar_partidos_finalizados(db)
            partidos_actualizados = partidos
            predicciones_actualizadas = preds
        db.commit()
        return {
            "partidos_actualizados": partidos_actualizados,
            "predicciones_actualizadas": predicciones_actualizadas,
        }
    except Exception as e:
        db.rollback()
        logger.exception("Error en actualizacion_resultados: %s", e)
        raise
    finally:
        db.close()
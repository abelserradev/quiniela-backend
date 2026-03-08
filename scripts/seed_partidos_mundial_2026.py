"""Seed: partidos de la Copa Mundial FIFA 2026.
Fuente: FIFA, Sporting News, Olympics.com (sorteo 5 dic 2025).
12 grupos A-L, fase de grupos 11-27 jun 2026. Repechajes como 'Por definir'.
"""
from datetime import datetime

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.partido import Partido

TBD = "Por definir"

# Partidos por grupo: orden exacto FIFA (local, visitante)
# Matchday 1: (1v2, 3v4), Matchday 2: (4v2, 1v3), Matchday 3: (4v1, 2v3)
FIXTURES = [
    ("México", "Sudáfrica"),
    ("Corea del Sur", TBD),
    (TBD, "Sudáfrica"),
    ("México", "Corea del Sur"),
    (TBD, "México"),
    ("Sudáfrica", "Corea del Sur"),
]
FIXTURES_B = [
    ("Canadá", TBD),
    ("Catar", "Suiza"),
    (TBD, "Suiza"),
    ("Canadá", "Catar"),
    ("Suiza", "Canadá"),
    (TBD, "Catar"),
]
FIXTURES_C = [
    ("Brasil", "Marruecos"),
    ("Haití", "Escocia"),
    ("Escocia", "Marruecos"),
    ("Brasil", "Haití"),
    ("Escocia", "Brasil"),
    ("Marruecos", "Haití"),
]
FIXTURES_D = [
    ("Estados Unidos", "Paraguay"),
    ("Australia", TBD),
    ("Estados Unidos", "Australia"),
    (TBD, "Paraguay"),
    (TBD, "Estados Unidos"),
    ("Paraguay", "Australia"),
]
FIXTURES_E = [
    ("Alemania", "Curazao"),
    ("Costa de Marfil", "Ecuador"),
    ("Alemania", "Costa de Marfil"),
    ("Ecuador", "Curazao"),
    ("Ecuador", "Alemania"),
    ("Curazao", "Costa de Marfil"),
]
FIXTURES_F = [
    ("Países Bajos", "Japón"),
    (TBD, "Túnez"),
    ("Países Bajos", TBD),
    ("Túnez", "Japón"),
    ("Túnez", "Países Bajos"),
    ("Japón", TBD),
]
FIXTURES_G = [
    ("Bélgica", "Egipto"),
    ("Irán", "Nueva Zelanda"),
    ("Bélgica", "Irán"),
    ("Nueva Zelanda", "Egipto"),
    ("Nueva Zelanda", "Bélgica"),
    ("Egipto", "Irán"),
]
FIXTURES_H = [
    ("España", "Cabo Verde"),
    ("Arabia Saudita", "Uruguay"),
    ("España", "Arabia Saudita"),
    ("Uruguay", "Cabo Verde"),
    ("Uruguay", "España"),
    ("Cabo Verde", "Arabia Saudita"),
]
FIXTURES_I = [
    ("Francia", "Senegal"),
    (TBD, "Noruega"),
    ("Francia", TBD),
    ("Noruega", "Senegal"),
    ("Noruega", "Francia"),
    ("Senegal", TBD),
]
FIXTURES_J = [
    ("Argentina", "Argelia"),
    ("Austria", "Jordania"),
    ("Argentina", "Austria"),
    ("Jordania", "Argelia"),
    ("Jordania", "Argentina"),
    ("Argelia", "Austria"),
]
FIXTURES_K = [
    ("Portugal", TBD),
    ("Uzbekistán", "Colombia"),
    ("Portugal", "Uzbekistán"),
    ("Colombia", TBD),
    ("Colombia", "Portugal"),
    (TBD, "Uzbekistán"),
]
FIXTURES_L = [
    ("Inglaterra", "Croacia"),
    ("Ghana", "Panamá"),
    ("Inglaterra", "Ghana"),
    ("Panamá", "Croacia"),
    ("Panamá", "Inglaterra"),
    ("Croacia", "Ghana"),
]

FIXTURES_POR_GRUPO = {
    "A": FIXTURES,
    "B": FIXTURES_B,
    "C": FIXTURES_C,
    "D": FIXTURES_D,
    "E": FIXTURES_E,
    "F": FIXTURES_F,
    "G": FIXTURES_G,
    "H": FIXTURES_H,
    "I": FIXTURES_I,
    "J": FIXTURES_J,
    "K": FIXTURES_K,
    "L": FIXTURES_L,
}

# Fechas por grupo (año, mes, día) - 2 partidos por fecha
FECHAS = {
    "A": [(2026, 6, 11), (2026, 6, 18), (2026, 6, 24)],
    "B": [(2026, 6, 12), (2026, 6, 18), (2026, 6, 24)],
    "C": [(2026, 6, 13), (2026, 6, 19), (2026, 6, 24)],
    "D": [(2026, 6, 12), (2026, 6, 19), (2026, 6, 25)],
    "E": [(2026, 6, 14), (2026, 6, 20), (2026, 6, 25)],
    "F": [(2026, 6, 14), (2026, 6, 20), (2026, 6, 25)],
    "G": [(2026, 6, 15), (2026, 6, 21), (2026, 6, 26)],
    "H": [(2026, 6, 15), (2026, 6, 21), (2026, 6, 26)],
    "I": [(2026, 6, 16), (2026, 6, 22), (2026, 6, 26)],
    "J": [(2026, 6, 16), (2026, 6, 22), (2026, 6, 27)],
    "K": [(2026, 6, 17), (2026, 6, 23), (2026, 6, 27)],
    "L": [(2026, 6, 17), (2026, 6, 23), (2026, 6, 27)],
}


def run():
    db = SessionLocal()
    try:
        existentes = db.execute(select(Partido)).scalars().all()
        if existentes:
            print(f"Ya existen {len(existentes)} partidos. Omitiendo seed.")
            return
        creados = 0
        for grupo in "ABCDEFGHIJKL":
            fase = f"Grupo {grupo}"
            fixtures = FIXTURES_POR_GRUPO[grupo]
            fechas = FECHAS[grupo]
            for i, (local, visitante) in enumerate(fixtures):
                y, m, d = fechas[i // 2]
                hora = 18 if i % 2 == 0 else 21
                fecha_hora = datetime(y, m, d, hora, 0)
                p = Partido(
                    equipo_local=local,
                    equipo_visitante=visitante,
                    fecha_hora=fecha_hora,
                    estado="pendiente",
                    fase=fase,
                )
                db.add(p)
                creados += 1
        db.commit()
        print(f"Seed completado: {creados} partidos (fase de grupos FIFA 2026).")
    finally:
        db.close()


if __name__ == "__main__":
    run()

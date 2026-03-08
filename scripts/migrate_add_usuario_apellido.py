"""Migración: añade columnas usuario y apellido a usuarios.
Ejecutar si la tabla ya existe: cd backend && python -m scripts.migrate_add_usuario_apellido
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from app.core.database import engine


def run():
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS usuario VARCHAR(50)"))
        conn.execute(text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS apellido VARCHAR(100)"))
        conn.execute(text("""
            UPDATE usuarios SET
                usuario = COALESCE(NULLIF(TRIM(usuario), ''), 'user_' || id),
                apellido = COALESCE(NULLIF(TRIM(apellido), ''), '')
            WHERE usuario IS NULL OR usuario = '' OR apellido IS NULL OR apellido = ''
        """))
        conn.execute(text("ALTER TABLE usuarios ALTER COLUMN usuario SET NOT NULL"))
        conn.execute(text("ALTER TABLE usuarios ALTER COLUMN apellido SET DEFAULT ''"))
        conn.execute(text("ALTER TABLE usuarios ALTER COLUMN apellido SET NOT NULL"))
        conn.execute(text(
            "CREATE UNIQUE INDEX IF NOT EXISTS ix_usuarios_usuario ON usuarios(usuario)"
        ))
    print("Migración completada")


if __name__ == "__main__":
    run()

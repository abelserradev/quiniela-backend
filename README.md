# Quiniela Mundial 2026 — Backend API

API REST para la quiniela de fútbol del Mundial 2026. FastAPI, SQLAlchemy, PostgreSQL.

## Requisitos

- Python 3.12+
- PostgreSQL 16+

## Instalación local

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Variables de entorno

Crear `.env` en la raíz del backend (no subir al repo):

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | URL de PostgreSQL | `postgresql://user:pass@localhost:5432/quiniela` |
| `JWT_SECRET_KEY` | Clave para JWT (mín. 32 caracteres) | — |
| `ENVIRONMENT` | `development` o `production` | `development` |
| `DEBUG` | Modo debug | `true` / `false` |
| `CORS_ORIGINS` | Orígenes permitidos (separados por coma) | `http://localhost:3000` |
| `POSTGRES_USER` | Usuario PostgreSQL (Docker) | — |
| `POSTGRES_PASSWORD` | Contraseña PostgreSQL (Docker) | — |
| `POSTGRES_DB` | Nombre de la base (Docker) | `quiniela` |
| `DB_PORT` | Puerto expuesto en host (Docker) | `5433` |

## Ejecución local

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API: http://localhost:8000  
Docs: http://localhost:8000/docs

## Docker

### Desarrollo

```bash
cd backend
docker compose -f docker-compose.dev.yml up --build
```

- PostgreSQL en puerto `DB_PORT` (ej. 5433 si 5432 está ocupado)
- Backend en 8000 con hot-reload

### Producción

```bash
cd backend
docker compose -f docker-compose.prod.yml up -d --build
```

- Sin volúmenes de código; usuario no-root
- 2 workers Uvicorn

## Estructura

```
backend/
├── app/
│   ├── api/endpoints/   # auth, partidos, predicciones, puntuacion, tabla, users
│   ├── core/            # config, database, security
│   ├── models/          # partido, prediccion, usuario, historial_puntos
│   ├── schemas/         # Pydantic
│   └── services/        # calculo_puntos, actualizacion_resultados
├── main.py
├── Dockerfile           # multi-stage: development | production
├── docker-compose.dev.yml
└── docker-compose.prod.yml
```

## Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/auth/login` | Login (cookie HttpOnly) |
| POST | `/api/auth/registro` | Registro |
| GET | `/api/partidos` | Listar partidos |
| GET | `/api/partidos/{id}` | Detalle partido |
| POST | `/api/predicciones` | Crear/actualizar predicción |
| GET | `/api/puntuacion` | Puntuación del usuario |
| GET | `/api/tabla` | Tabla de posiciones |

## Tareas programadas

- **Actualización de resultados**: cada 10 min (APScheduler). Actualiza goles y recalcula puntuaciones.

## Seguridad

- Mensajes genéricos en auth (no revelar si email existe o contraseña incorrecta)
- JWT en cookie HttpOnly
- CORS configurado por `CORS_ORIGINS`
- Cabeceras de seguridad (X-Content-Type-Options, X-Frame-Options, etc.)

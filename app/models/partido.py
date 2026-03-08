from datetime import datetime
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
class Partido(Base):
    __tablename__ = "partidos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipo_local: Mapped[str] = mapped_column(String(100), nullable=False)
    equipo_visitante: Mapped[str] = mapped_column(String(100), nullable=False)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    goles_local: Mapped[int | None] = mapped_column(Integer, nullable=True)
    goles_visitante: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente", nullable=False)
    fase: Mapped[str | None] = mapped_column(String(50), nullable=True)
    predicciones = relationship("Prediccion", back_populates="partido", lazy="selectin")
    historial_puntos = relationship("HistorialPuntos", back_populates="partido", lazy="selectin")
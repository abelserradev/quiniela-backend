from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
class HistorialPuntos(Base):
    __tablename__ = "historial_puntos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    partido_id: Mapped[int] = mapped_column(ForeignKey("partidos.id"), nullable=False)
    puntos: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    usuario = relationship("Usuario", back_populates="historial_puntos")
    partido = relationship("Partido", back_populates="historial_puntos")
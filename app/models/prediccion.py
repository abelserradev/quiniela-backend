from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
class Prediccion(Base):
    __tablename__ = "predicciones"
    __table_args__ = (UniqueConstraint("usuario_id", "partido_id", name="uq_usuario_partido"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    partido_id: Mapped[int] = mapped_column(ForeignKey("partidos.id"), nullable=False)
    prediccion_local: Mapped[int] = mapped_column(Integer, nullable=False)
    prediccion_visitante: Mapped[int] = mapped_column(Integer, nullable=False)
    puntos_obtenidos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    usuario = relationship("Usuario", back_populates="predicciones")
    partido = relationship("Partido", back_populates="predicciones")
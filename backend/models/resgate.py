from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.usuario import Usuario
    from models.recompensa import Recompensa


class Resgate(Base):
    __tablename__ = "resgates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    recompensa_id: Mapped[int] = mapped_column(ForeignKey("recompensas.id"), nullable=False)
    pontos_gastos: Mapped[int] = mapped_column(Integer, nullable=False)
    resgatado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    usuario: Mapped["Usuario"] = relationship(back_populates="resgates")
    recompensa: Mapped["Recompensa"] = relationship(back_populates="resgates")

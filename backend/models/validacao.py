from sqlalchemy import String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.usuario import Usuario
    from models.denuncia import Denuncia

class Validacao(Base):
    __tablename__ = "validacoes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    denuncia_id: Mapped[int] = mapped_column(ForeignKey("denuncias.id"), nullable=False)
    tipo_validacao: Mapped[str] = mapped_column(String(20), default="ainda_sujo")
    data: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    usuario: Mapped["Usuario"] = relationship(back_populates="validacoes")
    denuncia: Mapped["Denuncia"] = relationship(back_populates="validacoes")
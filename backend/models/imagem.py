from sqlalchemy import String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.denuncia import Denuncia

class Imagem(Base):
    __tablename__ = "imagens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    denuncia_id: Mapped[int] = mapped_column(ForeignKey("denuncias.id"), nullable=False)
    url_imagem: Mapped[str] = mapped_column(String(255), unique=True)
    enviada_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    denuncia: Mapped["Denuncia"] = relationship(back_populates="imagens")
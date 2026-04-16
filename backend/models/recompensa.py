from sqlalchemy import String, Integer, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.resgate import Resgate


class Recompensa(Base):
    __tablename__ = "recompensas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    pontos_necessarios: Mapped[int] = mapped_column(Integer, nullable=False)
    estoque: Mapped[int] = mapped_column(Integer, default=10)
    imagem_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criada_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    resgates: Mapped[list["Resgate"]] = relationship(back_populates="recompensa")

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.denuncia import Denuncia
    from models.validacao import Validacao
    from models.resgate import Resgate

class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(125), nullable=False)
    email: Mapped[str] = mapped_column(String(125), nullable=False, unique=True)
    senha: Mapped[str] = mapped_column(String(255), nullable=False)
    pontos: Mapped[int] = mapped_column(default=0)
    papel: Mapped[str] = mapped_column(String(10), default="morador")
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    denuncias: Mapped[list["Denuncia"]] = relationship(back_populates="usuario")
    validacoes: Mapped[list["Validacao"]] = relationship(back_populates="usuario")
    resgates: Mapped[list["Resgate"]] = relationship(back_populates="usuario")
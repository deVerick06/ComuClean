from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.usuario import Usuario
    from models.imagem import Imagem
    from models.validacao import Validacao

class Denuncia(Base):
    __tablename__= "denuncias"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey('usuarios.id'), nullable=False)
    tipo_lixo: Mapped[str] = mapped_column(String(20), nullable=False)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="aberta", nullable=False)
    criada_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    usuario: Mapped["Usuario"] = relationship(back_populates="denuncias")
    imagens: Mapped[list["Imagem"]] = relationship(back_populates="denuncia")
    validacoes: Mapped[list["Validacao"]] = relationship(back_populates="denuncia")
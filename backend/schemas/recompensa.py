from pydantic import BaseModel
from datetime import datetime


class RecompensaResponse(BaseModel):
    id: int
    nome: str
    descricao: str | None
    pontos_necessarios: int
    estoque: int
    imagem_url: str | None
    ativo: bool
    criada_em: datetime

    class Config:
        from_attributes = True

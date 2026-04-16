from pydantic import BaseModel
from datetime import datetime
from typing import Literal


class ValidacaoCreate(BaseModel):
    denuncia_id: int
    tipo_validacao: Literal["ainda_sujo", "ja_limpo"]
    latitude: float | None = None
    longitude: float | None = None


class ValidacaoResponse(BaseModel):
    id: int
    denuncia_id: int
    tipo_validacao: str
    imagem_url: str | None
    data: datetime

    class Config:
        from_attributes = True

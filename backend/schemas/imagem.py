from pydantic import BaseModel
from datetime import datetime


class ImagemResponse(BaseModel):
    id: int
    denuncia_id: int
    url_imagem: str
    enviada_em: datetime

    class Config:
        from_attributes = True

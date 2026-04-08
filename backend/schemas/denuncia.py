from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DenunciaCreate(BaseModel):
    tipo_lixo: str
    latitude: float
    longitude: float
    descricao: Optional[str] = None

class DenunciaResponse(BaseModel):
    id: int
    usuario_id: int
    tipo_lixo: str
    latitude: float
    longitude: float
    descricao: Optional[str] = None
    status: str
    criada_em: datetime

    class Config:
        from_attributes = True
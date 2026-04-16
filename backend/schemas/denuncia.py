from pydantic import BaseModel
from datetime import datetime
from typing import Literal


class DenunciaCreate(BaseModel):
    tipo_lixo: Literal["lixo_comum", "entulho", "reciclavel"]
    latitude: float
    longitude: float
    descricao: str | None = None


class DenunciaResponse(BaseModel):
    id: int
    tipo_lixo: str
    latitude: float
    longitude: float
    descricao: str | None
    status: str
    criada_em: datetime
    total_urgentes: int = 0
    total_resolvidos: int = 0


class DenunciaStatusUpdate(BaseModel):
    status: Literal["aberta", "em_analise", "resolvida"]


class DenunciaAdminResponse(BaseModel):
    id: int
    tipo_lixo: str
    latitude: float
    longitude: float
    descricao: str | None
    status: str
    criada_em: datetime

    class Config:
        from_attributes = True

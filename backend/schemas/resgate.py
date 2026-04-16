from pydantic import BaseModel
from datetime import datetime


class ResgateResponse(BaseModel):
    id: int
    recompensa_id: int
    pontos_gastos: int
    resgatado_em: datetime
    recompensa_nome: str

    class Config:
        from_attributes = True

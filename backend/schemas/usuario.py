from pydantic import BaseModel, EmailStr
from datetime import datetime

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str

class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    pontos: int
    papel: str
    criado_em: datetime

    class Config:
        from_attributes = True
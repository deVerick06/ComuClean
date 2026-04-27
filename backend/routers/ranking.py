from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import hashlib

from core.database import get_db
from models.usuario import Usuario
from schemas.usuario import UsuarioRankingResponse

router = APIRouter(tags=["Ranking"])

def gerar_nome_anonimo(email: str) -> str:
    codigo = hashlib.md5(email.encode()).hexdigest()[:6].upper()
    return f"Cidadão-{codigo}"

@router.get("/ranking", response_model=list[UsuarioRankingResponse])
async def ranking(
    limite: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Usuario)
        .where(Usuario.papel != "admin")
        .order_by(Usuario.pontos.desc())
        .limit(limite)
    )
    usuarios = result.scalars().all()

    return [
        UsuarioRankingResponse(
            posicao=i + 1,
            nome=gerar_nome_anonimo(u.email),
            pontos=u.pontos,
        )
        for i, u in enumerate(usuarios)
    ]
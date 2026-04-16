from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.deps import get_current_user
from models.usuario import Usuario
from models.recompensa import Recompensa
from models.resgate import Resgate
from schemas.recompensa import RecompensaResponse
from schemas.resgate import ResgateResponse

router = APIRouter(tags=["Recompensas"])


@router.get("/recompensas", response_model=list[RecompensaResponse])
async def listar_recompensas(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Recompensa)
        .where(Recompensa.ativo == True, Recompensa.estoque > 0)
        .order_by(Recompensa.pontos_necessarios.asc())
    )
    return result.scalars().all()


@router.post(
    "/recompensas/{recompensa_id}/resgatar",
    response_model=ResgateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def resgatar_recompensa(
    recompensa_id: int,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    result = await db.execute(
        select(Recompensa).where(Recompensa.id == recompensa_id)
    )
    recompensa = result.scalar_one_or_none()

    if not recompensa:
        raise HTTPException(status_code=404, detail="Recompensa nao encontrada")

    if not recompensa.ativo:
        raise HTTPException(status_code=400, detail="Recompensa indisponivel")

    if recompensa.estoque <= 0:
        raise HTTPException(status_code=400, detail="Estoque esgotado")

    if usuario.pontos < recompensa.pontos_necessarios:
        raise HTTPException(
            status_code=400,
            detail=f"Pontos insuficientes (necessario: {recompensa.pontos_necessarios}, disponivel: {usuario.pontos})",
        )

    usuario.pontos -= recompensa.pontos_necessarios
    recompensa.estoque -= 1

    resgate = Resgate(
        usuario_id=usuario.id,
        recompensa_id=recompensa.id,
        pontos_gastos=recompensa.pontos_necessarios,
    )
    db.add(resgate)
    await db.commit()
    await db.refresh(resgate)

    return ResgateResponse(
        id=resgate.id,
        recompensa_id=resgate.recompensa_id,
        pontos_gastos=resgate.pontos_gastos,
        resgatado_em=resgate.resgatado_em,
        recompensa_nome=recompensa.nome,
    )

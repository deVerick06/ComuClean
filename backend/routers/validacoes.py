from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.deps import get_current_user
from core.geo import haversine, RAIO_MAXIMO_METROS
from models.usuario import Usuario
from models.denuncia import Denuncia
from models.validacao import Validacao
from schemas.validacao import ValidacaoCreate, ValidacaoResponse
import os
import uuid

router = APIRouter(tags=["Validacoes"])

VOTOS_PARA_RESOLVER = 3
PONTOS_POR_DENUNCIA_RESOLVIDA = 10
UPLOAD_DIR = "uploads"


@router.post("/validacoes", response_model=ValidacaoResponse, status_code=status.HTTP_201_CREATED)
async def criar_validacao(
    dados: ValidacaoCreate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Denuncia).where(Denuncia.id == dados.denuncia_id))
    denuncia = result.scalar_one_or_none()
    if not denuncia:
        raise HTTPException(status_code=404, detail="Denuncia nao encontrada")

    if denuncia.status == "resolvida":
        raise HTTPException(status_code=400, detail="Denuncia ja foi resolvida")

    if denuncia.usuario_id == usuario.id:
        raise HTTPException(status_code=400, detail="Voce nao pode validar sua propria denuncia")

    ja_votou = await db.execute(
        select(Validacao).where(
            Validacao.usuario_id == usuario.id,
            Validacao.denuncia_id == dados.denuncia_id,
        )
    )
    if ja_votou.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Voce ja validou esta denuncia")

    # Para "ja_limpo" exige coordenadas e verifica proximidade
    if dados.tipo_validacao == "ja_limpo":
        if dados.latitude is None or dados.longitude is None:
            raise HTTPException(
                status_code=400,
                detail="Coordenadas obrigatorias para marcar como resolvido",
            )
        distancia = haversine(
            denuncia.latitude, denuncia.longitude,
            dados.latitude, dados.longitude,
        )
        if distancia > RAIO_MAXIMO_METROS:
            raise HTTPException(
                status_code=400,
                detail=f"Voce precisa estar a no maximo {RAIO_MAXIMO_METROS}m do local ({distancia:.0f}m detectados)",
            )

    validacao = Validacao(
        usuario_id=usuario.id,
        denuncia_id=dados.denuncia_id,
        tipo_validacao=dados.tipo_validacao,
        latitude=dados.latitude,
        longitude=dados.longitude,
    )
    db.add(validacao)

    # Regra: 3 votos "ja_limpo" → resolve + credita pontos
    if dados.tipo_validacao == "ja_limpo":
        contagem = await db.execute(
            select(func.count()).select_from(Validacao).where(
                Validacao.denuncia_id == dados.denuncia_id,
                Validacao.tipo_validacao == "ja_limpo",
            )
        )
        total_limpo = contagem.scalar() + 1

        if total_limpo >= VOTOS_PARA_RESOLVER:
            denuncia.status = "resolvida"
            result_autor = await db.execute(
                select(Usuario).where(Usuario.id == denuncia.usuario_id)
            )
            autor = result_autor.scalar_one()
            autor.pontos += PONTOS_POR_DENUNCIA_RESOLVIDA

    await db.commit()
    await db.refresh(validacao)
    return validacao


@router.post(
    "/validacoes/{validacao_id}/imagem",
    response_model=ValidacaoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_prova(
    validacao_id: int,
    arquivo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Validacao).where(Validacao.id == validacao_id))
    validacao = result.scalar_one_or_none()

    if not validacao:
        raise HTTPException(status_code=404, detail="Validacao nao encontrada")

    if validacao.usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="Sem permissao")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(arquivo.filename or "img.jpg")[1]
    nome = f"prova_{uuid.uuid4().hex}{ext}"
    caminho = os.path.join(UPLOAD_DIR, nome)

    conteudo = await arquivo.read()
    with open(caminho, "wb") as f:
        f.write(conteudo)

    validacao.imagem_url = f"/{UPLOAD_DIR}/{nome}"
    await db.commit()
    await db.refresh(validacao)
    return validacao

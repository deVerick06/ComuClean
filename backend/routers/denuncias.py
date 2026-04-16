from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
from sqlalchemy import select, func, cast, Date, case
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime
from core.database import get_db
from core.deps import get_current_user, get_admin_user
from models.usuario import Usuario
from models.denuncia import Denuncia
from models.imagem import Imagem
from models.validacao import Validacao
from schemas.denuncia import DenunciaCreate, DenunciaResponse, DenunciaStatusUpdate, DenunciaAdminResponse
from schemas.imagem import ImagemResponse
import os
import uuid

router = APIRouter(tags=["Denúncias"])

UPLOAD_DIR = "uploads"
LIMITE_DIARIO_DENUNCIAS = 5
PONTOS_POR_DENUNCIA_CRIADA = 5
EXTENSOES_PERMITIDAS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_TAMANHO_ARQUIVO = 5 * 1024 * 1024  # 5MB


@router.post("/denuncias", response_model=DenunciaResponse, status_code=status.HTTP_201_CREATED)
async def criar_denuncia(
    dados: DenunciaCreate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    # Controle de spam: limite diário
    contagem = await db.execute(
        select(func.count()).select_from(Denuncia).where(
            Denuncia.usuario_id == usuario.id,
            cast(Denuncia.criada_em, Date) == date.today(),
        )
    )
    total_hoje = contagem.scalar()
    if total_hoje >= LIMITE_DIARIO_DENUNCIAS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Limite de {LIMITE_DIARIO_DENUNCIAS} denúncias por dia atingido",
        )

    denuncia = Denuncia(
        usuario_id=usuario.id,
        tipo_lixo=dados.tipo_lixo,
        latitude=dados.latitude,
        longitude=dados.longitude,
        descricao=dados.descricao,
    )
    db.add(denuncia)

    # Gamificacao: +5 pontos por criar denuncia
    usuario.pontos += PONTOS_POR_DENUNCIA_CRIADA

    await db.commit()
    await db.refresh(denuncia)
    return denuncia


@router.get("/denuncias", response_model=list[DenunciaResponse])
async def listar_denuncias(
    status_filtro: str | None = Query(None, alias="status"),
    tipo_lixo: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    total_urgentes = func.count(
        case((Validacao.tipo_validacao == "ainda_sujo", 1))
    ).label("total_urgentes")
    total_resolvidos = func.count(
        case((Validacao.tipo_validacao == "ja_limpo", 1))
    ).label("total_resolvidos")

    query = (
        select(Denuncia, total_urgentes, total_resolvidos)
        .outerjoin(Validacao, Validacao.denuncia_id == Denuncia.id)
        .group_by(Denuncia.id)
    )

    if status_filtro:
        query = query.where(Denuncia.status == status_filtro)
    if tipo_lixo:
        query = query.where(Denuncia.tipo_lixo == tipo_lixo)

    query = query.order_by(total_urgentes.desc(), Denuncia.criada_em.desc())
    result = await db.execute(query)

    denuncias = []
    for row in result.all():
        d = row[0]
        denuncias.append(DenunciaResponse(
            id=d.id,
            tipo_lixo=d.tipo_lixo,
            latitude=d.latitude,
            longitude=d.longitude,
            descricao=d.descricao,
            status=d.status,
            criada_em=d.criada_em,
            total_urgentes=row[1],
            total_resolvidos=row[2],
        ))
    return denuncias


@router.get("/denuncias/{denuncia_id}", response_model=DenunciaResponse)
async def obter_denuncia(denuncia_id: int, db: AsyncSession = Depends(get_db)):
    total_urg = func.count(case((Validacao.tipo_validacao == "ainda_sujo", 1))).label("tu")
    total_res = func.count(case((Validacao.tipo_validacao == "ja_limpo", 1))).label("tr")

    result = await db.execute(
        select(Denuncia, total_urg, total_res)
        .outerjoin(Validacao, Validacao.denuncia_id == Denuncia.id)
        .where(Denuncia.id == denuncia_id)
        .group_by(Denuncia.id)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Denuncia nao encontrada")

    d = row[0]
    return DenunciaResponse(
        id=d.id, tipo_lixo=d.tipo_lixo, latitude=d.latitude,
        longitude=d.longitude, descricao=d.descricao, status=d.status,
        criada_em=d.criada_em, total_urgentes=row[1], total_resolvidos=row[2],
    )


@router.patch("/denuncias/{denuncia_id}/status", response_model=DenunciaAdminResponse)
async def atualizar_status(
    denuncia_id: int,
    dados: DenunciaStatusUpdate,
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(get_admin_user),
):
    result = await db.execute(select(Denuncia).where(Denuncia.id == denuncia_id))
    denuncia = result.scalar_one_or_none()
    if not denuncia:
        raise HTTPException(status_code=404, detail="Denúncia não encontrada")

    denuncia.status = dados.status
    await db.commit()
    await db.refresh(denuncia)
    return denuncia


@router.post(
    "/denuncias/{denuncia_id}/imagens",
    response_model=ImagemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_imagem(
    denuncia_id: int,
    arquivo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Denuncia).where(Denuncia.id == denuncia_id))
    denuncia = result.scalar_one_or_none()
    if not denuncia:
        raise HTTPException(status_code=404, detail="Denúncia não encontrada")

    if denuncia.usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="Sem permissao para adicionar imagens nesta denuncia")

    ext = os.path.splitext(arquivo.filename or "img.jpg")[1].lower()
    if ext not in EXTENSOES_PERMITIDAS:
        raise HTTPException(status_code=400, detail="Tipo de arquivo nao permitido. Use: jpg, png ou webp")

    conteudo = await arquivo.read()
    if len(conteudo) > MAX_TAMANHO_ARQUIVO:
        raise HTTPException(status_code=413, detail="Arquivo muito grande. Maximo: 5MB")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    nome_arquivo = f"{uuid.uuid4().hex}{ext}"
    caminho = os.path.join(UPLOAD_DIR, nome_arquivo)

    with open(caminho, "wb") as f:
        f.write(conteudo)

    imagem = Imagem(
        denuncia_id=denuncia_id,
        url_imagem=f"/{UPLOAD_DIR}/{nome_arquivo}",
    )
    db.add(imagem)
    await db.commit()
    await db.refresh(imagem)
    return imagem

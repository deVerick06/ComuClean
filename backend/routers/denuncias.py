from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query
from sqlalchemy import select, func, cast, Date, case
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime
from typing import Literal
import os
import uuid

from core.database import get_db
from core.deps import get_current_user, get_admin_user
from core.uploads import validar_imagem
from models.usuario import Usuario
from models.denuncia import Denuncia
from models.imagem import Imagem
from models.validacao import Validacao
from schemas.denuncia import DenunciaResponse, DenunciaStatusUpdate, DenunciaAdminResponse

router = APIRouter(tags=["Denúncias"])

UPLOAD_DIR = "uploads"
LIMITE_DIARIO_DENUNCIAS = 5
PONTOS_POR_DENUNCIA_CRIADA = 5


@router.post("/denuncias", response_model=DenunciaResponse, status_code=status.HTTP_201_CREATED)
async def criar_denuncia(
    tipo_lixo: Literal["lixo_comum", "entulho", "reciclavel"] = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    descricao: str | None = Form(None),
    arquivo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    ext = os.path.splitext(arquivo.filename or "img.jpg")[1].lower()
    conteudo = await arquivo.read()
    
    # Se a imagem passar de 20MB, o sistema barra aqui e NADA é salvo no banco!
    validar_imagem(conteudo, ext)

    # 2. Controle de spam: limite diário
    contagem = await db.execute(
        select(func.count()).select_from(Denuncia).where(
            Denuncia.usuario_id == usuario.id,
            cast(Denuncia.criada_em, Date) == date.today(),
        )
    )
    if contagem.scalar() >= LIMITE_DIARIO_DENUNCIAS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Limite de {LIMITE_DIARIO_DENUNCIAS} denúncias por dia atingido",
        )

    # 3. Tudo certo! Criamos a Denúncia no banco
    denuncia = Denuncia(
        usuario_id=usuario.id,
        tipo_lixo=tipo_lixo,
        latitude=latitude,
        longitude=longitude,
        descricao=descricao,
    )
    db.add(denuncia)
    await db.flush() # Flush salva no banco para gerar o ID, mas ainda não "comita" em definitivo

    # 4. Salvamos a imagem no disco e associamos ao ID da denúncia
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    nome_arquivo = f"{uuid.uuid4().hex}{ext}"
    caminho = os.path.join(UPLOAD_DIR, nome_arquivo)

    with open(caminho, "wb") as f:
        f.write(conteudo)

    imagem = Imagem(
        denuncia_id=denuncia.id,
        url_imagem=f"/{UPLOAD_DIR}/{nome_arquivo}",
    )
    db.add(imagem)

    # 5. Gamificação e Commit (salva tudo de uma vez de forma segura)
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


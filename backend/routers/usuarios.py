from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.security import hash_senha, verificar_senha, criar_token
from core.deps import get_current_user
from models.usuario import Usuario
from models.denuncia import Denuncia
from models.resgate import Resgate
from models.recompensa import Recompensa
from schemas.usuario import UsuarioCreate, UsuarioLogin, UsuarioResponse, TokenResponse
from schemas.denuncia import DenunciaResponse
from schemas.resgate import ResgateResponse

router = APIRouter(tags=["Usuários"])


@router.post("/usuarios", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def registrar(dados: UsuarioCreate, db: AsyncSession = Depends(get_db)):
    existe = await db.execute(select(Usuario).where(Usuario.email == dados.email))
    if existe.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado",
        )

    usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha=hash_senha(dados.senha),
    )
    db.add(usuario)
    await db.commit()
    await db.refresh(usuario)
    return usuario


@router.post("/login", response_model=TokenResponse)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Usuario).where(Usuario.email == form.username))
    usuario = result.scalar_one_or_none()

    if not usuario or not verificar_senha(form.password, usuario.senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )

    token = criar_token({"sub": str(usuario.id)})
    return TokenResponse(access_token=token)


@router.get("/usuarios/me", response_model=UsuarioResponse)
async def perfil(usuario: Usuario = Depends(get_current_user)):
    return usuario


@router.get("/usuarios/me/denuncias", response_model=list[DenunciaResponse])
async def minhas_denuncias(
    usuario: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Denuncia)
        .where(Denuncia.usuario_id == usuario.id)
        .order_by(Denuncia.criada_em.desc())
    )
    return result.scalars().all()


@router.get("/usuarios/me/resgates", response_model=list[ResgateResponse])
async def meus_resgates(
    usuario: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resgate, Recompensa.nome)
        .join(Recompensa, Resgate.recompensa_id == Recompensa.id)
        .where(Resgate.usuario_id == usuario.id)
        .order_by(Resgate.resgatado_em.desc())
    )
    return [
        ResgateResponse(
            id=row[0].id,
            recompensa_id=row[0].recompensa_id,
            pontos_gastos=row[0].pontos_gastos,
            resgatado_em=row[0].resgatado_em,
            recompensa_nome=row[1],
        )
        for row in result.all()
    ]

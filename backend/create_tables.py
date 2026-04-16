import asyncio
from core.database import engine, Base

from models.usuario import Usuario
from models.denuncia import Denuncia
from models.imagem import Imagem
from models.validacao import Validacao
from models.recompensa import Recompensa
from models.resgate import Resgate

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())
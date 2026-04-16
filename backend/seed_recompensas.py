import asyncio
from sqlalchemy import select
from core.database import engine, Base, SessionLocal
from models.usuario import Usuario
from models.denuncia import Denuncia
from models.imagem import Imagem
from models.validacao import Validacao
from models.recompensa import Recompensa
from models.resgate import Resgate

RECOMPENSAS_INICIAIS = [
    {
        "nome": "Desconto de 10% no Mercado Central",
        "descricao": "Apresente o codigo de resgate no Mercado Central para 10% de desconto em compras ate R$50.",
        "pontos_necessarios": 50,
        "estoque": 20,
    },
    {
        "nome": "Desconto de 15% na Padaria Damiao",
        "descricao": "Valido para qualquer produto da Padaria Damiao. Apresente o codigo no caixa.",
        "pontos_necessarios": 30,
        "estoque": 30,
    },
    {
        "nome": "Bolo fatia gratis na Bolos dos Baianos",
        "descricao": "Troque seus pontos por uma fatia de bolo na Bolos dos Baianos. Apresente o codigo no balcao.",
        "pontos_necessarios": 20,
        "estoque": 50,
    },
    {
        "nome": "Corte gratis na Barbearia Peniel",
        "descricao": "Um corte de cabelo gratis na Barbearia Peniel. Agende pelo codigo de resgate.",
        "pontos_necessarios": 60,
        "estoque": 15,
    },
    {
        "nome": "Kit ecologico (sacola + canudo inox)",
        "descricao": "Kit com sacola reutilizavel e canudo de inox. Retire no ponto de coleta do bairro.",
        "pontos_necessarios": 40,
        "estoque": 20,
    },
    {
        "nome": "Muda de arvore nativa",
        "descricao": "Retire sua muda de arvore nativa no viveiro municipal. Ajude a reflorestar a comunidade!",
        "pontos_necessarios": 25,
        "estoque": 50,
    },
]


async def seed(force=False):
    async with SessionLocal() as session:
        result = await session.execute(select(Recompensa).limit(1))
        if result.scalar_one_or_none() and not force:
            print("Recompensas ja existem, pulando seed.")
            return

        if force:
            await session.execute(select(Recompensa))
            result_all = await session.execute(select(Recompensa))
            for r in result_all.scalars().all():
                await session.delete(r)
            await session.commit()
            print("Recompensas antigas removidas.")

        for dados in RECOMPENSAS_INICIAIS:
            session.add(Recompensa(**dados))

        await session.commit()
        print(f"{len(RECOMPENSAS_INICIAIS)} recompensas inseridas com sucesso.")


if __name__ == "__main__":
    import sys
    force = "--force" in sys.argv
    asyncio.run(seed(force))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from core.config import settings
from routers import usuarios, denuncias, validacoes, recompensas, ranking
import os

app = FastAPI(title="ComuClean API", version="1.0.0")

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(usuarios.router)
app.include_router(denuncias.router)
app.include_router(validacoes.router)
app.include_router(recompensas.router)
app.include_router(ranking.router)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    return {"mensagem": "ComuClean API ativa"}

from fastapi import HTTPException


EXTENSOES_PERMITIDAS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_TAMANHO_ARQUIVO = 5 * 1024 * 1024


def _is_jpeg(b: bytes) -> bool:
    return len(b) >= 3 and b[:3] == b"\xff\xd8\xff"


def _is_png(b: bytes) -> bool:
    return len(b) >= 8 and b[:8] == b"\x89PNG\r\n\x1a\n"


def _is_webp(b: bytes) -> bool:
    return len(b) >= 12 and b[:4] == b"RIFF" and b[8:12] == b"WEBP"


def validar_imagem(conteudo: bytes, extensao: str) -> None:
    if len(conteudo) > MAX_TAMANHO_ARQUIVO:
        raise HTTPException(status_code=413, detail="Arquivo muito grande. Maximo: 5MB")

    ext = extensao.lower()
    if ext not in EXTENSOES_PERMITIDAS:
        raise HTTPException(
            status_code=400,
            detail="Tipo de arquivo nao permitido. Use: jpg, png ou webp",
        )

    if ext in {".jpg", ".jpeg"} and _is_jpeg(conteudo):
        return
    if ext == ".png" and _is_png(conteudo):
        return
    if ext == ".webp" and _is_webp(conteudo):
        return

    raise HTTPException(
        status_code=400,
        detail="Conteudo do arquivo nao corresponde a uma imagem valida",
    )

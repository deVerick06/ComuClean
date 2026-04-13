# ComuClean - Documentacao Completa

Plataforma comunitaria para denuncia anonima de descarte irregular de lixo, com gamificacao, mapa inteligente e validacao crowdsourced.

## Stack Tecnologica

| Camada | Tecnologia |
|--------|-----------|
| Backend | FastAPI (Python) - async |
| Banco de Dados | PostgreSQL + asyncpg |
| ORM | SQLAlchemy 2.0 (DeclarativeBase) |
| Autenticacao | JWT (python-jose) + bcrypt |
| Frontend | React 19 + Vite |
| Mapa | Leaflet + react-leaflet + OpenStreetMap (free) |
| Heatmap | leaflet.heat |
| HTTP Client | Axios |

## Estrutura do Projeto

```
ComuClean/
├── backend/
│   ├── core/
│   │   ├── config.py          # Settings via .env (DATABASE_URL, SECRET_KEY)
│   │   ├── database.py        # Engine async, sessionmaker, Base, get_db
│   │   ├── security.py        # Hash bcrypt, criacao/verificacao JWT
│   │   ├── deps.py            # Dependencies: get_current_user, get_admin_user
│   │   └── geo.py             # Haversine (calculo distancia GPS)
│   ├── models/
│   │   ├── usuario.py         # Tabela usuarios (id, nome, email, senha, pontos, papel)
│   │   ├── denuncia.py        # Tabela denuncias (id, usuario_id, tipo_lixo, lat, lng, status)
│   │   ├── imagem.py          # Tabela imagens (id, denuncia_id, url_imagem)
│   │   └── validacao.py       # Tabela validacoes (id, usuario_id, denuncia_id, tipo, lat, lng, imagem_url)
│   ├── schemas/
│   │   ├── usuario.py         # UsuarioCreate, UsuarioLogin, UsuarioResponse, TokenResponse
│   │   ├── denuncia.py        # DenunciaCreate, DenunciaResponse, DenunciaAdminResponse, DenunciaStatusUpdate
│   │   ├── imagem.py          # ImagemResponse
│   │   └── validacao.py       # ValidacaoCreate, ValidacaoResponse
│   ├── routers/
│   │   ├── usuarios.py        # Registro, login, perfil, minhas denuncias
│   │   ├── denuncias.py       # CRUD denuncias, upload imagem, admin status
│   │   └── validacoes.py      # Votacao comunitaria, upload prova
│   ├── main.py                # App FastAPI, CORS, StaticFiles, routers
│   ├── create_tables.py       # Script criacao de tabelas
│   └── Instrucoes/            # Documentos de escopo e especificacao
│       ├── ESCOPO.md
│       ├── BACKEND.md
│       ├── FRONTEND.md
│       └── DATABASE.md
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Navbar.jsx     # Barra navegacao inferior (Mapa / + / Perfil)
│       │   └── HeatmapLayer.jsx  # Camada heatmap do Leaflet
│       ├── contexts/
│       │   └── AuthContext.jsx    # Estado global autenticacao (login, registro, logout)
│       ├── pages/
│       │   ├── Login.jsx      # Tela de login
│       │   ├── Cadastro.jsx   # Tela de registro
│       │   ├── Home.jsx       # Mapa + Feed com filtros e acoes
│       │   ├── NovaDenuncia.jsx  # Wizard 3 steps (tipo > foto > confirmar)
│       │   └── Perfil.jsx     # Dashboard do usuario (pontos, denuncias)
│       ├── services/
│       │   └── api.js         # Axios configurado com interceptor JWT
│       ├── styles/
│       │   └── global.css     # Design system (cores neutras, tipografia Inter)
│       ├── App.jsx            # Roteamento com protecao de rotas
│       └── main.jsx           # Entry point
└── DOCUMENTACAO.md
```

## Endpoints da API

### Autenticacao e Usuarios

| Metodo | Rota | Auth | Descricao |
|--------|------|------|-----------|
| POST | `/usuarios` | Nao | Registro (hash bcrypt) |
| POST | `/login` | Nao | Login OAuth2 (retorna JWT) |
| GET | `/usuarios/me` | JWT | Perfil do usuario autenticado |
| GET | `/usuarios/me/denuncias` | JWT | Denuncias do proprio usuario |

### Denuncias

| Metodo | Rota | Auth | Descricao |
|--------|------|------|-----------|
| POST | `/denuncias` | JWT | Criar denuncia (limite 5/dia) |
| GET | `/denuncias` | Nao | Listar com filtros + contagem urgentes |
| GET | `/denuncias/{id}` | Nao | Detalhe de uma denuncia |
| PATCH | `/denuncias/{id}/status` | Admin | Atualizar status manualmente |
| POST | `/denuncias/{id}/imagens` | JWT | Upload de imagem |

### Validacoes

| Metodo | Rota | Auth | Descricao |
|--------|------|------|-----------|
| POST | `/validacoes` | JWT | Votar urgente/resolvido (proximidade 100m para ja_limpo) |
| POST | `/validacoes/{id}/imagem` | JWT | Upload foto de prova |

## Regras de Negocio Implementadas

### Anonimato Total (Diferencial)
- Denuncias sao sempre anonimas para outros usuarios
- DenunciaResponse publica NAO expoe usuario_id
- Apenas o autor (GET /usuarios/me/denuncias) e admins veem a autoria

### Controle de Spam
- Limite de 5 denuncias por dia por usuario
- Retorna HTTP 429 quando excede

### Sistema de Urgencia
- Usuarios marcam denuncias como "Urgente" (envia ainda_sujo ao backend)
- Feed ordena por total de votos urgentes (mais urgente = primeiro)
- Contagem visivel no card e no popup do mapa

### Validacao com Prova (Resolvido)
- Para marcar como resolvido, o usuario deve:
  1. Estar a no maximo 100 metros do local (verificacao Haversine no backend)
  2. Tirar uma foto como prova
- Backend calcula distancia GPS e rejeita se estiver longe
- 3 votos "ja_limpo" = denuncia resolvida automaticamente

### Gamificacao (Pontos)
- +10 pontos ao autor quando sua denuncia e resolvida
- Pontos exibidos no perfil do usuario
- Sistema de recompensas previsto para versao futura

### Papeis de Usuario
- **morador** (padrao): cria denuncias, vota, acumula pontos
- **admin**: tudo do morador + PATCH status de denuncias

## Funcionalidades do Frontend

### Mapa Inteligente
- **Pinos coloridos**: azul (aberta), amarelo (em analise), verde (resolvida)
- **Mapa de calor**: heatmap com gradiente verde > amarelo > vermelho por concentracao
- **Toggle Pinos/Calor**: troca entre visualizacoes
- **Popup**: tipo de lixo, status, contagem de urgentes, descricao
- **Geolocalizacao**: centraliza no GPS do usuario
- Tecnologia: Leaflet + OpenStreetMap (100% gratuito)

### Feed de Denuncias
- Cards com badges de tipo e status
- Contagem de urgentes por denuncia
- Filtros: Todas, Abertas, Em analise, Resolvidas
- Botao **Urgente**: voto rapido com 1 toque
- Botao **Resolvido**: abre fluxo de prova (foto + GPS)

### Fluxo de Nova Denuncia
- Wizard de 3 passos com indicador visual
- Step 1: Selecao do tipo de lixo (lixo comum, entulho, reciclavel)
- Step 2: Foto obrigatoria + descricao opcional
- Step 3: Confirmacao de GPS + resumo antes de enviar

### Perfil do Usuario
- Avatar com inicial do nome
- Estatisticas: pontos, total denuncias, resolvidas
- Lista de "minhas denuncias" com status
- Botao de logout

### Design
- Paleta neutra (cinzas, branco) com accent teal
- Tipografia Inter
- Mobile-first com navbar bottom + FAB central
- Bordas suaves, sombras minimas
- Badges coloridos por status e tipo

## Como Rodar

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python create_tables.py
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npx vite --port 5173
```

### Variaveis de Ambiente (backend/.env)
```
DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost:5432/comuclean
SECRET_KEY=sua-chave-secreta
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## Pendencias (Roadmap)
- [ ] Alembic para migrations
- [ ] Dashboard admin com estatisticas (graficos, areas criticas)
- [ ] Agrupamento de denuncias por proximidade (Pandas)
- [ ] Sistema de recompensas (resgate de pontos)
- [ ] Modo offline (cache local + sync)
- [ ] Notificacoes push/email
- [ ] Testes automatizados

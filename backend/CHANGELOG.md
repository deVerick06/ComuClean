# Changelog - ComuClean Backend

## [0.3.0] - 2026-04-12

### Adicionado
- **Anonimato total**: DenunciaResponse pública não expõe mais usuario_id (diferencial do app)
- **DenunciaAdminResponse**: Schema separado com usuario_id visível apenas para admins
- **DenunciaStatusUpdate**: Schema para admin atualizar status (aberta/em_analise/resolvida)
- **GET /usuarios/me/denuncias**: Endpoint para o usuário ver suas próprias denúncias
- **PATCH /denuncias/{id}/status**: Endpoint admin para alterar status manualmente
- **Controle de spam**: Limite de 5 denúncias por dia por usuário (HTTP 429)
- **Arquivos estáticos**: Imagens servidas via /uploads (StaticFiles)
- **get_admin_user**: Dependency para proteger rotas administrativas (papel="admin")

### Corrigido
- **bcrypt**: Removido passlib (incompatível), usando bcrypt diretamente
- **JWT sub**: Campo sub do token agora é string (exigência do python-jose)
- **Login OAuth2**: Endpoint /login aceita form-data para integração com Swagger Authorize

### Documentação
- **ESCOPO.md**: Adicionada regra de anonimato total nas denúncias
- **BACKEND.md**: Reescrito com todos os endpoints e regras de negócio atualizadas

## [0.2.0] - 2026-04-12

### Adicionado
- **main.py**: Entry point da aplicação FastAPI com CORS habilitado e inclusão dos routers
- **core/security.py**: Módulo de segurança com hash bcrypt e geração/validação de JWT
- **core/deps.py**: Dependency `get_current_user` para proteger rotas autenticadas
- **core/config.py**: Adicionado SECRET_KEY e ACCESS_TOKEN_EXPIRE_MINUTES nas settings
- **schemas/usuario.py**: Adicionado UsuarioLogin e TokenResponse
- **schemas/denuncia.py**: DenunciaCreate (com Literal para tipo_lixo) e DenunciaResponse
- **schemas/imagem.py**: ImagemResponse
- **schemas/validacao.py**: ValidacaoCreate (com Literal para tipo_validacao) e ValidacaoResponse
- **routers/usuarios.py**: POST /usuarios (registro), POST /login (JWT), GET /usuarios/me (perfil)
- **routers/denuncias.py**: POST /denuncias, GET /denuncias (filtros status/tipo_lixo), GET /denuncias/{id}, POST /denuncias/{id}/imagens (upload de arquivo)
- **routers/validacoes.py**: POST /validacoes com regras de negócio (impede auto-voto, impede duplicata, 3 votos "ja_limpo" resolve denúncia e credita 10 pontos ao autor)
- **Dependências**: passlib, bcrypt, python-jose, python-multipart

### Endpoints disponíveis
| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/` | Não | Health check |
| POST | `/usuarios` | Não | Registro com hash bcrypt |
| POST | `/login` | Não | Login retorna JWT |
| GET | `/usuarios/me` | JWT | Perfil do usuário autenticado |
| POST | `/denuncias` | JWT | Criar denúncia |
| GET | `/denuncias` | Não | Listar denúncias (filtro por status e tipo_lixo) |
| GET | `/denuncias/{id}` | Não | Detalhe de uma denúncia |
| POST | `/denuncias/{id}/imagens` | JWT | Upload de imagem para denúncia |
| POST | `/validacoes` | JWT | Registrar voto comunitário |

## [0.1.0] - Commits anteriores

### Adicionado
- **core/config.py**: Settings com pydantic-settings carregando .env
- **core/database.py**: Engine assíncrona, sessionmaker, Base e get_db
- **models/**: Tabelas usuarios, denuncias, imagens e validacoes com relacionamentos bidirecionais
- **schemas/usuario.py**: UsuarioCreate e UsuarioResponse (versão inicial)
- **create_tables.py**: Script para criação das tabelas no banco

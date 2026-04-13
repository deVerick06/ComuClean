# Documentação da API Backend

## Especificações Técnicas
- Framework: FastAPI
- Validação de Dados: Pydantic V2
- Gerenciamento de Ambiente: pydantic-settings (.env)
- Arquitetura: Camadas separadas (core, models, schemas, routers)

## Estrutura Atual (Finalizada)
- /core: Configurações globais, engine assíncrona (get_db via yield), segurança (bcrypt + JWT) e dependências de autenticação.
- /models: Classes de mapeamento objeto-relacional com relacionamentos bidirecionais explícitos.
- /schemas: Classes de validação de entrada/saída (Create e Response) para blindagem da API.
- /routers: Endpoints organizados por domínio (usuarios, denuncias, validacoes).

## Regras de Negócio Fundamentais

### Anonimato de Denúncias (Diferencial do App)
- Denúncias são SEMPRE anônimas para outros usuários.
- A resposta pública (DenunciaResponse) NÃO expõe o usuario_id.
- Apenas o próprio autor vê suas denúncias em GET /usuarios/me/denuncias.
- Apenas administradores (papel="admin") veem o usuario_id via DenunciaAdminResponse.

### Controle de Spam
- Limite de 5 denúncias por dia por usuário.
- Retorna HTTP 429 quando o limite é atingido.

### Gamificação (Sistema de Pontos)
- +10 pontos ao autor quando sua denúncia é resolvida (3 votos "ja_limpo").
- Pontos futuros: participação em ações comunitárias, comprovação de reciclagem.
- Sistema de recompensas (parcerias com comércio local) previsto para versão futura.
- Os pontos ficam no campo `usuarios.pontos`.

### Validação Comunitária (Crowdsourcing)
- Qualquer usuário autenticado pode votar em denúncias de terceiros.
- Tipos de voto: "ainda_sujo" ou "ja_limpo".
- Não pode votar na própria denúncia.
- Não pode votar duas vezes na mesma denúncia.
- 3 votos "ja_limpo" = status muda para "resolvida" + pontos ao autor.

## Endpoints Implementados

### Módulo de Autenticação
- [x] Hash de senha com bcrypt (direto, sem passlib).
- [x] Geração de token JWT (python-jose).
- [x] Dependência get_current_user para rotas protegidas.
- [x] Dependência get_admin_user para rotas administrativas.

### Módulo de Usuários
- [x] POST /usuarios (Registro com hash de senha).
- [x] POST /login (Autenticação OAuth2, retorna JWT).
- [x] GET /usuarios/me (Retorna perfil autenticado).
- [x] GET /usuarios/me/denuncias (Lista denúncias do próprio usuário).

### Módulo de Denúncias
- [x] POST /denuncias (Cria denúncia com limite diário).
- [x] GET /denuncias (Lista denúncias, filtros por status e tipo_lixo).
- [x] GET /denuncias/{id} (Detalhe de uma denúncia).
- [x] PATCH /denuncias/{id}/status (Admin atualiza status manualmente).
- [x] POST /denuncias/{id}/imagens (Upload de imagem).

### Módulo de Validações
- [x] POST /validacoes (Voto comunitário com regras de negócio).

## Tarefas Pendentes (Roadmap)
- [ ] Configurar Alembic para migrações.
- [ ] Endpoints de estatísticas para dashboard admin (volume, áreas críticas).
- [ ] Endpoint de dados para heatmap (agrupamento com Pandas).
- [ ] Sistema de recompensas (resgate de pontos).
- [ ] Notificações push/email.

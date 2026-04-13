# ComuClean - Especificação do Sistema

Documentação central do escopo, arquitetura e regras de negócio da plataforma ComuClean.

## 1. Arquitetura Tecnológica
- Backend: FastAPI (Python)
- Banco de Dados: PostgreSQL
- Frontend: A definir (React/Vite recomendado)
- Mapeamento: Leaflet (Renderização de mapas e coordenadas)
- Análise de Dados: Pandas (Processamento de estatísticas e heatmaps)

## 2. Módulo de Denúncias (Core)
O fluxo principal de interação do morador com o aplicativo.

Regras de Negócio e Funcionalidades:
- Anonimato Total: Denúncias são sempre anônimas para outros usuários. Este é o diferencial da plataforma — o morador denuncia sem medo de retaliação. Apenas o próprio autor e administradores têm acesso à autoria.
- Captura de Imagem: Foto obrigatória do local (Controle de Qualidade).
- Geolocalização: Captura e marcação automática das coordenadas GPS.
- Categorização do Descarte:
  - Lixo comum
  - Entulho
  - Reciclável
- Ciclo de Vida da Denúncia (Status):
  - Aberta
  - Em análise
  - Resolvida
- Controle de Spam: Limite de 5 denúncias diárias por usuário ativo.

## 3. Mapa Inteligente e Análise Geoespacial
Visualização de dados para moradores e gestão pública.

Visualização do Mapa:
- Pontos individuais de denúncias ativas.
- Heatmap (Mapa de Calor) indicando concentração de descartes.
  - Vermelho: Nível Crítico
  - Amarelo: Nível Médio
  - Verde: Nível Baixo

Inteligência de Dados (Pandas):
- Agrupamento de denúncias por raio de proximidade.
- Sistema de Sugestão: Detecção de áreas com alta reincidência de descarte irregular para acionar alertas de necessidade de instalação de lixeiras ou contêineres públicos.

## 4. Gamificação e Engajamento
Sistema de incentivo para manter os moradores ativos na plataforma.

Sistema de Pontuação:
- Crédito de pontos por registro de denúncias válidas.
- Crédito por participação em ações comunitárias.
- Crédito por comprovação de reciclagem.

Sistema de Recompensas:
- Viabilizado via parcerias com o comércio local.
- Resgate de pontos por descontos em mercados da região.
- Uso de pontos como ingressos para participação em sorteios locais.

Validação Comunitária (Crowdsourcing):
- Moradores podem interagir com denúncias de terceiros.
- Função de confirmação ("Já limparam aqui" / "Ainda está sujo").
- Validação cruzada para garantir a veracidade do status da denúncia.

## 5. Painel Administrativo e Dashboard
Interface dedicada à gestão (Organizadores comunitários ou Prefeitura).

Dashboard Analítico:
- Volume total de denúncias cadastradas.
- Identificação e listagem das áreas mais críticas.
- Gráficos de evolução temporal (resoluções vs. novas denúncias).
- Métricas de engajamento da comunidade (usuários ativos, validações).

Funções de Gestão:
- Visualização de todas as denúncias em painel tabular.
- Atualização manual de status (ex: marcar como resolvido após coleta).
- Ferramenta para priorização de rotas de limpeza com base na criticidade.

## 6. Funcionalidades de Melhoria Contínua (Roadmap Futuro)
Recursos previstos para iterações posteriores do sistema.

Modo Offline:
- Capacidade de registrar fotos e coordenadas sem conexão com a internet.
- Armazenamento em cache local e sincronização automática (Envio) quando a conexão for restabelecida.

Sistema de Notificações (Push/Email):
- Alertas de resolução ("Sua denúncia foi resolvida").
- Alertas de proximidade ("Novo ponto crítico relatado perto de você").
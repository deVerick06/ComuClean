# Documentação da Interface Frontend

## Especificações Técnicas
- Framework Base: React (via Vite)
- Rotas: React Router DOM
- Mapa: Biblioteca a definir (Leaflet / React-Leaflet recomendado para uso gratuito)
- Cliente HTTP: Axios ou Fetch API nativa.

## Requisitos de Interface (Pendentes)

1. Autenticação e Perfil
- Tela de Cadastro (Nome, Email, Senha).
- Tela de Login (Email, Senha).
- Componente de Dashboard do Usuário (Exibição de Pontuação e Histórico de Denúncias).

2. Módulo de Mapa e Feed
- Mapa interativo renderizando pinos nas coordenadas das denúncias ativas.
- Feed lateral ou modal em formato de lista (estilo rede social) exibindo foto, descrição e tipo de lixo.

3. Fluxo de Criação
- Formulário de Denúncia: Captura de coordenada atual (Geolocation API do navegador), seleção do tipo de lixo, descrição opcional.
- Interface de captura/upload de câmera para a foto do local.

4. Fluxo de Validação
- Botões de ação nas denúncias de terceiros: "Ainda está sujo" e "Já foi limpo".
# Documentação do Banco de Dados

## Especificações Técnicas
- SGBD: PostgreSQL 15+
- Driver Assíncrono: asyncpg
- ORM: SQLAlchemy 2.0 (Paradigma DeclarativeBase com Type Hints)
- Controle de Migrações: Script local (create_tables.py). Migração para Alembic pendente.

## Esquema de Tabelas (Finalizado)

1. usuarios
- id: Integer, Primary Key, Autoincrement
- nome: String(125), Not Null
- email: String(125), Not Null, Unique
- senha: String(255), Not Null (Armazenará hash)
- pontos: Integer, Default 0
- papel: String(10), Default 'morador'
- criado_em: DateTime, Default utcnow

2. denuncias
- id: Integer, Primary Key, Autoincrement
- usuario_id: Integer, Foreign Key (usuarios.id)
- tipo_lixo: String(20), Not Null
- latitude: Float, Not Null
- longitude: Float, Not Null
- descricao: Text, Nullable
- status: String(20), Default 'aberta'
- criada_em: DateTime, Default utcnow

3. imagens
- id: Integer, Primary Key, Autoincrement
- denuncia_id: Integer, Foreign Key (denuncias.id)
- url_imagem: String(255), Unique
- enviada_em: DateTime, Default utcnow

4. validacoes (Tabela Associativa)
- id: Integer, Primary Key, Autoincrement
- usuario_id: Integer, Foreign Key (usuarios.id)
- denuncia_id: Integer, Foreign Key (denuncias.id)
- tipo_validacao: String(20), Default 'ainda_sujo'
- data: DateTime, Default utcnow

## Tarefas Pendentes
- [ ] Configurar Alembic para rastreamento de alterações estruturais (Migrations).
- [ ] Criar tabela ou lógica de recompensas baseada na pontuação do usuário.
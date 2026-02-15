# Be-Productive

**Rede Social com Foco em Saúde Mental** - Uma plataforma que equilibra produtividade e bem-estar.

## 🧠 Sobre o Projeto

Be-Productive é uma rede social inovadora que utiliza algoritmos éticos de recomendação para promover o equilíbrio entre produtividade e entretenimento, priorizando a saúde mental dos usuários.

### Funcionalidades Principais

- 🎯 **Metas de Foco** - Defina tempos para produtividade e entretenimento
- 📰 **Feed Personalizado** - Conteúdo baseado em seus interesses e bem-estar
- 🌱 **Sugestões Saudáveis** - Lembretes para pausas e autocuidado
- 🤖 **Moderação Inteligente** - Sistema de moderação com suporte a IA

## 🏗️ Arquitetura

```
Be-Productive/
├── frontend/          # SvelteKit + TypeScript
├── backend/           # Go + MySQL
└── recommender/       # Python + FastAPI + scikit-learn
```

## 🚀 Quick Start

### Pré-requisitos

- Node.js 18+
- Go 1.21+
- Python 3.11+
- MySQL 8.0+

### 1. Configurar Banco de Dados

```bash
# Criar banco de dados
mysql -u root -p -e "CREATE DATABASE be_productive;"

# Executar migrations
mysql -u root -p be_productive < backend/migrations/001_create_tables.up.sql
mysql -u root -p be_productive < backend/migrations/002_seed_data.up.sql
```

### 2. Iniciar Backend (Go)

```bash
cd backend

# Instalar dependências
go mod download

# Configurar variáveis de ambiente
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD=sua_senha
export DB_NAME=be_productive
export SERVER_PORT=8080

# Executar
go run cmd/server/main.go
```

### 3. Iniciar Frontend (SvelteKit)

```bash
cd frontend

# Instalar dependências
npm install

# Executar em modo desenvolvimento
npm run dev
```

Acesse: http://localhost:5173

### 4. Iniciar Recommender (Python)

```bash
cd recommender

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Executar
uvicorn src.api.main:app --port 8001 --reload
```

## 📁 Estrutura do Projeto

### Frontend (SvelteKit)

```
frontend/src/
├── lib/
│   ├── api.ts           # Cliente API
│   ├── stores.ts        # Estado global (Svelte stores)
│   └── components/      # Componentes reutilizáveis
├── routes/
│   ├── +page.svelte     # Landing page
│   ├── auth/            # Login/Registro
│   ├── feed/            # Feed personalizado
│   └── focus/           # Metas de foco
└── app.css              # Design system
```

### Backend (Go)

```
backend/
├── cmd/server/main.go   # Entry point
├── internal/
│   ├── domain/          # Entidades de domínio
│   ├── usecase/         # Lógica de negócio
│   ├── adapter/
│   │   ├── http/        # Handlers e rotas
│   │   └── repository/  # Repositórios MySQL
│   └── infrastructure/  # Config, DB, serviços externos
└── migrations/          # Scripts SQL
```

### Recommender (Python)

```
recommender/src/
├── api/
│   └── routes/          # Endpoints FastAPI
├── domain/
│   └── metrics.py       # Cálculo de qualidade (RN002)
├── models/
│   ├── hybrid.py        # Modelo híbrido
│   ├── content_based.py # Filtro baseado em conteúdo
│   └── collaborative.py # Filtro colaborativo
└── inference/
    └── predictor.py     # Geração de recomendações
```

## 🔧 Variáveis de Ambiente

### Backend (.env)

```env
SERVER_HOST=localhost
SERVER_PORT=8080
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=be_productive
RECOMMENDER_URL=http://localhost:8001
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8080/api/v1
```

## 📚 API Endpoints

### Usuários
- `POST /api/v1/auth/register` - Registrar usuário
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/users/{id}` - Obter usuário
- `POST /api/v1/users/{id}/topics` - Selecionar tópicos

### Conteúdo
- `POST /api/v1/content` - Publicar conteúdo
- `GET /api/v1/feed` - Obter feed personalizado
- `POST /api/v1/content/{id}/feedback` - Enviar feedback
- `POST /api/v1/content/{id}/report` - Reportar conteúdo

### Foco
- `POST /api/v1/focus/goals` - Criar meta
- `GET /api/v1/focus/goals` - Listar metas
- `POST /api/v1/focus/sessions` - Iniciar sessão
- `PUT /api/v1/focus/sessions/{id}` - Finalizar sessão
- `GET /api/v1/focus/sessions/{id}/report` - Relatório da sessão

## 🧪 Testes

```bash
# Backend
cd backend && go test ./...

# Frontend
cd frontend && npm run test

# Recommender
cd recommender && pytest
```

## 📝 Licença

Este projeto é desenvolvido para fins acadêmicos - FAETERJ-RIO.

---

Desenvolvido com ❤️ por Fellype Samuel e Daniel Gomes Venâncio

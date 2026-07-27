# Backend (Go) — API Gateway

Gateway único do Be-Productive (net/http, porta **8080**). Faz autenticação (JWT + bcrypt), CRUD de conteúdo, sessões de foco, comunidades e settings. É a **única** camada que o frontend conhece, e o único cliente do recomendador Python.

## Executar

```bash
cd backend
go mod download
go run cmd/server/main.go
go test ./...          # testes colocados (*_test.go)
```

## Variáveis de ambiente (`.env`)

```
DB_HOST=localhost DB_PORT=3306 DB_USER=root DB_PASSWORD= DB_NAME=be_productive
SERVER_HOST=localhost SERVER_PORT=8080
RECOMMENDER_URL=http://localhost:8002
RECOMMENDER_SHARED_SECRET=<segredo enviado como X-Internal-Auth ao Python>
JWT_SECRET=<segredo>
```

## Estrutura (Clean Architecture)

```
internal/
├── domain/          # Entidades: User, Content, Topic, Community, FocusGoal, Session
├── usecase/         # Regras de negócio (content, focus, user, community)
├── adapter/
│   ├── http/        # Handlers + router + middleware (auth)
│   └── repository/  # Implementações MySQL
└── infrastructure/  # Conexão DB, config
```

## Segurança

- Senhas em **bcrypt** (upgrade transparente de hashes SHA-256 legados no login).
- Identidade sempre derivada dos **claims do JWT**, não do corpo/query (sem IDOR); `403` se o id do path divergir do token.
- **Pacto de Ulisses** (Modo Absoluto) enforçado a partir da sessão de foco ativa, server-side.
- Ao chamar o Python, envia `X-Internal-Auth` quando `RECOMMENDER_SHARED_SECRET` está definido.

Detalhes em [`../docs/pt-BR/security.md`](../docs/pt-BR/security.md) e [`../docs/pt-BR/architecture.md`](../docs/pt-BR/architecture.md).

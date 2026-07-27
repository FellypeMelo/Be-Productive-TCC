# Segurança e privacidade

Um sistema cuja tese é proteger usuários vulneráveis não pode, ele próprio, vazá-los ou forjá-los. Esta é a postura atual.

## Aplicado

| Item | Implementação |
|---|---|
| **Hashing de senha** | bcrypt (`DefaultCost`). Hashes SHA-256 legados são verificados uma vez e **re-hasheados para bcrypt** no próximo login bem-sucedido. `backend/internal/usecase/user/service.go` |
| **Identidade da requisição** | Derivada dos **claims do JWT**, nunca do corpo/query. Rotas que operam sobre "o usuário atual" ignoram `user_id`/`autor_id` do cliente; divergência entre id do path e do token → `403`. Elimina IDOR. `backend/internal/adapter/http/handler/*.go` |
| **Pacto de Ulisses server-side** | Modo Absoluto é derivado da **sessão de foco ativa** no servidor, não de um flag de cliente descartável. |
| **Endpoints internos do Python** | Guarda `X-Internal-Auth` comparado a `RECOMMENDER_SHARED_SECRET`. Quando o segredo está definido, os endpoints recommend/fatigue/behavior exigem o header; quando ausente (dev), ficam abertos. `recommender/src/api/deps.py` |
| **Privacidade Edge-AI** | Fadiga computada **no dispositivo**; telemetria bruta (`v_scroll`, `v_alt`) nunca sai do navegador; frontend fala só com o Go. `frontend/src/lib/fatigue.ts` |
| **Injeção de SQL** | Nenhuma. Go e Python usam apenas placeholders parametrizados (`?` / `%s`), inclusive em cláusulas `IN(...)`/`ORDER BY FIELD(...)`. |

## Pendências de hardening (fora do escopo desta rodada)

- `JWT_SECRET` possui default hardcoded no `config.go` — em produção deve **falhar-fechado** (recusar iniciar) se a variável não estiver definida.
- CORS usa `Access-Control-Allow-Origin: *` — restringir às origens conhecidas.
- Middleware JWT não faz *allowlist* explícita do método de assinatura (jwt/v5 já rejeita `alg:none` por padrão).

## Privacidade por design (LGPD/RGPD)

- Inferência comportamental **on-device**; o servidor recebe apenas o veredito de fricção.
- A população da simulação é **100% sintética** (log-normal), sem dados empíricos reais.
- Job de anonimização remove PII de usuários inativos (`backend/internal/usecase/user/anonimize_job.go`).

Ver [architecture.md](architecture.md) para o modelo de confiança entre camadas.

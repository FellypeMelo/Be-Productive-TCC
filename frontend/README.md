# Frontend (SvelteKit) — UI + Edge AI on-device

SvelteKit + TypeScript na porta **5173**. Fala **exclusivamente** com o gateway Go. É aqui que vive o **Edge AI**: a inferência de fadiga roda no navegador.

## Executar

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
npm run check        # type-check (svelte-check / tsc)
npm run build        # build de produção
```

## Variáveis de ambiente (`.env`)

```
VITE_API_URL=http://localhost:8080/api/v1
```

Não há `RECOMMENDER_URL`: o frontend **não** chama o Python. Toda inferência de fadiga é local.

## Edge AI — `src/lib/fatigue.ts`

Módulo TypeScript, sem dependências e sem rede, que espelha a matemática do domínio Python:

- **EDO de Ego-Depletion (Eq. 4)** — integra `R(t)` a partir de `v_scroll`/`v_alt` medidos localmente.
- **Hawkes bi-kernel (Eq. 2)** — soma sobre o histórico de eventos para detectar dominância do Sistema 1.
- **Fricção positiva** — nível (`none`/`mild`/`high`/`block`) derivado de `R/R_max` localmente.

Telemetria bruta (`v_scroll`, `v_alt`) **nunca sai do dispositivo**. A fricção **falha-fechada**: em erro, escala para pelo menos `mild`. O bloqueio exige confirmação deliberada (não é um clique único).

## Estrutura

```
src/
├── lib/
│   ├── api.ts          # Cliente do gateway Go (somente)
│   ├── fatigue.ts      # Edge AI: EDO + Hawkes + fricção (on-device)
│   ├── stores.ts       # Estado global (Svelte stores)
│   └── components/
└── routes/             # feed, focus, auth, communities, settings
```

Ver [`../Docs/ARCHITECTURE.md`](../Docs/ARCHITECTURE.md) para o modelo Edge-AI e [`../Docs/SECURITY.md`](../Docs/SECURITY.md) para privacidade.

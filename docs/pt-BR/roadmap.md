# Roadmap de evolução — do protótipo à visão do artigo

Plano de melhorias organizado em torno da tese do artigo: **transformar sistemas de recomendação de predadores da atenção em guardiões da reserva cognitiva.** Cada fase aproxima a implementação do modelo idealizado e ataca as limitações que o próprio artigo reconhece (validação in-vivo, classificadores reais, modelos de negócio).

Legenda de estado: ✅ feito · 🟡 parcial · ⬜ planejado.

## Onde estamos hoje

| Pilar do artigo | Estado |
|---|---|
| ABM sem confundimento reproduzindo d = 3.25 | ✅ |
| Hawkes real, Thompson com posterior, Min-Norm exercida | ✅ |
| Edge AI on-device (EDO + Hawkes no navegador) | ✅ |
| Pacto de Ulisses enforçado server-side | ✅ |
| Segurança base (bcrypt, sem IDOR, auth interna) | ✅ |
| Classificadores de segurança / recomendador híbrido | 🟡 baselines observáveis; modelos treinados pendentes |
| Validação com usuários reais | ⬜ |

---

## Fase 1 — De stand-ins a modelos reais
*Objetivo: o Min-Norm e o `base_score` operarem sobre sinal aprendido, não heurística.*

- 🟡 **Classificadores de segurança reais (IA_Safety, Eq. 3).** O hash foi removido; uma baseline lexical auditável analisa texto real em cinco dimensões. Modelos ONNX ainda exigem treino e validação.
- 🟡 **Recomendador híbrido treinado.** O ranking usa sinais reais de conteúdo e interação. TF-IDF/ALS ainda exigem dataset, treino e avaliação.
- ⬜ **Estimação de Hawkes por MLE.** Ajustar α/β dos dois kernels a partir de trajetórias reais de eventos, em vez de constantes fixas.
- ⬜ **Calibração de fadiga por usuário.** Aprender `μ_rest`, `k1`, `k2` individuais a partir do comportamento observado (com consentimento), sincronizados via os endpoints Edge já existentes.

## Fase 2 — Maturidade do Edge AI
*Objetivo: cumprir plenamente “inferência estritamente no dispositivo”.*

- ⬜ **Inferência on-device via WASM/ONNX Runtime Web / TF.js** para os classificadores de segurança, não só a EDO/Hawkes.
- ⬜ **Persistência local** da reserva `R(t)` e dos parâmetros (IndexedDB) para continuidade entre sessões, sem servidor.
- ⬜ **Offline-first / PWA** com service worker; o servidor recebe apenas vereditos de fricção.
- ⬜ **Fricção sensorial** completa: dessaturação progressiva, desaceleração real de scroll e ranqueamento exclusivo de conteúdo denso quando `R` cai (hoje: dessaturação + gate de bloqueio).

## Fase 3 — Validação empírica in-vivo *(a principal limitação declarada no artigo)*
*Objetivo: sair do ambiente simulado para usuários reais.*

- ⬜ **Estudo longitudinal** com voluntários (opt-in), aprovação ética/CEP, grupo controle vs. Be-Productive.
- ⬜ **Métricas além de tempo de tela**: bem-estar (escalas validadas), recaídas cognitivas, aceitação das fricções, retenção da intenção declarada (KL real).
- ⬜ **Instrumentação de telemetria anônima e agregada** (sob consentimento) que preserve o princípio on-device.
- ⬜ **Pré-registro** do desenho experimental e publicação dos dados/`abm` como material reprodutível.

## Fase 4 — Sustentabilidade e conformidade *(discussão do artigo)*
*Objetivo: viabilizar um sistema que, por design, reduz tempo de uso.*

- ⬜ **Modelos de negócio não-extrativistas**: assinatura premium, B2B de produtividade, licenciamento para instituições de ensino/saúde.
- ⬜ **Conformidade regulatória**: transparência algorítmica e mitigação de risco alinhadas ao Digital Services Act (DSA) e à LGPD; relatório de “nutrição algorítmica”.
- ⬜ **Painel de transparência** para o usuário: por que um item foi rebaixado (qual `P_m` disparou o Min-Norm), estado da reserva, histórico de fricção.

## Fase 5 — Hardening de produção
*Objetivo: um sistema de proteção que não se comprometa.*

- ⬜ `JWT_SECRET` **fail-closed** (recusar iniciar sem segredo); allowlist de método de assinatura.
- ⬜ CORS restrito às origens conhecidas; rate limiting; headers de segurança.
- 🟡 Logs estruturados, métricas, correlação, readiness e CI das três camadas foram implementados. Tracing distribuído continua planejado.
- ⬜ Migração da anonimização para usar `last_active` real (hoje usa `updated_at`) e cascatear em linhas comportamentais.

## Fase 6 — Extensões de pesquisa
*Objetivo: aprofundar o Value-Aligned RecSys.*

- ⬜ **Bandits contextuais** substituindo o Thompson de 2 braços por seleção sensível ao contexto (hora, histórico, estado de fadiga).
- ⬜ **Otimização multiobjetivo de Pareto** explícita entre engajamento, alinhamento à intenção e reserva cognitiva.
- ⬜ **Avaliação causal off-policy** (IPS/doubly-robust) para estimar efeito sem A/B disruptivo.
- ⬜ **Ablações adicionais** e análise de sensibilidade ampliada no ABM (mais eixos de vulnerabilidade).

## Transversais (contínuo)

- ⬜ **Acessibilidade** (WCAG AA), i18n (PT/EN), tema claro/escuro real.
- ⬜ **Runner de testes de frontend** (Vitest já presente) com cobertura de componentes; E2E Playwright ampliado.
- ⬜ **Documentação viva**: manter [architecture](architecture.md), [reproducibility](reproducibility.md), [security](security.md) e [paper-code-truth-map](paper-code-truth-map.md) sincronizados a cada mudança estrutural.

---

### Princípio de priorização

Sempre que houver conflito, a ordem de prioridade segue a tese do artigo: **preservar a agência e a reserva cognitiva do usuário > alinhamento à intenção declarada > eficiência técnica > engajamento**. Nenhuma melhoria deve inverter essa hierarquia.

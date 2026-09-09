# Implementação dos 10 milestones

Este documento registra o que foi implementado, como validar e quais limites dependem de dados ou operação externa. Um item não é chamado de "modelo treinado" sem dataset, treino e avaliação.

## 1. Baseline e métricas

Implementado: métricas offline `Precision@K`, `Recall@K`, `NDCG@K`, cobertura e diversidade; executor reproduzível; versão, experimento, explicações e fallback no feed.

```bash
cd recommender
python -m src.evaluation.run --input evaluation_fixture.example.json --k 3
```

Limite externo: baseline de produto precisa de eventos reais consentidos.

## 2. Segurança de produção

Implementado: `JWT_SECRET` obrigatório; segredo interno obrigatório em produção; comparação constante; CORS configurável; rate limits; limite de corpo; headers de segurança; erros sanitizados; timeouts; pool de conexões; shutdown gracioso.

## 3. Contratos entre serviços

Implementado: OpenAPI do feed e eventos; schemas FastAPI estritos; metadados propagados entre Python, Go e TypeScript; `X-Request-ID` para correlação.

Próxima extensão: documentar endpoints CRUD antigos no OpenAPI. Comportamento atual foi preservado.

## 4. Eventos e feedback

Implementado: migration `004`; impressão, abertura, conclusão e ocultação; `event_id` idempotente; identidade pelo JWT; posição, algoritmo, variante e fricção derivada; coleta desativada sem personalização. Scroll bruto nunca sai do navegador.

## 5. Ranking híbrido v2

Implementado: candidatos com cold start; afinidade, qualidade, recência, histórico, repetição e exploração estável; priors; diversificação limitada; filtros; score personalizado separado da qualidade global; explicações.

Limite externo: TF-IDF/ALS só deve ser ativado após treino e avaliação com dataset real.

## 6. Fadiga e autonomia

Implementado: ODE e Hawkes locais; consentimento por configuração; reserva local por oito horas; recuperação durante ausência; bloqueio com confirmação e espera; falha aumenta proteção.

## 7. Safety Gateway

Implementado: análise de título, corpo e tags em cinco dimensões auditáveis; Min-Norm; penalidade moderada; bloqueio crítico; interface pronta para ONNX.

Limite externo: baseline lexical não é classificador treinado. Produção exige corpus rotulado, revisão humana e avaliação por categoria.

## 8. Experimentos

Implementado: atribuição estável `control`/`treatment`; exposição na resposta e eventos; tratamento de diversidade; ABM separado do runtime.

Limite externo: causalidade exige amostra real, consentimento e protocolo pré-registrado.

## 9. Observabilidade e resiliência

Implementado: logs JSON sem PII; métricas Prometheus em Go e Python; liveness; readiness; request ID; fallback explícito; timeout do recomendador.

```text
GET /health
GET /health/ready
GET /metrics
```

## 10. Qualidade e entrega

Implementado: CI das três camadas; testes, type-check e build; Dockerfiles; Compose; ledger de migrations; rollback da migration de eventos.

```bash
docker compose up --build
```

## Definition of Done

Código fica concluído quando testes das três camadas passam. Qualidade científica exige dados reais, avaliação humana, revisão ética e monitoramento longitudinal. Esses resultados não podem ser fabricados dentro do repositório.

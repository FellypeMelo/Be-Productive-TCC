# Runbook operacional — sustainable-attention-v1

Este runbook descreve como operar a implementação sem transformar o resultado do ABM em alegação de eficácia.

## Antes da exposição

1. Revisar o manifesto `recommender/experiment_manifest.sustainable-attention-v1.json` e congelar a versão do algoritmo.
2. Confirmar protocolo, consentimento, faixa de elegibilidade, responsável e plano de poder fora do código.
3. Configurar `EXPERIMENT_ROLLOUT` no container do recommender para `0.05`, `0.25` ou `0.50`.
4. Reconstruir o serviço e registrar o digest da imagem. A atribuição permanece por usuário e não muda durante a rampa.

## Monitoramento

- `experimento_exposicao` é a fonte de exposição válida; `event_id` torna a gravação idempotente.
- Rodar o relatório ITT com dados agregados por participante:

```bash
docker compose run --rm --workdir /app --entrypoint sh recommender \
  -c 'PYTHONPATH=/app python -m src.evaluation.ab_report /path/to/aggregate.json'
```

- Interromper a janela se SRM (`p < 0,001`), erro crítico, segurança, acessibilidade ou retenção cruzar os limites do manifesto.
- Não usar rolagem, contexto, reserva, fricção ou tempo de tela bruto no arquivo de análise.

## Rollback

Rollback significa configurar `EXPERIMENT_ROLLOUT=0`, parar novas exposições e registrar a razão. Não apagar exposições já persistidas; elas permanecem auditáveis e são marcadas pela janela operacional fora deste serviço.

## Interpretação

O relatório calcula diferença tratamento − controle, IC95% e SRM. Ele não decide eficácia automaticamente, não substitui revisão humana e não autoriza claims clínicos ou de qualidade de vida sem protocolo aprovado.

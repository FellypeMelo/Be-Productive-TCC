# SPEC-AB-001 — A/B robusto para atenção sustentável

**Status:** implementação operacional inicial concluída; execução real ainda depende de protocolo, aprovação e amostra  
**Versão:** 1.0  
**Escopo:** experimento com usuários reais, consentido e separado do ABM  
**Princípio:** agência e reserva cognitiva > intenção declarada > eficiência > engajamento

## 1. Objetivo

Medir, com validade causal e proteção de privacidade, se o algoritmo Be-Productive melhora a retenção da intenção declarada e preserva a reserva cognitiva em comparação com um ranking de controle.

O experimento deve responder três perguntas diferentes:

1. O tratamento preserva mais reserva cognitiva ao longo do tempo?
2. O conteúdo consumido permanece mais alinhado à intenção declarada?
3. A proteção é aceita pelas pessoas sem aumentar abandono, frustração ou exposição a conteúdo inseguro?

O percentual de melhoria não será definido pelo resultado do ABM. O ABM (`N=1000`, `T=60`) é uma validação simulada e serve para testar o mecanismo e a instrumentação, não para estimar o efeito em pessoas reais.

## 2. Diagnóstico da implementação atual

O repositório já possui:

- atribuição determinística estável `control`/`treatment` por usuário;
- identificação de experimento e variante na resposta do recomendador;
- eventos de impressão, abertura, conclusão e ocultação;
- métricas offline de ranking;
- ABM sem confundimento e teste de sanidade;
- inferência de fadiga no dispositivo, sem envio de `v_scroll`, `v_alt`, reserva ou nível de fricção.

Isso ainda não constitui um A/B real completo. Atualmente, `ranking-v2` aplica a variante principalmente à diversificação do ranking; o ABM baseline versus sustentável não é automaticamente o experimento online. A coleta de eventos também é condicionada à personalização do produto, o que não pode substituir um consentimento de pesquisa específico.

## 3. Definição dos braços

### 3.1 Controle

Ranking atual de produção com:

- filtros de segurança obrigatórios;
- limites de qualidade e disponibilidade;
- afinidade mínima com tópicos declarados;
- nenhuma intervenção adicional de atenção sustentável que esteja sendo avaliada.

O controle nunca deve desligar autenticação, segurança, acessibilidade, proteção legal ou bloqueios de conteúdo crítico.

### 3.2 Tratamento

O mesmo ranking do controle, acrescido de um pacote versionado e inseparável de mecanismos sustentáveis:

- alinhamento à intenção declarada;
- qualidade e profundidade como objetivo dominante;
- penalidade de repetição e diversificação limitada;
- Min-Norm e classificação de segurança;
- modo protetivo acionado pela ordem booleana local;
- conteúdo denso durante estado impulsivo;
- fricção positiva e Pacto de Ulisses quando escolhidos pela pessoa.

O nome do pacote, seus parâmetros e a versão do modelo devem ser imutáveis durante cada execução do experimento.

### 3.3 O que não deve ser comparado

Não comparar o tratamento com um controle que exponha deliberadamente conteúdo inseguro. Não comparar uma versão visual com uma versão funcionalmente diferente sem registrar essa mudança. Não misturar, no mesmo resultado, o efeito do pacote inteiro com o efeito isolado da diversificação.

## 4. Elegibilidade e consentimento

Antes da atribuição, o sistema deve verificar:

- conta ativa e sessão autenticada;
- região e faixa etária elegíveis segundo o protocolo aprovado;
- consentimento explícito para participar do experimento;
- consentimento separado para métricas agregadas de bem-estar, quando aplicável;
- ausência de participação anterior em outro experimento incompatível;
- dispositivo capaz de executar a inferência local mínima.

Recusar participação não pode degradar o produto. Usuários sem consentimento recebem a experiência padrão e não entram no denominador analítico.

O experimento não deve inferir diagnóstico, transtorno, estado clínico ou vulnerabilidade médica. Qualquer escala validada de bem-estar exige protocolo ético próprio, linguagem não clínica e revisão humana.

## 5. Randomização e isolamento

### 5.1 Unidade de randomização

A unidade primária é `user_id`, não sessão, dispositivo ou impressão. A mesma pessoa deve permanecer no mesmo braço durante toda a execução.

Usar uma função versionada equivalente a:

```text
bucket = SHA-256(experiment_name + salt + user_id)
variant = control ou treatment
```

O `salt`, o nome, as datas e a regra de alocação devem ser registrados no manifesto do experimento. Nunca usar e-mail, nome ou um valor aleatório gerado a cada requisição.

### 5.2 Alocação

Começar com rollout de 5%, depois 25% e, somente após os critérios de segurança, 50/50. A rampa deve ser por usuário e não reatribuir participantes já expostos.

### 5.3 Interferência e contaminação

Registrar `experiment_id`, `variant`, `assignment_version` e `request_id` em cada exposição. Uma pessoa não pode aparecer em dois braços. Mudança de algoritmo ou de parâmetros cria uma nova versão do experimento; não editar retroativamente a anterior.

Durante a análise, excluir ou marcar separadamente:

- usuários que receberam menos de uma exposição válida;
- respostas de fallback;
- sessões sem consentimento vigente;
- períodos em que a configuração de emergência esteve ativa;
- tráfego automatizado, contas de teste e duplicatas.

## 6. Contrato de exposição

Cada resposta de feed elegível deve produzir um registro mínimo, independente da personalização comercial:

```json
{
  "event_id": "uuid",
  "experiment_id": "sustainable-attention-v1",
  "variant": "control|treatment",
  "assignment_version": "sha256-v1",
  "algorithm_version": "2.2.0-sustainable-attention",
  "request_id": "uuid",
  "user_id": "internal-id",
  "eligible": true,
  "served": true,
  "fallback": false,
  "position_count": 20,
  "created_at": "UTC"
}
```

O armazenamento deve aplicar os mesmos controles de acesso e retenção dos eventos de produto. O `user_id` não pode aparecer em logs públicos. Não incluir no evento dados brutos de rolagem, trocas de contexto, reserva, fricção, texto digitado ou histórico de navegação.

## 7. Métricas

### 7.1 Métrica primária

**AUC normalizada de reserva cognitiva por usuário durante os primeiros 7 dias após a primeira exposição**, calculada no dispositivo:

```text
auc_normalizada = integral(R(t) / R_max) / duração_observada
```

O cliente só pode enviar, sob consentimento específico, um resumo agregado limitado ao período, por exemplo `auc_normalizada` quantizada em faixas. O dado bruto e a série temporal permanecem no dispositivo.

Se o protocolo aprovado não permitir esse resumo, a métrica primária será a retenção da intenção declarada, e a reserva será usada apenas como métrica local de proteção.

### 7.2 Métricas secundárias

- retenção da categoria/objetivo declarado;
- divergência KL entre intenção e consumo agregado;
- conclusão voluntária de sessões de foco;
- aceitação de fricção e taxa de retorno após pausa;
- qualidade percebida por feedback explícito;
- cobertura e diversidade do catálogo;
- tempo até a primeira ação deliberada, sem otimizar tempo total de tela.

### 7.3 Guardrails

O tratamento deve ser interrompido ou revertido se houver deterioração estatisticamente e operacionalmente relevante em qualquer guardrail:

- conteúdo reportado ou bloqueio crítico;
- erros, latência e falhas de carregamento;
- abandono imediato após a intervenção;
- feedback “não relevante”;
- falha de acessibilidade ou aumento de suporte;
- exposição indevida a conteúdo repetitivo, inseguro ou fora do objetivo;
- diferença adversa por subgrupo pré-especificado.

Tempo de tela e cliques são métricas diagnósticas, nunca objetivo primário ou critério isolado de sucesso.

## 8. Tamanho de amostra e poder

Antes do rollout, o responsável deve registrar um plano de poder usando:

- `alpha = 0,05` bilateral;
- poder mínimo de 80% e preferencial de 90%;
- efeito mínimo detectável definido antes de olhar os resultados;
- perda, não exposição e correlação intrapessoa esperadas;
- correção para métricas secundárias e subgrupos.

Não dimensionar a amostra usando `Cohen’s d = 3,25` do ABM. Para planejamento conservador, iniciar com um efeito pequeno e plausível de usuário real, como `d = 0,20`, e recalcular após um piloto cego. O número final, a perda esperada e a justificativa devem ser anexados ao manifesto antes da alocação.

## 9. Plano estatístico

### 9.1 Análise principal

- intenção de tratar: analisar cada pessoa no braço originalmente atribuído;
- unidade de inferência: usuário;
- estimativa: diferença tratamento − controle na métrica primária;
- intervalo de confiança de 95%;
- modelo robusto a repetição de sessões por usuário;
- ajuste por estratos definidos antes do experimento, se existirem;
- resultado negativo ou inconclusivo deve ser reportado.

### 9.2 Análises secundárias

Análise por protocolo, heterogeneidade por dispositivo e efeito por nível inicial de intenção são exploratórias, salvo se pré-registradas. Não selecionar subgrupos depois de observar o efeito.

### 9.3 Monitoramento sequencial

Definir janelas de leitura e uma regra de alpha spending ou teste sequencial antes do início. Não interromper por olhar informal diário. Um painel operacional pode mostrar contagens e guardrails sem liberar o resultado inferencial antes da janela prevista.

### 9.4 Correções

Registrar o desfecho primário único. Controlar FDR ou hierarquia de testes para métricas secundárias. Não transformar uma métrica que melhorou em “primária” após o resultado.

## 10. Privacidade on-device

O princípio obrigatório é:

```text
rolagem/contexto → EdgeFatigueEngine local → ordem booleana → feed protegido
```

O servidor pode receber apenas:

- atribuição e exposição do experimento;
- eventos de produto consentidos;
- resumo agregado expressamente autorizado.

O servidor não pode receber `v_scroll`, `v_alt`, reserva atual, nível de fricção, sequência temporal ou reconstrução da navegação. Falha de rede deve manter o modo protetivo, não substituí-lo por feed irrestrito.

## 11. Rollout, parada e rollback

### Gate 0 — pré-lançamento

- protocolo e métricas aprovados;
- manifesto versionado;
- teste de balanceamento e teste de não-contaminação;
- ameaça à privacidade revisada;
- plano de rollback testado;
- dados sintéticos e fixtures reproduzíveis.

### Gate 1 — shadow

Calcular tratamento e controle sem alterar a experiência. Comparar latência, disponibilidade, ordenação, segurança e cobertura.

### Gate 2 — 5%

Verificar falhas, guardrails e distribuição por braço. Nenhum claim de eficácia nesta fase.

### Gate 3 — 25%

Verificar estabilidade, exposição suficiente e ausência de efeito adverso por subgrupo pré-especificado.

### Gate 4 — 50/50

Executar até atingir a amostra planejada ou uma regra de parada registrada.

Rollback imediato se houver risco de segurança, privacidade, indisponibilidade severa ou deterioração de um guardrail crítico. Rollback não apaga dados; marca a janela e a razão operacional.

## 12. Manifesto obrigatório

Cada execução deve ter um manifesto imutável contendo:

```yaml
experiment_id: sustainable-attention-v1
status: draft
assignment_version: sha256-v1
control: standard-ranking
treatment: sustainable-attention-package
allocation: 0.50
primary_metric: normalized_reserve_auc_7d
alpha: 0.05
power: 0.80
minimum_detectable_effect: 0.20
analysis_unit: user
analysis: intention_to_treat
start_at: null
end_at: null
stop_rules: []
consent_version: null
privacy_review: pending
```

O manifesto deve ser revisado por duas pessoas antes de `status: running` e arquivado junto com o resultado final.

## 13. Critérios de aceite técnico

1. Um usuário elegível recebe exatamente uma variante estável.
2. A distribuição de atribuição passa o teste de SRM pré-definido.
3. Nenhum usuário sem consentimento entra na análise.
4. Nenhum evento de exposição contém telemetria bruta de fadiga.
5. O evento de exposição é criado para controle e tratamento, mesmo com personalização comercial desligada, desde que exista consentimento de pesquisa.
6. Fallback, emergência e tráfego de teste são identificáveis e não contaminam a análise principal.
7. O tratamento pode ser desligado por configuração sem deploy destrutivo.
8. Os guardrails têm limiares, responsáveis e ação de rollback definidos.
9. O relatório reproduz a análise a partir do manifesto e de uma extração imutável.
10. Nenhum número do ABM é apresentado como efeito de usuário real.

## 14. Sequência de implementação

1. Separar `research_consent` de `personalizacao_ativa`.
2. Criar manifesto e configuração versionada do experimento.
3. Formalizar o contrato de exposição no OpenAPI e no backend.
4. Registrar atribuição/exposição de modo idempotente.
5. Criar agregador local de reserva e intenção com opt-in explícito.
6. Implementar validação de SRM, balanceamento e não-contaminação.
7. Criar pipeline offline de análise ITT com intervalos de confiança.
8. Adicionar painel operacional de guardrails sem revelar o resultado inferencial.
9. Executar shadow e piloto de 5%.
10. Só então iniciar a coleta do A/B 50/50.

## 15. Fora de escopo

- usar o A/B para diagnosticar saúde mental;
- vender ou compartilhar telemetria individual;
- otimizar para tempo de tela, cliques ou retenção isoladamente;
- usar o resultado do ABM como prova clínica;
- substituir revisão ética por aprovação técnica;
- enviar rolagem, contexto ou reserva bruta ao servidor.

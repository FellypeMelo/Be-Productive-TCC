# Reprodutibilidade científica

Este documento explica como reproduzir, do zero, o resultado que sustenta o artigo — e por que ele é metodologicamente honesto.

## Executar o experimento

```bash
cd recommender
python -m venv venv && venv\Scripts\activate      # Windows (ou: source venv/bin/activate)
pip install -r requirements.txt
python -m src.abm.run_simulation
```

Saídas regeneradas em `recommender/abm_results/`:

- `statistical_proof.md` — Cohen's d, p-valor, **tabela de ablação** e **teste de sanidade**
- `fig_1_ego_depletion.png` — distribuição da reserva cognitiva retida (Fig. 1)
- `fig_2_kl_divergence.png` — divergência KL intenção × consumo (Fig. 2)
- `fig_3_robustness_manifold.png` — manifold de robustez (Fig. 3)

## Resultado esperado (N = 1000, T = 60, semente 42)

| Métrica | Valor |
|---|---|
| Cohen's d (AUC de reserva) | **3.25** |
| Cohen's d (métrica limitada R_final/R_max) | 3.62 |
| p (Mann-Whitney U) | ≈ 3.8 × 10⁻²⁹⁵ |
| KL mediana (baseline → Be-Productive) | 0.87 → 0.21 |

### Ablação — atribuição causal

| Configuração | Cohen's d | KL mediana (sust.) |
|---|---|---|
| Modelo completo | 3.25 | 0.21 |
| Somente fricção | 2.57 | 0.87 |
| Somente min-norm | 0.35 | 0.87 |
| Somente steering (TS + Hawkes) | ≈ 0 | 0.21 |
| **Nenhum (sanidade)** | **≈ 0.02** | 0.87 |

## Por que é justo (sem confundimento)

A versão anterior do motor embutia o resultado: dava recuperação (`μ_rest`) só ao braço tratado e fixava um scroll 3× menor à mão. Aqui:

- **`μ_rest` é idêntico nos dois braços** — recuperação é propriedade do humano, não do algoritmo.
- **A carga emerge** do conteúdo servido (compulsividade) e da fricção; não é fixada por braço.
- A única diferença entre os braços são as **ações do algoritmo** (min-norm, fricção, steering).

O **teste de sanidade** prova isso: com todos os mecanismos desligados, o braço sustentável degenera no baseline e `d ≈ 0`. O efeito não está no arcabouço — é gerado pelos mecanismos.

## Testes automatizados

```bash
cd recommender && python -m pytest src/ -q          # 89 testes
```

Inclui `src/abm/tests/test_fair_validation.py`, que reproduz `d = 3.25` de uma execução semeada, verifica a sanidade (`d ≈ 0`) e a ordenação da ablação. Sementes de **numpy e do módulo `random`** são fixadas → reprodutibilidade estrita.

## Relação com o artigo

As figuras nas eventuais pastas do artigo permanecem as **publicadas** (o artigo não é alterado). As figuras honestas geradas pelo código vivem em `recommender/abm_results/`. O número 3.25 é o mesmo do artigo — agora produzido por um desenho defensável.

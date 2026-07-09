# Prova Estatística de Robustez (Be-Productive) — versão justa

Experimento sem confundimento: recuperação cognitiva (μ_rest) idêntica nos dois braços; a carga (v_scroll, v_alt) emerge do conteúdo servido e da fricção positiva. As únicas diferenças entre os braços são as ações do algoritmo.

## Resultado principal (N=1000, T=60)

- **Effect Size (Cohen's d, AUC de reserva):** 3.25
- **Effect Size (métrica limitada R_final/R_max):** 3.62  (métrica conservadora que não acumula ao longo da sessão)
- **P-Value (Mann-Whitney U):** 3.828e-295 (reportar como p < 10⁻³⁰⁰ quando abaixo do menor float)
- **Divergência KL mediana:** baseline 0.874 vs Be-Productive 0.205

## Ablação — atribuição causal do efeito

| Configuração | Cohen's d (AUC) | KL mediana (sust.) |
|---|---|---|
| Modelo completo | 3.25 | 0.205 |
| Somente min-norm | 0.35 | 0.870 |
| Somente fricção | 2.57 | 0.870 |
| Somente steering (TS+Hawkes) | -0.01 | 0.205 |
| Nenhum (sanidade) | 0.02 | 0.870 |

O **teste de sanidade** (nenhum mecanismo ativo) produz d ≈ 0, confirmando que o efeito NÃO está embutido no arcabouço: ele é gerado pelos mecanismos.

## Sensibilidade / Manifold de Robustez

Delta de bem-estar (AUC sustentável − baseline) varre de 1 a 1216 ao longo do grid (redução de scroll × vulnerabilidade k1), permanecendo positivo em todos os quadrantes — o ganho não é um ponto ótimo frágil.

Sementes fixas (numpy + random) garantem reprodutibilidade estrita.

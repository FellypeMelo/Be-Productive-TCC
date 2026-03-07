import numpy as np
from scipy import stats

def calculate_p_value(group_a, group_b) -> float:
    """
    Calcula o P-Value usando o Wilcoxon Rank-Sum Test (Mann-Whitney U).
    Ideal para distribuições que não são necessariamente normais (como a saúde cognitiva).
    """
    # Se os grupos forem idênticos, o teste pode lançar erro ou p=1.0
    if np.array_equal(group_a, group_b):
        return 1.0
    
    # Mann-Whitney U test (não paramétrico)
    _, p_val = stats.mannwhitneyu(group_a, group_b, alternative='two-sided')
    return float(p_val)

def calculate_effect_size(group_sust, group_base) -> float:
    """
    Calcula o Cohen's d para mensurar a magnitude do efeito.
    Fórmula: (mean_sust - mean_base) / pooled_std
    """
    n1, n2 = len(group_sust), len(group_base)
    v1, v2 = np.var(group_sust, ddof=1), np.var(group_base, ddof=1)
    
    # Pooled standard deviation
    pooled_std = np.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2))
    
    if pooled_std == 0:
        return 0.0
        
    return (np.mean(group_sust) - np.mean(group_base)) / pooled_std

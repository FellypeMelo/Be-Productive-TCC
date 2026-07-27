# Academic purpose and interdisciplinary impact

## Academic purpose

Be-Productive originated as an academic project at **FAETERJ-RIO** and was consolidated in the peer-reviewed paper:

> *Arquitetura Algorítmica para Atenção Sustentável: O Modelo Be-Productive como Resposta à Sobrecarga Cognitiva no Capitalismo de Vigilância.* Revista Tópicos (ISSN 2965-6672, Qualis A2). DOI: [10.70773/revistatopicos/781363235](https://doi.org/10.70773/revistatopicos/781363235).

The paper positions the architecture as a **technical possibility** — proof that it *is viable* to recommend content while protecting cognitive reserve. This repository is the reference implementation that makes that possibility executable, auditable, and reproducible, **without altering the paper**.

Central goal: to show, with engineering evidence, that **algorithmic efficiency doesn't have to be predatory**.

## How the project can help other fields

The paper is classified under **Engineering, Health Sciences, and Applied Social Sciences**. The underlying math (the depletion ODE, Hawkes processes, Min-Norm filtering, Thompson Sampling) and the Edge-AI architecture are reusable well beyond computer science:

### Health

- **Clinical psychology / mental health** — instrumenting studies of attentional fatigue, digital dependency, ADHD, and cognitive relapse; the cognitive-reserve ODE is a formal model of depletion and recovery.
- **Public health** — evidence for digital-wellbeing programs and population-level attentional hygiene.
- **Neuroscience of attention** — a computational testbed for simulating depletion/re-engagement (System 1 vs. System 2).

### Education

- **EdTech** — study environments and LMS platforms that protect deep deliberation (System 2) instead of fragmenting it; concrete support for "learning to focus."
- **Educational research** — measuring the divergence between declared study intent and actual consumption (KL divergence).

### Applied social sciences & policy

- **Digital law & regulation** — a technical reference point for algorithmic transparency and risk mitigation (e.g., the Digital Services Act).
- **Ethics & privacy** — Edge AI and *privacy by design* as an LGPD/GDPR compliance pattern (on-device inference, behavioral anonymity).
- **Behavioral economics** — operationalizing the "Ulysses Pact," hyperbolic discounting, and pre-commitment in software.

### Computing & industry

- **Recommender systems (research)** — a replicable Value-Aligned RecSys framework: multi-objective Min-Norm filtering, deliberative steering, honest ablation.
- **Human-Computer Interaction / ethical UX** — "positive friction" as a design pattern.
- **Organizational productivity / HR** — a foundation for B2B focus and corporate wellbeing tools.

## How to reuse it

- The pure math lives in `recommender/src/domain/` and is cleanly dependency-free (testable without a framework).
- The ABM validation (`recommender/src/abm/`) is a parameterizable simulation testbed (impulsivity, vulnerability, intervention strength).
- The on-device fatigue engine (`frontend/src/lib/fatigue.ts`) is a self-contained TypeScript module.

See [reproducibility.md](reproducibility.md) to run the testbed and [paper-code-truth-map.md](paper-code-truth-map.md) for the claim↔code map.

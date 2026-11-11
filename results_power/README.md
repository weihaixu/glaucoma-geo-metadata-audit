# Post-hoc detectable effect size (MDE) - sensitivity only

- Input: `results/04_deg_primary_M2.csv` (69,513 probe-level primary M2 fits).
- Method: two-sided alpha=0.05, target power=0.80, solved with the noncentral t distribution from each probe's SE and residual df. MDE does **not** use the observed effect size, so it is not the classical post-hoc-power fallacy.
- Outputs: `01_platform_mde.csv`, `02_six_genes_mde.csv`, `tables/TableS13_power_mde.tsv|.md`.
- **Interpretation limit:** a non-significant BH q >= 0.05 in an underpowered, structurally imbalanced design is *not* evidence of no effect. If |log2FC| < MDE, the data cannot exclude a smaller true effect. Do not write 'no effect', 'equivalent' or 'confirmed negative' anywhere in the manuscript.
- `results/`, `results_m2b/`, `results_limma/` and all figures/tables 1-4 / S1-S12 are untouched. This is a NEW supplementary analysis, not a replacement of M2.

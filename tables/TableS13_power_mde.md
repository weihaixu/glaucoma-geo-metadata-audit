# Table S13. Post-hoc detectable effect size for the six transcripts (primary M2)

Descriptive sensitivity analysis derived from `results/04_deg_primary_M2.csv`; two-sided alpha = 0.05, target power = 0.80, noncentral-t solution using each probe's standard error and residual df. **Not** an a-priori power calculation and **not** a test of equivalence or absence of effect. Primary results are unchanged.

| Platform | Gene | log2FC | 95% CI | MDE (power 80%) | q_BH |
|---|---|---:|---|---:|---:|
| GSE2378-GPL8300 | CASP1 | 1.921 | [1.006, 2.836] | 1.279 | 0.224 |
| GSE2378-GPL8300 | CASP4 | 0.784 | [0.327, 1.240] | 0.638 | 0.290 |
| GSE2378-GPL8300 | FGFR1 | 0.729 | [0.228, 1.230] | 0.701 | 0.354 |
| GSE2378-GPL8300 | SMAD1 | 0.845 | [0.351, 1.339] | 0.691 | 0.290 |
| GSE2378-GPL8300 | STAT1 | -0.821 | [-1.443, -0.199] | 0.870 | 0.433 |
| GSE2378-GPL8300 | TGFBR2 | 0.603 | [0.308, 0.898] | 0.412 | 0.227 |
| GSE9944-GPL571 | CASP1 | 1.075 | [0.208, 1.942] | 1.223 | 0.145 |
| GSE9944-GPL571 | CASP4 | 0.669 | [0.101, 1.237] | 0.801 | 0.170 |
| GSE9944-GPL571 | FGFR1 | -0.445 | [-0.874, -0.015] | 0.605 | 0.238 |
| GSE9944-GPL571 | SMAD1 | 0.878 | [-0.015, 1.772] | 1.260 | 0.267 |
| GSE9944-GPL571 | STAT1 | -1.132 | [-2.133, -0.130] | 1.412 | 0.191 |
| GSE9944-GPL571 | TGFBR2 | 0.405 | [-0.267, 1.078] | 0.949 | 0.544 |
| GSE9944-GPL8300 | CASP1 | 0.467 | [0.198, 0.736] | 0.377 | 0.356 |
| GSE9944-GPL8300 | CASP4 | 0.740 | [0.121, 1.360] | 0.869 | 0.543 |
| GSE9944-GPL8300 | FGFR1 | 0.440 | [0.046, 0.834] | 0.553 | 0.576 |
| GSE9944-GPL8300 | SMAD1 | 0.458 | [-0.025, 0.940] | 0.677 | 0.679 |
| GSE9944-GPL8300 | STAT1 | -0.968 | [-1.596, -0.340] | 0.881 | 0.428 |
| GSE9944-GPL8300 | TGFBR2 | 0.484 | [-0.045, 1.012] | 0.742 | 0.691 |

## Platform-level summary

| Platform | Probes | Residual df | Median SE | Typical MDE | Probes with power>=80% at abs(log2FC)=1 |
|---|---:|---:|---:|---:|---:|
| GSE2378-GPL8300 | 12625 | 11 | 0.3711 | 1.142 | 43.52% |
| GSE45570 | 22011 | 10 | 0.1464 | 0.455 | 95.28% |
| GSE9944-GPL571 | 22277 | 18 | 0.1258 | 0.373 | 90.71% |
| GSE9944-GPL8300 | 12600 | 13 | 0.1348 | 0.409 | 94.24% |

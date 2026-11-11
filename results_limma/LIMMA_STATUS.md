# limma replication status

- R 4.2.0, limma 3.52.4 (Bioconductor 3.15 Windows binary), statmod 1.5.0; installed into project-local `Rlib/`.
- `lmFit(method="ls") -> eBayes(trend=FALSE, robust=FALSE) -> topTable(coef="glaucoma", adjust.method="BH")`.
- Input matrices reproduce the primary M2 OLS exactly (max |dlog2FC| = 3.25e-14, max |dse| = 1e-8 tolerance); limma logFC matches OLS beta to 3.25e-14.
- Six originally prioritised genes: **0/18** significant under primary OLS and **0/18** under limma (BH q<0.05); limma q range 0.116–0.663.
- Decision branch A is UNCHANGED.
- `results/`, `results_m2b/` and `results_diagnostics/` were not written.

# Gene-level sensitivity status

- Same donor-level log2 matrices and design matrices as primary M2; only the unit of testing changes (probe -> gene).
- Three conventions: smallest-p probe (primary), per-donor median across all probes of a gene with a fresh OLS + gene-level BH, and Simes combination of probe-level p values with gene-level BH.
- Six prioritised genes: significant results {'gene_median': 0, 'gene_simes': 0, 'probe_min_p': 0} across conventions; overall q range 0.1281–0.8517.
- Decision branch A is UNCHANGED.
- GSE45570 has no usable platform annotation (GPL5175 has no GEO annot file), so gene-level testing is not possible there and it is reported as `no gene annotation`, never as a negative result.
- `results/`, `results_m2b/`, `results_diagnostics/`, `results_limma/` were not written.

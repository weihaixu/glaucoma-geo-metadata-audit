# Facts for manuscript back-filling (auto-generated)

> Source: `results/*.csv` from `reanalysis.py` on REAL GEO series matrices. `_selftest_results/` is synthetic and must never be cited.


## 1. Design / QC (02_qc_summary.csv)

| dataset | arrays | donors | groups | ancestry x group | scale | annotation | design warning |
|---|---|---|---|---|---|---|---|
| GSE2378-GPL8300 | 13 | 13 | {"glaucoma": 7, "control": 6} | {"UNKNOWN": {"control": 6, "glaucoma": 7}} | linear | GPL8300.annot.gz | none detected |
| GSE2378-GPL91 | 2 | 2 | {"glaucoma": 1, "control": 1} | {"UNKNOWN": {"control": 1, "glaucoma": 1}} | linear | GPL91.annot.gz | only 1 glaucoma / 1 control donors - underpowered |
| GSE45570 | 12 | 12 | {"glaucoma": 6, "control": 6} | {"UNKNOWN": {"control": 6, "glaucoma": 6}} | log2 | MISSING - no gene symbols | none detected |
| GSE9944-GPL571 | 42 | 21 | {"control": 18, "glaucoma": 3} | {"African_American": {"control": 9, "glaucoma": 3}, "Caucasian": {"control": 9, "glaucoma": 0}} | log2 | GPL571.annot.gz | only 3 glaucoma / 18 control donors - underpowered; ALL glaucoma donors share one ancestry: race and disease are nearly collinear; the adjusted disease coefficient is not interpretable |
| GSE9944-GPL8300 | 19 | 16 | {"glaucoma": 10, "control": 6} | {"African_American": {"control": 0, "glaucoma": 3}, "Caucasian": {"control": 6, "glaucoma": 7}} | log2 | GPL8300.annot.gz | none detected |
| GSE9944-GPL91 | 2 | 2 | {"glaucoma": 1, "control": 1} | {"Caucasian": {"control": 1, "glaucoma": 1}} | log2 | GPL91.annot.gz | only 1 glaucoma / 1 control donors - underpowered; ALL glaucoma donors share one ancestry: race and disease are nearly collinear; the adjusted disease coefficient is not interpretable |

## 2. DEG counts by model (03_deg_by_model.csv)

| dataset | model | n DE probes | probes tested | residual df | note |
|---|---|---|---|---|---|
| GSE2378-GPL8300 | M0_array_nominal | 748 | 12625 | 11 | nan |
| GSE2378-GPL8300 | M1_donor_nominal | 748 | 12625 | 11 | nan |
| GSE2378-GPL8300 | M2_donor_adjusted_FDR_LFC1 | 1 | 12625 | 11 | ADJUSTMENT NOT POSSIBLE: race missing in GEO metadata |
| GSE2378-GPL8300 | M3_donor_adjusted_FDR_LFC05 | 2 | 12625 | 11 | ADJUSTMENT NOT POSSIBLE: race missing in GEO metadata |
| GSE45570 | M0_array_nominal | 89 | 22011 | 10 | nan |
| GSE45570 | M1_donor_nominal | 89 | 22011 | 10 | nan |
| GSE45570 | M2_donor_adjusted_FDR_LFC1 | 0 | 22011 | 10 | ADJUSTMENT NOT POSSIBLE: race missing in GEO metadata |
| GSE45570 | M3_donor_adjusted_FDR_LFC05 | 0 | 22011 | 10 | ADJUSTMENT NOT POSSIBLE: race missing in GEO metadata |
| GSE9944-GPL571 | M0_array_nominal | 1375 | 22277 | 40 | nan |
| GSE9944-GPL571 | M1_donor_nominal | 1075 | 22277 | 19 | nan |
| GSE9944-GPL571 | M2_donor_adjusted_FDR_LFC1 | 114 | 22277 | 18 | nan |
| GSE9944-GPL571 | M3_donor_adjusted_FDR_LFC05 | 640 | 22277 | 18 | nan |
| GSE9944-GPL8300 | M0_array_nominal | 472 | 12600 | 17 | nan |
| GSE9944-GPL8300 | M1_donor_nominal | 337 | 12600 | 14 | nan |
| GSE9944-GPL8300 | M2_donor_adjusted_FDR_LFC1 | 0 | 12600 | 13 | nan |
| GSE9944-GPL8300 | M3_donor_adjusted_FDR_LFC05 | 0 | 12600 | 13 | nan |

## 3. Six originally prioritized genes, primary M2 model (05_six_key_genes.csv)

| dataset | gene | probes | log2FC | nominal p | BH q | status |
|---|---|---|---|---|---|---|
| GSE2378-GPL8300 | FGFR1 | 4 | 0.7289 | 0.008441 | 0.3535 | not significant (BH q>=.05) |
| GSE2378-GPL8300 | SMAD1 | 2 | 0.845 | 0.003122 | 0.2904 | not significant (BH q>=.05) |
| GSE2378-GPL8300 | STAT1 | 8 | -0.821 | 0.01434 | 0.4332 | not significant (BH q>=.05) |
| GSE2378-GPL8300 | TGFBR2 | 2 | 0.6027 | 0.0009035 | 0.2271 | not significant (BH q>=.05) |
| GSE2378-GPL8300 | CASP1 | 2 | 1.921 | 0.0007374 | 0.2241 | not significant (BH q>=.05) |
| GSE2378-GPL8300 | CASP4 | 1 | 0.7835 | 0.003057 | 0.2902 | not significant (BH q>=.05) |
| GSE45570 | FGFR1 | 0 | nan | nan | nan | no probe mapped |
| GSE45570 | SMAD1 | 0 | nan | nan | nan | no probe mapped |
| GSE45570 | STAT1 | 0 | nan | nan | nan | no probe mapped |
| GSE45570 | TGFBR2 | 0 | nan | nan | nan | no probe mapped |
| GSE45570 | CASP1 | 0 | nan | nan | nan | no probe mapped |
| GSE45570 | CASP4 | 0 | nan | nan | nan | no probe mapped |
| GSE9944-GPL571 | FGFR1 | 6 | -0.4447 | 0.04307 | 0.2377 | not significant (BH q>=.05) |
| GSE9944-GPL571 | SMAD1 | 2 | 0.8784 | 0.05356 | 0.2668 | not significant (BH q>=.05) |
| GSE9944-GPL571 | STAT1 | 6 | -1.132 | 0.02889 | 0.1912 | not significant (BH q>=.05) |
| GSE9944-GPL571 | TGFBR2 | 2 | 0.4053 | 0.2217 | 0.5436 | not significant (BH q>=.05) |
| GSE9944-GPL571 | CASP1 | 5 | 1.075 | 0.01791 | 0.1455 | not significant (BH q>=.05) |
| GSE9944-GPL571 | CASP4 | 2 | 0.669 | 0.02346 | 0.1702 | not significant (BH q>=.05) |
| GSE9944-GPL8300 | FGFR1 | 4 | 0.4401 | 0.03129 | 0.5755 | not significant (BH q>=.05) |
| GSE9944-GPL8300 | SMAD1 | 2 | 0.4576 | 0.06123 | 0.6791 | not significant (BH q>=.05) |
| GSE9944-GPL8300 | STAT1 | 8 | -0.9682 | 0.005423 | 0.4283 | not significant (BH q>=.05) |
| GSE9944-GPL8300 | TGFBR2 | 2 | 0.4837 | 0.0696 | 0.6911 | not significant (BH q>=.05) |
| GSE9944-GPL8300 | CASP1 | 2 | 0.4668 | 0.002432 | 0.3559 | not significant (BH q>=.05) |
| GSE9944-GPL8300 | CASP4 | 1 | 0.7402 | 0.02282 | 0.5427 | not significant (BH q>=.05) |

- Mapped gene x dataset tests: **18**; with BH q<0.05: **0**.

## 4. External comparison (06_external_validation.csv)

| dataset | gene | probes | log2FC | p | BH q | AUC | 95% CI | perm p | status |
|---|---|---|---|---|---|---|---|---|---|
| GSE2378-GPL8300 | FGFR1 | 4 | 0.729 | 0.00844 | 0.354 | 0.976 | 0.857-1 | 0.002 | NOT replicated |
| GSE2378-GPL8300 | SMAD1 | 2 | 0.845 | 0.00312 | 0.29 | 0.881 | 0.571-1 | 0.013 | NOT replicated |
| GSE2378-GPL8300 | STAT1 | 8 | -0.821 | 0.0143 | 0.433 | 0.119 | 0-0.333 | 0.994 | NOT replicated |
| GSE2378-GPL8300 | TGFBR2 | 2 | 0.603 | 0.000903 | 0.227 | 1 | 1-1 | 0.002 | NOT replicated |
| GSE2378-GPL8300 | CASP1 | 2 | 1.92 | 0.000737 | 0.224 | 0.976 | 0.857-1 | 0.002 | NOT replicated |
| GSE2378-GPL8300 | CASP4 | 1 | 0.784 | 0.00306 | 0.29 | 0.929 | 0.762-1 | 0.004 | NOT replicated |
| GSE45570 | FGFR1 | 0 | nan | nan | nan | nan | nan-nan | nan | probe not mapped |
| GSE45570 | SMAD1 | 0 | nan | nan | nan | nan | nan-nan | nan | probe not mapped |
| GSE45570 | STAT1 | 0 | nan | nan | nan | nan | nan-nan | nan | probe not mapped |
| GSE45570 | TGFBR2 | 0 | nan | nan | nan | nan | nan-nan | nan | probe not mapped |
| GSE45570 | CASP1 | 0 | nan | nan | nan | nan | nan-nan | nan | probe not mapped |
| GSE45570 | CASP4 | 0 | nan | nan | nan | nan | nan-nan | nan | probe not mapped |

## 5. Donor overlap across matrices (10_donor_overlap.csv)

| A | B | donors A | donors B | shared | interpretation |
|---|---|---|---|---|---|
| GSE2378-GPL8300 | GSE2378-GPL91 | 13 | 2 | 0 | SAME GEO SERIES but no shared donor IDs in titles - still one experiment, not an independe |
| GSE2378-GPL8300 | GSE45570 | 13 | 12 | 0 | DIFFERENT SERIES - verify donor provenance before claiming independence |
| GSE2378-GPL8300 | GSE9944-GPL571 | 13 | 21 | 0 | DIFFERENT SERIES - verify donor provenance before claiming independence |
| GSE2378-GPL8300 | GSE9944-GPL8300 | 13 | 16 | 0 | DIFFERENT SERIES - verify donor provenance before claiming independence |
| GSE2378-GPL8300 | GSE9944-GPL91 | 13 | 2 | 0 | DIFFERENT SERIES - verify donor provenance before claiming independence |
| GSE2378-GPL91 | GSE45570 | 2 | 12 | 0 | DIFFERENT SERIES - verify donor provenance before claiming independence |
| GSE2378-GPL91 | GSE9944-GPL571 | 2 | 21 | 0 | DIFFERENT SERIES - verify donor provenance before claiming independence |
| GSE2378-GPL91 | GSE9944-GPL8300 | 2 | 16 | 0 | DIFFERENT SERIES - verify donor provenance before claiming independence |
| GSE2378-GPL91 | GSE9944-GPL91 | 2 | 2 | 0 | DIFFERENT SERIES - verify donor provenance before claiming independence |
| GSE45570 | GSE9944-GPL571 | 12 | 21 | 0 | DIFFERENT SERIES - verify donor provenance before claiming independence |
| GSE45570 | GSE9944-GPL8300 | 12 | 16 | 0 | DIFFERENT SERIES - verify donor provenance before claiming independence |
| GSE45570 | GSE9944-GPL91 | 12 | 2 | 0 | DIFFERENT SERIES - verify donor provenance before claiming independence |
| GSE9944-GPL571 | GSE9944-GPL8300 | 21 | 16 | 5 | SAME GEO SERIES - overlapping donors / arrays are technical replication, NOT independent v |
| GSE9944-GPL571 | GSE9944-GPL91 | 21 | 2 | 0 | SAME GEO SERIES but no shared donor IDs in titles - still one experiment, not an independe |
| GSE9944-GPL8300 | GSE9944-GPL91 | 16 | 2 | 0 | SAME GEO SERIES but no shared donor IDs in titles - still one experiment, not an independe |

## 6. Automatic decision-tree branch

- Six-gene tests with BH q<0.05: **0** of 18 mapped -> branch **A**.
- Total M2 DEG probes across all platforms: **115**.
- Rule: A = no gene survives -> stop calling them candidates; re-position as a methodological re-assessment. B/C = 1-2 / >=3 survive. D = whole DEG list collapses.


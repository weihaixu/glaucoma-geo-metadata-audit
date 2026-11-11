# Table S17. Cross-tissue directional concordance of the six pre-specified transcripts in GSE27276

Exploratory **cross-tissue directional concordance only**. GSE27276 profiles human trabecular meshwork on GPL2507 from a different laboratory with a different case definition. It is **not an independent replication or validation**. Disease is perfectly confounded with tissue procurement and postmortem delay, and no ancestry/age/sex covariates are deposited, so the coefficient is `intercept + glaucoma` only. BH q is computed across all matrix probes within each unit convention; 95% CIs are nominal. Values are for the probe with the smallest nominal p within each gene.

| Convention | Gene | n probes | log2FC | nominal 95% CI | p | BH q | Status |
|---|---|---:|---:|---|---:|---:|---|
| array_level | TGFBR2 | 1 | +0.036 | [-0.053, +0.124] | 0.4173 | 0.7696 | not significant (BH q>=0.05) |
| array_level | SMAD1 | 2 | -0.050 | [-0.147, +0.046] | 0.2971 | 0.6840 | not significant (BH q>=0.05) |
| array_level | STAT1 | 3 | +0.283 | [-0.038, +0.604] | 0.08201 | 0.4195 | not significant (BH q>=0.05) |
| array_level | CASP1 | 2 | +0.076 | [-0.003, +0.154] | 0.05738 | 0.3604 | not significant (BH q>=0.05) |
| array_level | FGFR1 | 2 | -0.054 | [-0.164, +0.057] | 0.3294 | 0.7098 | not significant (BH q>=0.05) |
| array_level | CASP4 | 2 | -0.266 | [-0.735, +0.203] | 0.2575 | 0.6499 | not significant (BH q>=0.05) |
| donor_metadata | TGFBR2 | 1 | +0.035 | [-0.059, +0.129] | 0.4557 | 0.7789 | not significant (BH q>=0.05) |
| donor_metadata | SMAD1 | 2 | -0.048 | [-0.142, +0.046] | 0.3023 | 0.6701 | not significant (BH q>=0.05) |
| donor_metadata | STAT1 | 3 | +0.344 | [-0.019, +0.707] | 0.0625 | 0.3577 | not significant (BH q>=0.05) |
| donor_metadata | CASP1 | 2 | +0.074 | [-0.000, +0.148] | 0.05121 | 0.3298 | not significant (BH q>=0.05) |
| donor_metadata | FGFR1 | 2 | +0.033 | [-0.050, +0.117] | 0.4203 | 0.7567 | not significant (BH q>=0.05) |
| donor_metadata | CASP4 | 2 | -0.272 | [-0.764, +0.219] | 0.2661 | 0.6391 | not significant (BH q>=0.05) |
| donor_declared | TGFBR2 | 1 | +0.035 | [-0.063, +0.134] | 0.4682 | 0.8049 | not significant (BH q>=0.05) |
| donor_declared | SMAD1 | 2 | -0.042 | [-0.129, +0.046] | 0.3346 | 0.7186 | not significant (BH q>=0.05) |
| donor_declared | STAT1 | 3 | +0.342 | [-0.042, +0.726] | 0.07826 | 0.4332 | not significant (BH q>=0.05) |
| donor_declared | CASP1 | 2 | +0.069 | [-0.008, +0.147] | 0.07663 | 0.4297 | not significant (BH q>=0.05) |
| donor_declared | FGFR1 | 2 | +0.038 | [-0.046, +0.122] | 0.3604 | 0.7364 | not significant (BH q>=0.05) |
| donor_declared | CASP4 | 2 | -0.312 | [-0.834, +0.209] | 0.2288 | 0.6331 | not significant (BH q>=0.05) |

## Directional agreement with the primary discovery platforms

Descriptive sign counts for six transcripts; **no p-value or inferential test** was computed (n = 6 genes, cross-tissue, non-independent probes).

| Convention | Primary platform | Sign agreement |
|---|---|---:|
| array_level | GSE2378-GPL8300 | 2/6 (33.3%) |
| array_level | GSE9944-GPL571 | 3/6 (50.0%) |
| array_level | GSE9944-GPL8300 | 2/6 (33.3%) |
| donor_declared | GSE2378-GPL8300 | 3/6 (50.0%) |
| donor_declared | GSE9944-GPL571 | 2/6 (33.3%) |
| donor_declared | GSE9944-GPL8300 | 3/6 (50.0%) |
| donor_metadata | GSE2378-GPL8300 | 3/6 (50.0%) |
| donor_metadata | GSE9944-GPL571 | 2/6 (33.3%) |
| donor_metadata | GSE9944-GPL8300 | 3/6 (50.0%) |

Primary reference values are the min-p probe per gene from the frozen `results/04_deg_primary_M2.csv` (Table 2). Directional concordance is descriptive only (n=6 transcripts; no inference, no p-value). Disease is perfectly confounded with tissue procurement and postmortem delay, so any case-control contrast in this series is not interpretable as a disease effect. The six-gene result must not be used to support or refute the primary 0/18 finding.

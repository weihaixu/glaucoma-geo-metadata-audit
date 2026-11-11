# results_external/ -- GSE27276 stress test (round 13, P1-b)

**Read this before using any number in this directory.**

This is a cross-tissue directional-concordance exercise and a stress test of `geo_metadata_audit.py`. It is **not** an independent replication, not a validation cohort, and not confirmatory evidence for the six transcripts.

- Tissue: human trabecular meshwork (primary work used ONH astrocytes / whole ONH).
- Laboratory, platform (GPL2507, Illumina Sentrix Human-6), and case definition differ.
- Disease is **perfectly confounded** with collection method (surgery vs donated eye) and postmortem delay (0 vs >0), so the case-control coefficient cannot be interpreted as a disease effect (`09_confounding_audit.csv`).
- No ancestry/age/sex fields are deposited; the pre-specified M2 design reduces to `[1, glaucoma]` and every probe row is flagged `ADJUSTMENT NOT POSSIBLE`.

## Three unit conventions

| Convention | Units | POAG | Control | Residual df | Meaning |
|---|---:|---:|---:|---:|---|
| `array_level` | 36 | 17 | 19 | 34 | All 36 deposited arrays treated as independent (the naive reuse). |
| `donor_metadata` | 30 | 17 | 13 | 28 | Controls collapsed by postmortem delay (13 donors); POAG arrays left separate because deposited metadata cannot pair them. Known residual pseudo-replication on the case side. |
| `donor_declared` | 28 | 15 | 13 | 26 | As donor_metadata plus two disjoint highest-correlation POAG pairs merged by averaging, reproducing the declared 15 cases / 13 controls. The second merge is an unverifiable, data-driven assumption. |

GEO declares 13 controls + 15 POAG = 28 donors but deposits 36 arrays. The 19 control arrays collapse unambiguously to 13 donors by identical postmortem delay (six paired-eye donors), corroborated by expression correlation. All 17 POAG arrays have delay 0, so the two case-side merges in `donor_declared` are **data-driven and the second is unverifiable**. This residual ambiguity is the finding, not a defect to be hidden.

## Files

| File | Content |
|---|---|
| `01_array_metadata.csv` | 36 arrays, GSM, title, group, collection, delay |
| `02_donor_map.csv` | unit definitions per convention and reconstruction basis |
| `03_probe_gene_map.csv` | GPL2507 probe -> Gene symbol (mapped probes only) |
| `04_OLS_array_level.csv` | all-probe OLS, 36 arrays (naive) |
| `05_OLS_donor_metadata.csv` | all-probe OLS, 30 metadata-defined units |
| `06_OLS_donor_declared.csv` | all-probe OLS, 28 declared-design units |
| `07_six_genes_all_conventions.csv` | six transcripts, min-p probe + median, all conventions |
| `08_directional_concordance.csv` | sign comparison vs three primary discovery platforms |
| `09_confounding_audit.csv` | metadata defects and rank check |
| `10_sign_agreement_summary.csv` | descriptive sign-agreement counts (no p-values) |
| `external_summary.json` | machine-readable summary + sha256 of inputs/primary file |

BH correction is applied across all matrix probes within each convention. 95% CIs are nominal and not multiplicity-adjusted. Sign agreement is descriptive with n=6 genes; no inferential test was performed.

**`results/` was not modified.** `external_summary.json` records the sha256 of `results/04_deg_primary_M2.csv` for verification.

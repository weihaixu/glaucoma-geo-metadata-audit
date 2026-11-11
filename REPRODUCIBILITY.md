# Reproducibility package — donor-level re-analysis of glaucomatous ONH astrocyte microarrays

Generated 9 November 2026. Working directory: `work/data/`.

> All numbers in the manuscript and in `tables/` come from the six real GEO
> series matrices listed below. `_selftest_results/` and `_selftest/` contain
> **synthetic** data used only for unit-testing the pipeline; they must never be
> cited, quoted or compared with the real results.

## 1. Inputs (public, downloaded from NCBI GEO)

| File | Bytes | sha256 |
|---|---:|---|
see `tables/file_manifest.csv` for the full 31-entry manifest with hashes of the
six matrices, three platform annotations, all scripts and all result tables.

- Six series matrices: `GSE9944-GPL{571,8300,91}_series_matrix.txt.gz`,
  `GSE2378-GPL{8300,91}_series_matrix.txt.gz`, `GSE45570_series_matrix.txt.gz`
  (6,021,452 bytes in total).
- Three platform annotations: `GPL8300.annot.gz`, `GPL571.annot.gz`,
  `GPL91.annot.gz`.
- `GSE9944-GPL8300_series_matrix.txt.gz.PARTIAL-DO-NOT-USE` is an isolated
  truncated download and is **not** an input.
- GEO has **no official** `GPL5175.annot.gz` (the `annot/` directory returns 404).
  The v0.7 incremental SOFT extraction was **not completed**, which is why the
  frozen primary run in `results/` still reports GSE45570 as `probe not mapped`,
  never as a negative result. In v0.8 the complete 316,919-row platform table
  was rebuilt into a local `GPL5175.annot.gz` (33,475 probe-to-symbol rows;
  see section 11). That map is **not** a GEO annotation file and is used only
  for the exploratory boundary check in `results_gpl5175/`.

Download method (the NCBI endpoint throttled whole-file transfers to ~130 B/s
and intermittently returned 502): 64 KiB HTTP Range chunks, 3 concurrent
workers, resumable chunk cache in `chunks64/`, and a gzip integrity check per
file.

```bash
D:/anaconda3/python.exe parallel_fetch.py --workers 3 --rounds 8 \
  --only GSE9944-GPL571_series_matrix.txt.gz GSE9944-GPL8300_series_matrix.txt.gz \
         GSE9944-GPL91_series_matrix.txt.gz GSE2378-GPL8300_series_matrix.txt.gz \
         GSE2378-GPL91_series_matrix.txt.gz GSE45570_series_matrix.txt.gz
D:/anaconda3/python.exe parallel_fetch.py --workers 3 --rounds 8 \
  --only GPL8300.annot.gz GPL571.annot.gz GPL91.annot.gz
```

## 2. Analysis runs

| Run | Script | Output | Models actually fitted |
|---|---|---|---|
| Primary (used for all main numbers, Figure 1–2, Table 1–4) | `reanalysis.py` | `results/` | M2/M3 on GSE9944 platforms = donor level + **ancestry only**; on GSE2378/GSE45570 the adjusted design was rejected and the donor-level unadjusted table was used with BH correction |
| M2b covariate-complete sensitivity | `reanalysis_m2b.py` | `results_m2b/` | Same hierarchy, but free-text `char_age` / `char_sex` are parsed into numeric covariates, so GSE9944 M2/M3 = donor level + ancestry + age + sex |
| N1 diagnostics (round 8, does NOT change main numbers) | `diagnose_n1.py` | `results_diagnostics/` | Donor-level ROC/AUC and quantitative ancestry x disease diagnostics; reads the same six matrices, never writes to `results/` |

`reanalysis.py` is deliberately left **unchanged** so that `results/` stays
byte-reproducible. `reanalysis_m2b.py` differs only in `build_metadata()`.
`results/` and `results_m2b/` are separate; neither is silently overwritten.

```bash
D:/anaconda3/python.exe reanalysis.py     --data . --out results
D:/anaconda3/python.exe reanalysis_m2b.py --data . --out results_m2b
D:/anaconda3/python.exe summarize_results.py
D:/anaconda3/python.exe make_figures_tables.py
D:/anaconda3/python.exe diagnose_n1.py
D:/anaconda3/python.exe cold_read_v06.py ../青光眼生信稿件_全文重写稿_v0.6.md results
```

Model definitions (pre-specified, no threshold shopping):

| Model | Unit | Covariates | Call |
|---|---|---|---|
| M0 | array | none | nominal p<0.05, \|log2FC\|>=0.5 (reproduces the original design) |
| M1 | donor | none | nominal p<0.05, \|log2FC\|>=0.5 |
| **M2 (primary)** | donor | ancestry (age/sex only in M2b) | BH q<0.05, \|log2FC\|>=1 |
| M3 | donor | as M2 | BH q<0.05, \|log2FC\|>=0.5 |

Expression scale is declared per dataset, not guessed: GSE2378 is linear
MAS5-like intensity and is log2-transformed; GSE9944 and GSE45570 are stated as
RMA/log2 in their GEO processing fields and are analysed as log2. Evidence is in
`results/02_qc_summary.csv:scale_evidence`; the residual "author must confirm"
flag remains an open item for the submitting authors.

## 3. Environment

```
Python 3.9.13 (D:/anaconda3/python.exe)
numpy 1.21.5  pandas 1.4.4  scipy 1.9.1  statsmodels 0.13.2
scikit-learn 1.0.2  matplotlib 3.5.2  tabulate 0.8.10

R 4.2.0 (C:/Program Files/R/R-4.2.0/bin/x64/Rscript.exe)
limma 3.52.4 + statmod 1.5.0  ->  project-local library work/data/Rlib/
```

The **primary** pipeline is probe-wise OLS + BH in Python. An earlier version of
this note said no R was available; that was wrong — R 4.2.0 was installed but
not on PATH. Round 9 installed limma into the project-local `Rlib/` and ran a
real empirical-Bayes replication (`lmFit` -> `eBayes` -> `topTable`); see
section 8. The limma output is a **sensitivity analysis**, not the primary
result.

## 4. Outputs

- `figures/Figure1.{png,svg}`, `figures/Figure2.{png,svg}` — 300 dpi PNG plus
  editable SVG, generated only from `results/*.csv`.
- `tables/Table1..Table4*.{tsv,md}` — journal-ready main tables.
- `tables/TableS1_all_probes_six_genes.tsv` — every mapped probe with nominal
  95% CI (`log2FC +/- t(0.975, df_resid) * SE`).
- `tables/TableS2_*`, `TableS3_*` — primary M2 vs M2b comparison.
- `tables/TableS4_sensitivity_grid.tsv` — the real alpha x |log2FC| x FDR grid
  computed from `04_deg_primary_M2.csv`. `results/08_sensitivity.csv` is only a
  copy of `03_deg_by_model.csv`; the in-memory grid in `reanalysis.py` was never
  exported, which is why this table is regenerated here.
- `tables/TableS7_donor_vs_array_ROC.tsv` — donor- vs array-level AUC, all-probe
  median AUC, selection-free gene score, selection inflation, BH-adjusted
  permutation q. `tables/TableS8_collinearity_diagnostics.tsv` — VIF, phi,
  condition number, rank, zero-cell flags. Both come from `diagnose_n1.py`.
- `results_diagnostics/` — `07b_roc_donorlevel.csv`,
  `collinearity_diagnostics.csv`, `ancestry_disease_crosstab.csv`,
  `N1_DIAGNOSTICS.md`. Independent of `results/`.
- `DECISION_LOG.md` — author-confirmed primary-model decision (keep A).
- `tables/file_manifest.csv` — sha256 + byte size for inputs, scripts and results.
- `results/decision.json` — decision-tree branch `A`; `results/facts_for_manuscript.md`.

## 5. Deliberately unresolved (author input, not a computation gap)

1. Public code repository / Zenodo DOI and a version-locked environment file.
   No DOI is invented here.
2. GPL5175 gene-level mapping. Until it exists, "probe not mapped" must not be
   written as "validation failed".
3. **RESOLVED 2026-11-09 (author decision: keep A).** M2b is NOT promoted.
   `results/` (pre-specified M2: 114 DEG, q 0.145-0.691 on GSE9944-GPL571)
   remains the single primary result; `results_m2b/` (95 DEG, q 0.077-0.893)
   is reported only as sensitivity. Both give 0/18 significant genes. Rationale,
   the A/B comparison and the 7-file change list that was NOT executed are in
   `DECISION_LOG.md`. No primary number, figure or table was changed.
4. **RESOLVED in round 9 (limma replication).** `install_r_packages.py` +
   `setup_rlib.R` + `limma_replication.R` + `run_limma_replication.py` ran the
   real R/limma 3.52.4 replication; see section 8. Still outstanding:
   Zotero-style formatting of the 31 retained original references; CRediT,
   funding, conflict-of-interest and AI-tool disclosures; institutional
   similarity check (iThenticate/Turnitin).
5. The original wet-laboratory validation and the original downstream DAVID /
   KOBAS / miRNA network results were not re-run and are marked `[UNVERIFIED]`.
6. **RESOLVED in round 8 (N1).** `diagnose_n1.py` recomputed ROC/AUC at donor
   level with the identical probe and label order: all 6 array-level values
   reconcile exactly with `07_roc.csv` and delta = 0, because GSE2378-GPL8300
   has exactly one array per donor (13/13). So no number in `07_roc.csv` was
   changed. The real defect is circular probe selection on the same donors;
   Table S7 quantifies it (+/-0.19 AUC), and Methods/Results/Discussion in
   v0.6 now say so explicitly. The ROC analysis remains exploratory.

## 6. Round-7 additions (2026-11-09): references, declarations, second review

- `audit_references.py` parses all 69 original references and every numeric
  citation marker in v0.4 -> `references_audit.tsv|.json` (32 distinct cited
  numbers, 37 uncited).
- `verify_literature.py` pulls 27 new references from PubMed E-utilities
  esummary (batched by 8 PMIDs; NCBI silently truncates long id lists), Crossref
  (Benjamini-Hochberg 1995) and an official GEO accession record. Output:
  `verified_references.tsv|.json`. Every new reference has a PMID/DOI or URL.
- `apply_v05.py` derives `青光眼生信稿件_全文重写稿_v0.5.md`: 31 retained + 27
  added = 58 references, numbered by first appearance; 5 citation placeholders
  cleared; `references_v05.tsv`, `literature_ledger.tsv`,
  `citation_remap.json` and `青光眼生信稿件_声明填写指南.md` written.
- `cold_read_v05.py` adds two-way citation reconciliation and literature
  verification to the 87 v0.4 checks: 106 PASS / 0 FAIL.
- `青光眼生信稿件_第二轮预审与选刊矩阵.md` records the simulated second review
  (editor + 3 reviewers) and the 2026-11-09 policy check of 6 journals' official
  pages. Key finding: PeerJ explicitly requires two independent validation
  classes for bioinformatics studies using public datasets; PLOS ONE explicitly
  considers negative/null results but rejects derivative work without
  justification.
- **No statistical model was re-run in round 7.** `results/`, `results_m2b/`,
  `figures/` and `tables/` values are unchanged from round 6.

## 7. Round-8 additions (2026-11-09): decision A confirmed, N1 closed

- `DECISION_LOG.md`: author confirmed **keep A**. `results/` stays primary;
  `results_m2b/` stays sensitivity. Zero primary numbers changed.
- `diagnose_n1.py`: donor-level ROC recomputation + quantitative collinearity.
  Output `results_diagnostics/` + `tables/TableS7`, `TableS8`. Array-level
  reconciliation 6/6 exact, 0 mismatches. **This run does not modify
  `results/` or `results_m2b/`.**
- Key diagnostic findings: (i) GSE2378-GPL8300 has one array per donor, so the
  array/donor ROC distinction is numerically empty; the weakness is circular
  probe selection (selected-probe AUC minus all-probe median ranges -0.119 to
  +0.190). (ii) VIF 1.14-1.16 and condition numbers 3.76-6.29 show no classical
  multicollinearity; the problem is a structural zero cell. GSE9944-GPL8300
  also has a zero cell (no African-American controls) that the qualitative QC
  check in the primary run did not flag.
- `apply_v06.py` derives `青光眼生信稿件_全文重写稿_v0.6.md` (text-only revision:
  decision wording, ROC/circularity wording, ancestry wording, Table S7-S8,
  script lists). `cold_read_v06.py` adds decision/circularity/collinearity
  assertions.
- **No statistical model was re-run** and no primary output was overwritten.

The original manuscript `D:\BaiduSyncdisk\待研究相关资料\青光眼生信研究\Manuscript.docx`
was read only and has never been modified.

## 8. Round-9 additions (2026-11-09): real limma replication + gene-level sensitivity

Earlier rounds listed "limma replication" and "all-probe median sensitivity" as
outstanding. Both are now executed. Neither changes any number in `results/`,
`results_m2b/` or `results_diagnostics/`.

### 8.1 R environment (project-local, no user-library changes)

```
D:/anaconda3/python.exe install_r_packages.py        # browser-UA download of Windows binaries
"C:/Program Files/R/R-4.2.0/bin/x64/Rscript.exe" --vanilla setup_rlib.R <absolute /work/data path>
```

`install_r_packages.py` reads the Bioconductor 3.15 Windows binary index
(`https://bioconductor.org/packages/3.15/bioc/bin/windows/contrib/4.2/`, which
rejects the default Python user-agent) and the CRAN Windows binary index, then
saves `Rpackages/limma_3.52.4.zip` and `Rpackages/statmod_1.5.0.zip`.
`setup_rlib.R` installs both into `Rlib/` with `R_LIBS` scoped to the project.
`Rpackages/MANIFEST.tsv` records versions, file names, byte sizes and sources.

### 8.2 limma replication

```
D:/anaconda3/python.exe run_limma_replication.py
```

This script rebuilds the donor-level log2 expression matrix and the M2 design
matrix from the same six GEO series matrices, and **refuses to export** unless a
fresh Python OLS reproduces every primary `log2FC`/`se` in
`results/04_deg_primary_M2.csv` (max error 4.4e-16 over 69,513 probe rows).
It then calls `limma_replication.R`, which runs
`lmFit(method="ls") -> eBayes(trend=FALSE, robust=FALSE) ->
topTable(coef="glaucoma", adjust.method="BH")` for each of the four analysed
platforms. limma `logFC` agrees with the OLS beta to 3.3e-14. Prior df 2.25-4.58,
total df 13.28-20.25 and `sessionInfo()` are exported.

Result: six prioritised genes remain **0/18 significant** (BH q 0.116-0.663
versus 0.145-0.691 under OLS), so decision branch A is unchanged. Probe-level
DEG counts are engine-dependent: GSE9944-GPL571 M2 114 -> 128 and M3 640 -> 709;
GSE9944-GPL8300 M2 0 -> 2; the other two platforms unchanged. These are
**sensitivity results**, not substituted into Table 1 / Figure 1 / Abstract,
because the OLS M2 was the pre-specified primary model.

### 8.3 Gene-level sensitivity

```
D:/anaconda3/python.exe genelevel_sensitivity.py
```

Three conventions are compared on the same donor-level matrices: primary
smallest-p probe; per-donor median of all probes of a gene with a fresh OLS and
BH across genes; Simes combination of probe-level M2 p values with BH across
genes. Each convention gives **0/18 significant** results for the six genes
(minimum q 0.128 for median-expression, 0.219 for Simes). Gene counts were
9,084 / 13,101 / 9,068 on the three annotated platforms. GSE45570 has no usable
GPL5175 annotation and is reported as `no gene annotation`, **never** as a
negative replication. Simes assumes independence or positive dependence and is
exploratory because probes of one gene are correlated.

### 8.4 Files and manifest

`results_limma/` (4 per-platform probe tables, fit summary, sessionInfo,
per-probe reconciliation, six-gene table, dataset summary, status note) and
`results_genelevel/` (gene-level DEG table, Simes tables, six-gene table,
dataset summary, status note) are independent of the primary results.
`tables/TableS9-S12` are the manuscript-facing versions. All are included in
`tables/file_manifest.csv` with sha256 and byte size. `cold_read_v07.py` adds
group N (67 checks) covering the R environment, the 69,513-row reconciliation,
0/18 conclusions, DEG counts, prior df, S9-S12, positive and negative wording,
and the unchanged sha256 of `results/04_deg_primary_M2.csv`.

## 9. Release package (round 10, 2026-11-09)

No result file, figure, table, manuscript paragraph, `file_manifest.csv` entry or
cold-read assertion was modified in this round. Re-running `cold_read_v07.py`
still gives **PASS 228 / FAIL 0**; the regenerated report was restored to its
original bytes afterwards.

`release/` holds the author-side publication kit:

| File | Purpose |
|---|---|
| `.zenodo.json` | Zenodo deposition metadata; `creators / affiliation / orcid` are deliberately left as `__AUTHOR_INPUT_REQUIRED__` |
| `requirements.txt`, `ENVIRONMENT.md` | Exact Python 3.9.13 package pins (numpy 1.21.5, pandas 1.4.4, scipy 1.9.1, statsmodels 0.13.2, scikit-learn 1.0.2, matplotlib 3.5.2, requests 2.28.1) and R 4.2.0 / limma 3.52.4 / statmod 1.5.0 |
| `DECLARATIONS_12.md` | The 12 author-declaration placeholders, with manuscript line numbers and suggested wording |
| `PUBLISH_STEPS.md` | Seven-step route: metadata -> bundle -> GitHub tag v0.7 -> Zenodo DOI -> DOI backfill -> Zotero -> layout/plagiarism check |
| `build_release.py` | Allow-list bundler with sha256 manifest, READY guard, zip and per-file verification |
| `UPLOAD_MANIFEST.tsv` | 137 files, 75.3 MB, each with dest/source path, byte size and sha256 |
| `DOWNLOAD_INPUTS.md` | Auto-generated re-download commands and sha256 for the 9 raw GEO inputs |

Raw GEO `*.gz` inputs are **not redistributed** by default (re-distribution terms
are the author's responsibility); `--include-inputs` adds them. Chunk caches,
R package binaries, synthetic self-tests, trial runs, logs and the truncated
`.PARTIAL-DO-NOT-USE` file are always excluded. A dry run with
`--build --allow-draft --zip --verify` produced a 26,670,003-byte archive with
**0 sha mismatches and 0 extra files**; that draft contained placeholder metadata
and was deleted after verification.

**Cold-read caveat.** Three `cold_read_v07.py` assertions were written for the
pre-publication state (no DOI, placeholders still present): L68-L71, L160-L162
and L201-L202, plus the L516 report note. Backfilling a real Zenodo DOI and
completing the 12 declarations will make them FAIL. Derive `cold_read_v08.py`
and rewrite those checks before the final run; see `release/PUBLISH_STEPS.md`
step 5. Zotero must change reference *formatting only* - renumbering 1-58 breaks
the two-way citation audit in group E.

See `work/青光眼生信稿件_第十轮投稿前操作手册.html` for the full checklist.
**Submission readiness is unchanged: not submittable.**

## 10. Feasibility roadmap (round 11, 2026-11-09)

`work/青光眼生信稿件_投稿可行性提升路线图.html` applies a five-dimension mock
review rubric (contribution 30%, methods 25%, evidence 25%, writing 10%,
compliance 10%) and separates **wording/presentation fixes** from **structural
work that cannot be written around**. Three tiers are given: P0 compliance
(~2.7/5), P1 low-cost substantive enhancement (~3.4/5) and P2 structural
rebuild with new data or wet-lab work (~4.0/5). These are simulated estimates,
not acceptance probabilities. The main result and all 228 cold-read checks are
untouched.

### 10.1 P1-a: post-hoc detectable effect size (executed this round)

`power_mde.py` reads only `results/04_deg_primary_M2.csv` (69,513 probe-level
primary M2 fits), and solves the smallest detectable |log2FC| at two-sided
alpha = 0.05 and 80% power from each probe's standard error and residual df
using the noncentral t distribution. It deliberately does **not** use the
observed effect size, so it is not the classic post-hoc-power fallacy. Outputs
go to the independent `results_power/` directory and
`tables/TableS13_power_mde.tsv|.md`; `results/` is never written.

| Platform | Residual df | Median SE | Typical MDE | Probes with power >= 80% at abs(log2FC)=1 |
|---|---:|---:|---:|---:|
| GSE2378-GPL8300 | 11 | 0.371 | 1.142 | 43.52% |
| GSE9944-GPL571 | 18 | 0.126 | 0.373 | 90.71% |
| GSE9944-GPL8300 | 13 | 0.135 | 0.409 | 94.24% |
| GSE45570 | 10 | 0.146 | 0.455 | 95.28% |

In 11 of 18 six-gene tests the observed |log2FC| is smaller than the MDE
(all 6/6 on GSE9944-GPL571). Interpretation limit: BH q >= 0.05 in these
underpowered, structurally imbalanced designs **cannot exclude a smaller
effect**; it is not evidence of no effect, not a test of equivalence, and not
a reason to reinstate the six genes. The primary conclusion (0/18, branch A)
is unchanged.

### 10.2 P1-b/c/d/e: planned, not executed

`tables/TableS14_external_cohort_candidates.tsv|.md` lists candidate external
GEO series (GSE27276, GSE138125, GSE4316 human trabecular meshwork; GSE26299
DBA/2J mouse ONH; GSE110019/GSE139605 glaucoma-model ONH) as **unverified
planning leads** - accession sizes, platforms and tissue labels must be
checked against the official GEO series matrix before use. Any new series must
be fitted with the same pre-specified donor-level M2 in an independent
`results_external/`, and reported only as cross-tissue / cross-species
directional concordance, never as independent replication. GPL5175 annotation
completion, the planned `geo_metadata_audit.py` checklist tool, and five
wording fixes are described in the roadmap; none has been written into the
manuscript.

`release/build_release.py` now includes `results_power/` in the release
bundle. `tables/file_manifest.csv` was deliberately left unchanged this round;
sha256 for the new S13/S14 files is recorded in
`release/UPLOAD_MANIFEST.tsv` and should be merged into the main manifest at
the v0.8 finalisation.

## 11. Round 12 (2026-11-09): executing P1, producing manuscript v0.8

Order of execution, all read-only with respect to `results/`:

```bash
cd work/data
# P1-c: complete the GPL5175 SOFT platform table (219 x 64 KiB ranges,
#       resumable cache in chunks5175/, gzip-verified)
D:/anaconda3/python.exe fetch_5175_parallel.py --workers 8 --max-chunks 260 --batch 24
D:/anaconda3/python.exe fetch_gpl5175_annot.py          # -> GPL5175.annot.gz
D:/anaconda3/python.exe gpl5175_boundary.py             # -> results_gpl5175/
# P1-d: reusable five-class metadata audit (6 primary + 1 external candidate)
D:/anaconda3/python.exe geo_metadata_audit.py --matrix external_inputs/GSE27276_series_matrix.txt.gz
# P1-a + manuscript v0.8 + cold-read v0.8
D:/anaconda3/python.exe apply_v08.py
D:/anaconda3/python.exe cold_read_v08.py ../青光眼生信稿件_全文重写稿_v0.8.md results
```

Key facts, all verified in this round:

* The complete GPL5175 SOFT platform table has 316,919 data rows. The rebuilt
  local map assigns symbols to 33,475 platform rows and covers 17,634 / 22,011
  (80.11%) GSE45570 transcript clusters, including 7 probes for the six
  transcripts. GEO still has no official `GPL5175.annot.gz`.
* The GSE45570 boundary check excludes the 6 OHT arrays (6 POAG / 6 control,
  residual df 10), collapses probes to a per-sample median per gene and applies
  BH across 17,324 genes: 0 of 6 transcripts reach q < 0.05 (all q = 1.0).
  Whole ONH tissue, a different platform and a different case definition make
  this a boundary check, **not** validation or independent replication.
* `geo_metadata_audit.py` emits 159 metric rows for 7 matrices (6 primary,
  1 external candidate audited for metadata only). Among the 6 primary inputs:
  free-text compound covariates FAIL 3/6, empty group x ancestry strata FAIL
  2/6 (phi -0.354 and -0.462, both designs full rank), replicate/shared-donor
  WARN 2/6. Scale inference matches `results/02_qc_summary.csv` exactly.
  GSE27276's 36 titles do not encode donor identifiers; its official GEO
  record documents paired eyes and one technical replicate, so arrays must not
  be treated as independent donors.
* `apply_v08.py` performs 17 asserted single-match substitutions from v0.7 and
  derives `cold_read_v08.py` with a new O group. **cold-read v0.8: 283 PASS /
  0 FAIL.** v0.7 is byte-identical, `tables/file_manifest.csv` was not modified,
  and `results/04_deg_primary_M2.csv` (sha 48876f29f3d0) and
  `results/07_roc.csv` (sha 29a75234a169) are unchanged. Decision A stands.
* The release bundle now targets manuscript v0.8 and includes `results_audit/`
  and `results_gpl5175/`; `external_inputs/`, chunk caches and the 85 MB SOFT
  text prefix are excluded. `.zenodo.json` remains NOT READY until the author
  fills the three creator fields.

**Submission readiness is unchanged: not submittable.** These are descriptive
and sensitivity analyses. They do not add an independent cohort, a wet-laboratory
experiment or a biological claim, and the six transcripts remain 0/18
non-significant in the pre-specified primary model.




## 12. Round 13 (2026-11-09): completing P1-b, producing manuscript v0.9

```bash
cd work/data
D:/anaconda3/python.exe external_concordance.py     # -> results_external/ + Table S17/S18
D:/anaconda3/python.exe apply_v09.py               # -> manuscript v0.9 + cold_read_v09.py
D:/anaconda3/python.exe cold_read_v09.py           # 351 PASS / 0 FAIL
cd release
D:/anaconda3/python.exe build_release.py --build --allow-draft --zip --verify
```

* `external_concordance.py` reads only the two files in `external_inputs/` and
  the frozen `results/04_deg_primary_M2.csv` as a **sign reference** (never for
  fitting). Scale decision: log2-like (min 5.84, median 6.73, max 15.27), no
  transform, consistent with `ensure_log2(mode="log2")`. BH is applied across
  all 47,293 matrix probes within each of three unit conventions.
* Three conventions: `array_level` (36 units, POAG 17 / control 19, df 34),
  `donor_metadata` (30 units, 17/13, df 28), `donor_declared` (28 units,
  15/13, df 26). Control donors are grouped by identical postmortem delay;
  the two POAG merges are the two highest-correlation disjoint pairs, the
  second of which is an explicitly unverifiable assumption.
* GSE27276 is completely confounded: phi = 1.0 for disease vs collection and
  vs postmortem delay; design rank with both confounders is 2 of 4. No
  ancestry/age/sex is deposited, so M2 = `[1, glaucoma]` with an
  `ADJUSTMENT NOT POSSIBLE` flag on every probe.
* Results: 1115 / 1108 / 704 probes at BH q < 0.05; six transcripts 0/6
  significant in every convention (q 0.330-0.805); direction agreement
  23/54 (42.6%), descriptive only. **Not an independent replication or a
  validation cohort.**
* `apply_v09.py` performs 13 asserted single-match substitutions on v0.8 and
  derives `cold_read_v09.py` with a 68-item P group. **cold-read v0.9: 351
  PASS / 0 FAIL.** v0.7 (`3fcfdbb3d2d2`) and v0.8 (`7bb05464f69f`) are
  byte-identical; `results/04_deg_primary_M2.csv` (`48876f29f3d0`) and
  `results/07_roc.csv` (`29a75234a169`) are unchanged; `tables/file_manifest.csv`,
  Figure 1-2 and Table 1-4 were not touched. Decision A stands.
* The release bundle now targets manuscript v0.9 and includes
  `results_external/`. `.zenodo.json` remains NOT READY until the author fills
  the three creator fields.

**Submission readiness is unchanged: not submittable.** P1 is complete, but it
adds methodology and reporting quality only. It does not add an independent
human cohort, a wet-laboratory experiment or a biological claim, and the six
transcripts remain 0/18 non-significant in the pre-specified primary model.


## 13. Round 14 (2026-11-09): reframing for a methodology / data-quality article (v1.0)

```bash
cd work/data
D:/anaconda3/python.exe apply_v10.py          # -> manuscript v1.0 + cold_read_v10.py
D:/anaconda3/python.exe cold_read_v10.py      # 388 PASS / 0 FAIL
D:/anaconda3/python.exe apply_release_v10.py  # -> release package + run docs
cd release
D:/anaconda3/python.exe build_release.py --build --allow-draft --zip --verify
```

* `apply_v10.py` performs 14 asserted single-match substitutions on v0.9. All
  Results sections (3.1-3.5), Methods 2.1-2.7, Declarations, References and
  Figure legends are preserved verbatim. The R group of `cold_read_v10.py`
  verifies that the set of in-text citation numbers in v1.0 equals that of
  v0.9, that no numeric claim changed, that all 12 author-declaration
  placeholders and 10 UNVERIFIED markers remain, and that v0.7
  (`3fcfdbb3d2d2`), v0.8 (`7bb05464f69f`), v0.9 (`05c1aa8eb12e`) and
  `results/04_deg_primary_M2.csv` (`48876f29f3d0`) are byte-identical.
* New artefact: `tables/TableS19_metadata_audit_checklist.md|.tsv` - a
  reusable five-class checklist (structured covariates, group-by-ancestry zero
  cells, replicate/donor overlap, annotation availability, scale and excluded
  groups) with decision rules, a minimum per-series reporting schema and
  mandatory interpretation boundaries. It is a template, contains no
  disease-effect estimate and makes no transcript-level claim.
* The manuscript is journal-neutral: no journal name, quartile, impact factor
  or APC appears in the article text. Journal/category verification is kept in
  the separate positioning report and is explicitly dated.
* **Submission readiness: the category direction is viable, but the manuscript
  is still not a submission text** until the 12 author declarations, the code
  DOI, institutional journal-list confirmation and the target-journal format
  are completed. Reframing changes editorial fit, not the evidence base: no
  independent human cohort, wet-laboratory validation or biological claim was
  added, and the six transcripts remain 0/18 non-significant in the
  pre-specified primary model.

## 14. Round 15 (2026-11-10): pre-submission toolchain, no result changes

```bash
cd work/data
D:/anaconda3/python.exe preflight_v10.py                       # read-only gate -> report
D:/anaconda3/python.exe patch_cold_read_postdoi.py --check     # verify 8 anchors
D:/anaconda3/python.exe patch_cold_read_postdoi.py --build    # -> cold_read_v10_postdoi.py
D:/anaconda3/python.exe cold_read_v10.py                      # baseline 388 PASS / 0 FAIL
# after the author fills the 12 declarations and the Zenodo DOI:
D:/anaconda3/python.exe cold_read_v10_postdoi.py              # independent postdoi report
cd release
D:/anaconda3/python.exe build_release.py
D:/anaconda3/python.exe build_release.py --build --allow-draft --zip --verify
```

* `preflight_v10.py` is **read-only** except for writing its own Markdown
  report. It checks the frozen-chain hashes, the 12 author placeholders and
  10 `[UNVERIFIED]` markers, `.zenodo.json` creators, DOI state, six
  manuscript-internal repairs, the release manifest and the delivered
  toolchain, plus 8 author-only administrative confirmations. Current gate:
  **59 checks, READY 27 / PENDING 23 / FIX 4 / NOTE 5 → NOT READY**.
* `patch_cold_read_postdoi.py` performs 8 asserted single-match
  substitutions on the frozen `cold_read_v10.py` and inserts a 22-item group
  S. Five assertions encoded the "DOI not yet filled" state; the fifth is the
  v1.0-only `R 占位符` check that PUBLISH_STEPS.md had omitted. The derived
  script has a front gate that exits 2 when no DOI is present and writes to
  `青光眼生信稿件_cold-read_v1.0-postdoi报告.md`, never overwriting the
  v1.0 baseline report. Group S reconciles every `results/` entry in
  `tables/file_manifest.csv` against the file on disk (manifest → disk, not
  disk → manifest, because `results/RUN_REPORT.md` is documentation).
* **Validation by simulated backfill** (throwaway copy, DOI
  `10.5281/zenodo.1234567` in Methods 2.6 / Data availability / Code
  availability, 12 placeholders replaced, 10 UNVERIFIED kept):
  **410 PASS / 0 FAIL** = 388 baseline + 22 group-S checks. The simulated
  manuscript and report were deleted afterwards. `cold_read_v10.py` remains
  byte-identical (`99004478950a`) and still reports 388 / 0.
* Official BMC Medical Research Methodology Research article criteria were
  re-checked on 2026-11-10 (`.../submission-guidelines/research-article` and
  `.../preparing-your-manuscript`). Two constraints newly recorded:
  non-commissioned pooled analyses of selected published research are not
  considered, and new computational methods need to have been *well tested*.
  The cover letter addresses both: no effect sizes were pooled, and the C1–C5
  checklist is described as demonstrated on seven series matrices, never as
  validated. Abstract is 452 words against a 350-word limit; Declarations
  lacks `Consent for publication` and `Acknowledgements`; LLM use must be
  documented in Methods. These are author-side repairs listed in
  `青光眼生信稿件_投稿前操作清单_v1.0.md` §1, not changes made here.
* Strictly NOT verified: CAS/JCR quartile, official JIF cross-check, current
  APC, institutional warning lists and recognised-journal catalogue, review
  time definitions, and the target journal's AI policy on submission day.
  The institutional research-management office's current catalogue governs.

**Submission readiness is unchanged: not submittable.** This round adds
editorial-fit work and operational tooling only. No cohort, experiment,
biological claim or validation was added; the six transcripts remain 0/18 in
the pre-specified primary model, the external series is not an independent
replication, and `results/` is unchanged.

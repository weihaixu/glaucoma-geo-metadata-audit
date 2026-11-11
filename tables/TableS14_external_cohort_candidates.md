# Table S14. Candidate external GEO series for an independence check (NOT yet analysed)

Compiled 2026-11-09 from a literature/GEO web search. **Accession numbers, sample
counts, platforms and tissue labels MUST be re-verified against the official NCBI
GEO series matrix before any of these are downloaded, analysed or cited.** Several
published papers report different sample counts for the same accession; no number
below is a verified fact and none has been entered into a result table.

This table is a *planning aid* for raising submission feasibility, not evidence.
Adding any of these series does NOT automatically create an "independent replication":
GSE2378 and GSE9944 come from the same Northwestern / Hernandez laboratory and
share donor identifiers, and GSE45570 profiles whole ONH tissue on an exon array
with no GEO annotation file.

| Accession | Tissue / species | Reported size (unverified) | Reported platform (unverified) | Why it could help | Honest label if used | Verify first |
|---|---|---|---|---|---|---|
| GSE27276 | Human trabecular meshwork (POAG vs control) | 19/17, 17/19 or 15/13 depending on the paper | GPL2507 / Sentrix Human-6 | Different laboratory, different ocular tissue, different platform from GSE9944/GSE2378; the most realistic "independent public dataset" | Cross-tissue directional concordance, NOT astrocyte-specific replication | Official GEO series matrix: exact n, group labels, platform, gene annotation availability |
| GSE138125 | Human trabecular meshwork | 4 glaucoma / 4 control | not verified | Second independent human TM series; can be harmonised with GSE27276 | Small-n exploratory concordance | Official GEO record; batch/harmonisation feasibility |
| GSE4316 | Human trabecular meshwork (POAG) | 2 POAG / 3 control | Affymetrix HG-U133 Plus 2.0 | Has an official platform annotation, so gene-level tests are possible | Very small-n exploratory only; do not use for a primary claim | Official GEO record |
| GSE26299 | DBA/2J mouse optic nerve head + retina | 50 DBA/2J eyes / 10 D2-Gpnmb+ controls | Affymetrix Mouse 430 v2 | Same organ (ONH), staged glaucoma, substantially larger n; mouse orthologues of the six genes | Cross-species directional concordance, NOT human validation | Official GEO record; orthologue mapping and staging definition |
| GSE110019, GSE139605 | ONH in glaucoma models (cited by a 2024 WGCNA paper, PMID 39495230) | not verified | not verified | Additional ONH series for an audit-tool extension | Only after species/platform/n are verified | Official GEO records for both accessions |
| GSE105269 | Aqueous humour, POAG / XFG vs control | not verified | not verified | Different biospecimen, potentially a "new clinical data" dimension | Not a transcriptomic tissue comparison; verify assay type first | Official GEO record and assay type |
| GSE133563, GSE3554 | Rat optic nerve crush retina / DBA/2J mouse retina | not verified | not verified | Retinal injury models | **Not recommended** - optic nerve crush and retinal ageing are not glaucoma ONH comparisons | n/a |

## What a valid addition would require

1. Download the official series matrix + platform annotation; verify gzip integrity
   and record sha256 in `tables/file_manifest.csv`.
2. Reconstruct donor/sample identifiers, groups, OHT/other-exclusion and available
   covariates; run the same `geo_metadata_audit.py` checklist planned in the
   feasibility roadmap (free-text age/sex, race x disease zero cells, donor overlap,
   platform generation, annotation availability).
3. Fit the SAME pre-specified donor-level OLS M2 + BH, with the six transcripts
   pre-listed, and report all probes / CI / q. Do not select probes by smallest
   nominal p as the primary convention (the gene-level sensitivity showed this is
   optimistic).
4. Report concordance as a directional / boundary check with explicit tissue,
   species and platform differences. Never write "independent replication" or
   "validation" for a different tissue or species.
5. Keep the new results in an independent `results_external/` directory; do not
   overwrite `results/`. Re-derive Table S15 and extend `cold_read_v08.py` before
   claiming any improvement in the manuscript.

# Table S14 (official verification, 2026-11-09). Candidate external GEO series

**This file supersedes the unverified numbers in `TableS14_external_cohort_candidates.md`**
for the accessions listed below. Every row was read from the official NCBI GEO
accession viewer (`https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=<GSE>`)
on 2026-11-09, and platform annotation availability was probed with a single-byte
HTTP Range request against `ftp.ncbi.nlm.nih.gov/geo/platforms/.../annot/`.
A `206` means the annotated file exists; `404` means GEO has no official
`*.annot.gz` for that platform. **No series matrix or annotation file was
downloaded, parsed or analysed in this step**, and no number from this table has
been entered into any result table or into the manuscript.

This is a planning/verification aid, not evidence. None of these series has been
used for a differential-expression test. Adding any of them does **not**
constitute "independent replication": GSE2378 and GSE9944 come from the same
Northwestern / Hernandez laboratory and share donor identifiers, GSE45570
profiles whole ONH tissue on an exon array with no GEO annotation, and the
candidates below differ in tissue, species, assay and case definition.

| Accession | Official organism | Official tissue / assay | Official GSM count | Official groups (as stated) | Official platform | annot.gz probe | Verdict |
|---|---|---|---:|---|---|---|---|
| GSE27276 | Homo sapiens | Trabecular meshwork, expression profiling by array | 36 | 13 controls / 15 POAG cases; 6 controls and 1 case had both eyes profiled, 1 technical replicate among cases; "average from the biological replicates for each individual was used for analysis" | GPL2507 Sentrix Human-6 Expression BeadChip | GPL2507.annot.gz = 206; series matrix = 206 | **Most realistic** independent public series. Different laboratory (Augusta University / Liu Y), different tissue, different platform. Donor-level collapsing is mandatory because of paired eyes and a technical replicate. |
| GSE138125 | Homo sapiens | Trabecular meshwork, lncRNA + mRNA array | 8 | 4 normal controls / 4 POAG | GPL21827 Agilent-079487 Arraystar Human LncRNA V4 (Probe Name) | GPL21827.annot.gz = **404** (no official GEO annotation); "Processed data included within Sample table" | Small-n exploratory only. Gene-symbol mapping would have to come from the submitted processed table, not from a GEO annot file; record that limitation explicitly. |
| GSE4316 | Homo sapiens | Cultured HTM cells *and* dissected HTM tissue | 8 | 3 cultured HTM cell samples, 3 control TM tissue pairs, 2 POAG TM tissue pairs | GPL570 HG-U133 Plus 2.0 | GPL570.annot.gz = 206 | Very small-n exploratory only. The glaucoma-vs-control tissue comparison is effectively 2 vs 3; cultured cells are not a tissue comparison and must be excluded. Do not use for a primary claim. |
| GSE26299 | Mus musculus | DBA/2J ONH **and** retina, expression array | 108 | 40 DBA/2J eyes at 10.5 months (range of severity), 10 age/strain-matched D2-Gpnmb+ controls, 10 young 4.5-month DBA/2J; ONH and retina profiled separately, with rep1/rep2/rep3 technical replicates | GPL1261 Mouse Genome 430 2.0 | GPL1261.annot.gz = 206 | Cross-species directional concordance only. Arrays must first be split by tissue and collapsed by eye; mouse orthologues of the six genes need explicit mapping. |
| GSE110019 | **Felis catus** (cat) | ONH, RNA-seq (HiSeq 2000) | 16 | Congenital glaucoma cats vs age-matched normal cats; "early-stage glaucoma" | GPL17081 Illumina HiSeq 2000 (Felis catus) | n/a (RNA-seq; FPKM.txt.gz + GTF supplied) | Cross-species, cross-assay. FPKM is not log2 microarray intensity: the pre-specified M2 cannot be reused unchanged. GEO supplies `GSE110019_FPKM.txt.gz` and a cat GTF. |
| GSE139605 | Mus musculus | **ONH astrocytes**, RNA-seq (HiSeq 2500) | 16 | 13-week young naive, 40-week aged naive, saline-injected control, microbead-induced ocular hypertension; triplicate | GPL17021 Illumina HiSeq 2500 (Mus musculus) | n/a (RNA-seq; featureCounts XLSX supplied) | Closest cell type to the original report but cross-species, cross-assay and count-based. Requires an orthologue map and a count-appropriate model; cannot be a like-for-like M2 replication. |
| GSE105269 | Homo sapiens | **Aqueous humour miRNA** (NanoString nCounter) | 35 | POAG n=12 / XFG n=12 / cataract controls n=11 | GPL24158 NanoString nCounter Human v3 miRNA Assay | n/a | **EXCLUDE.** This is a non-coding RNA (miRNA) profiling experiment, not a six-gene mRNA expression dataset. It cannot support a directional-concordance check on FGFR1/SMAD1/STAT1/TGFBR2/CASP1/CASP4. |
| GSE133563, GSE3554 | not verified | Rat optic nerve crush retina / DBA/2J mouse retina | not verified | not verified | not verified | n/a | Still **not recommended**: optic nerve crush and retinal ageing are not glaucoma ONH comparisons. Left unverified deliberately. |

## Corrections to the earlier unverified planning table

| Accession | Earlier claim (unverified) | Official record |
|---|---|---|
| GSE27276 | "19/17, 17/19 or 15/13 depending on the paper"; platform "GPL2507 / Sentrix Human-6" | **13 controls / 15 POAG cases, 36 GSM**; GPL2507 confirmed. The 36 arrays include paired eyes and one technical replicate, which explains why published papers quote different "n". |
| GSE138125 | "4 glaucoma / 4 control; platform not verified" | 4 / 4 confirmed; platform is **GPL21827** (Agilent Arraystar LncRNA V4) and has **no** official GEO annot.gz. |
| GSE4316 | "2 POAG / 3 control; Affymetrix HG-U133 Plus 2.0" | Tissue comparison is ~2 POAG vs 3 control **plus 3 cultured-cell arrays** (8 GSM total); platform GPL570 confirmed. |
| GSE26299 | "50 DBA/2J eyes / 10 D2-Gpnmb+ controls; Affymetrix Mouse 430 v2" | **40 DBA/2J eyes + 10 D2-Gpnmb+ + 10 young DBA/2J**, ONH and retina separately, **108 GSM** with rep1-3; GPL1261 confirmed. |
| GSE110019, GSE139605 | "ONH in glaucoma models; species / platform / n not verified" | GSE110019 = **cat**, RNA-seq, 16 GSM, FPKM+GTF supplied; GSE139605 = **mouse ONH astrocytes**, RNA-seq, 16 GSM, featureCounts XLSX supplied. |
| GSE105269 | "Different biospecimen, potentially a 'new clinical data' dimension" | **miRNA profiling**, not mRNA; cannot test the six transcripts. Downgrade to excluded. |

## What a valid addition would require

1. Download the official series matrix + platform annotation; verify gzip integrity
   and record sha256 in a **new** manifest (do not touch `tables/file_manifest.csv`,
   which is the frozen primary-run manifest).
2. Reconstruct donor/sample identifiers, groups, OHT/other exclusions and available
   covariates; run the `geo_metadata_audit.py` checklist from P1-d (free-text
   age/sex, group x ancestry zero cells, donor overlap / technical replicates,
   platform generation, annotation availability, expression scale).
3. Fit the SAME pre-specified donor-level OLS M2 + BH, with the six transcripts
   pre-listed, and report all probes / 95% CI / q. For RNA-seq series (GSE110019,
   GSE139605) the model must be re-derived for count/FPKM data and reported as a
   separate convention, not silently merged with the microarray M2.
4. Report concordance as a **directional / boundary check** with explicit tissue,
   species and assay differences. Never write "independent replication" or
   "validation" for a different tissue, species or assay.
5. Keep new results in an independent `results_external/` directory; do not
   overwrite `results/`. Re-derive Table S15 and extend `cold_read_v08.py` before
   entering any new number into the manuscript.
6. Even with two or more additional public series, PeerJ's requirement of at least
   **two of three** validation classes (independent public data / new clinical
   data / new experimental data) may still be unmet, because multiple public
   series can count as one class.

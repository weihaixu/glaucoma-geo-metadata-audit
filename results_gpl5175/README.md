# GSE45570 gene-level boundary check (exploratory)

Built from the **rebuilt** GPL5175 probe-to-gene map (complete SOFT platform table, 316,919 rows). GEO still has no official `GPL5175.annot.gz`.

Files: `01_probe_mapping.csv`, `02_gene_level_boundary.csv` (gene = per-sample median of its probes; donor-level OLS `intercept + glaucoma`, BH across genes), `03_six_gene_boundary.csv`, `04_six_gene_probes.csv`, `boundary_summary.json`.

**Boundary, not validation.** GSE45570 is whole ONH tissue on an exon array with a different case definition; the OHT arm is excluded. It cannot validate a finding about cultured ONH astrocytes, and it is not an independent replication. `results/`, the 0/18 conclusion, Figures 1-2 and Tables 1-4 are untouched. Unmapped probes are missing annotation, never negative results.

# geo_metadata_audit outputs

Read-only audit of 7 GEO series matrices (five defect classes).

* `audit_report.csv` - long-form per-metric rows
* `audit_checklist.csv` - wide checklist, one row per matrix
* `audit_summary.json` - defect occurrence counts and interpretation boundaries
* `audit_records.json` - full machine-readable record per matrix
* `tables/TableS16_metadata_audit.md|tsv` - manuscript-ready supplementary table

Reuse: `python geo_metadata_audit.py --matrix NEW_series_matrix.txt.gz`.
The script never writes to `results/`, never edits an input matrix and never treats missing annotation as a negative result.

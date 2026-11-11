# Exact environment used for the v0.7 results (author must confirm licence/policy before release)

## Python

- Interpreter: **Python 3.9.13** (Anaconda, `D:/anaconda3/python.exe` on this machine)
- Install with: `pip install -r release/requirements.txt`
- Verified locally on 2026-11-09 with `importlib.metadata.version`:
  numpy 1.21.5, pandas 1.4.4, scipy 1.9.1, statsmodels 0.13.2,
  scikit-learn 1.0.2, matplotlib 3.5.2, requests 2.28.1.

## R (limma replication, sensitivity analysis only)

- **R 4.2.0** at `C:/Program Files/R/R-4.2.0/bin/x64/Rscript.exe` (not on PATH)
- **limma 3.52.4**, **statmod 1.5.0**, installed from Bioconductor 3.15 / CRAN
  Windows binaries into the project-local `Rlib/`; the user's R library was never modified.
- Installers: `install_r_packages.py` (browser User-Agent is required; the default
  urllib UA receives HTTP 403 from Bioconductor), `setup_rlib.R`, `Rpackages/MANIFEST.tsv`.
- Pipeline: `lmFit(method="ls") -> eBayes(trend=FALSE, robust=FALSE) ->
  topTable(coef="glaucoma", adjust.method="BH")`, driven by `run_limma_replication.py`.
- `results_limma/sessionInfo.txt` records the exact session.

## Version-lock caveat

`requirements.txt` pins the Python packages actually used. It is NOT a full conda
environment export, and it does not pin R itself. If the target journal requires a
container or a conda `environment.yml`, generate one from the working environment
and add its sha256 to `tables/file_manifest.csv` before tagging the release.

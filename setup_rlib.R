# Install limma + statmod from local Windows binary zips into a project-local
# library. Run with:
#   "C:/Program Files/R/R-4.2.0/bin/x64/Rscript.exe" --vanilla setup_rlib.R
args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) >= 1) args[1] else getwd()
lib <- file.path(root, "Rlib")
dir.create(lib, showWarnings = FALSE, recursive = TRUE)
.libPaths(c(normalizePath(lib, winslash = "/"), .libPaths()))
pkgs <- c("statmod_1.5.0.zip", "limma_3.52.4.zip")
for (f in pkgs) {
  p <- file.path(root, "Rpackages", f)
  if (!file.exists(p)) stop("missing package zip: ", p)
  install.packages(p, repos = NULL, type = "win.binary", lib = lib,
                   quiet = TRUE)
}
ok <- sapply(c("limma", "statmod"), requireNamespace, quietly = TRUE,
             lib.loc = lib)
cat("R:", R.version.string, "\n")
cat("lib:", lib, "\n")
for (n in names(ok)) {
  cat(n, if (isTRUE(ok[[n]])) as.character(packageVersion(n, lib.loc = lib)) else "MISSING", "\n")
}
if (!all(ok)) quit(status = 1)

# limma replication of the primary M2 model (round 9, task 1).
#
# Input TSVs are exported by run_limma_replication.py from EXACTLY the same
# donor-level log2 expression matrix and design matrix that reanalysis.py used
# for M2. This script only changes the statistical engine:
#     OLS t-test  ->  limma empirical-Bayes moderated t (lmFit + eBayes)
#
# Run:
#   Rscript --vanilla limma_replication.R <input_dir> <output_dir>
suppressPackageStartupMessages(library(limma))
args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2) stop("usage: limma_replication.R <input_dir> <output_dir>")
indir <- normalizePath(args[1], winslash = "/")
outdir <- args[2]
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

cat("limma:", as.character(packageVersion("limma")), "\n")
files <- sort(list.files(indir, pattern = "^expr_.*\\.tsv$", full.names = TRUE))
if (!length(files)) stop("no expr_*.tsv files in ", indir)
summary_rows <- list()

for (f in files) {
  ds <- sub("^expr_", "", sub("\\.tsv$", "", basename(f)))
  dfile <- file.path(indir, paste0("design_", ds, ".tsv"))
  if (!file.exists(dfile)) stop("missing design for ", ds)
  E <- read.delim(f, row.names = 1, check.names = FALSE,
                  stringsAsFactors = FALSE, quote = "")
  D <- read.delim(dfile, row.names = 1, check.names = FALSE,
                  stringsAsFactors = FALSE, quote = "")
  E <- as.matrix(E)
  D <- as.matrix(D)
  storage.mode(E) <- "double"
  storage.mode(D) <- "double"
  if (!identical(colnames(E), rownames(D)))
    stop("sample order mismatch in ", ds)
  if (!"glaucoma" %in% colnames(D))
    stop("design has no glaucoma coefficient in ", ds)
  if (any(!is.finite(E))) stop("non-finite expression values in ", ds)

  fit <- lmFit(E, D, method = "ls")
  eb  <- eBayes(fit, trend = FALSE, robust = FALSE)
  tt  <- topTable(eb, coef = "glaucoma", number = Inf, sort.by = "none",
                  adjust.method = "BH", confint = FALSE)
  rn <- rownames(tt)
  dprior <- if (length(eb$df.prior) > 1) eb$df.prior[1] else eb$df.prior
  s2prior <- if (length(eb$s2.prior) > 1) median(eb$s2.prior) else eb$s2.prior
  # fit$df.residual / eb$df.total are scalars when every probe has complete
  # data, but vectors when some probes have missing values. Handle both.
  pos <- match(rn, rownames(E))
  dfr <- as.numeric(fit$df.residual)
  dft <- as.numeric(eb$df.total)
  dfr <- if (length(dfr) == 1L) rep(dfr, length(rn)) else dfr[pos]
  dft <- if (length(dft) == 1L) rep(dft, length(rn)) else dft[pos]
  out <- data.frame(
    probe = rn,
    logFC = as.numeric(tt$logFC),
    AveExpr = as.numeric(tt$AveExpr),
    t_mod = as.numeric(tt$t),
    p_mod = as.numeric(tt$P.Value),
    q_BH_mod = as.numeric(tt$adj.P.Val),
    B = as.numeric(tt$B),
    se_ols = as.numeric(fit$stdev.unscaled[rn, "glaucoma"] * fit$sigma[rn]),
    sigma_ols = as.numeric(fit$sigma[rn]),
    s2_post = as.numeric(eb$s2.post[rn]),
    df_residual = as.numeric(dfr),
    df_prior = as.numeric(dprior),
    s2_prior = as.numeric(s2prior),
    df_total = as.numeric(dft),
    stringsAsFactors = FALSE
  )
  write.table(out, file.path(outdir, paste0("limma_", ds, ".tsv")),
              sep = "\t", row.names = FALSE, quote = FALSE)
  summary_rows[[ds]] <- data.frame(
    dataset = ds, n_probes = nrow(E), n_samples = ncol(E),
    n_design_cols = ncol(D), df_residual = fit$df.residual[1],
    df_prior = as.numeric(dprior), s2_prior = as.numeric(s2prior),
    sigma_median = median(fit$sigma), stringsAsFactors = FALSE)
  cat(sprintf("%-22s probes=%6d donors=%2d df.resid=%2d df.prior=%.3f s2.prior=%.5f\n",
              ds, nrow(E), ncol(E), fit$df.residual[1], dprior, s2prior))
}
write.table(do.call(rbind, summary_rows),
            file.path(outdir, "limma_fit_summary.tsv"),
            sep = "\t", row.names = FALSE, quote = FALSE)
sink(file.path(outdir, "session_info.txt"))
cat("R / package versions used for the limma replication\n")
cat("====================================================\n")
print(sessionInfo())
sink()
cat("wrote", length(files), "limma tables + fit summary + session_info\n")

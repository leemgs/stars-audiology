# Independent survey-variance reproduction for STARS (M6).
# ---------------------------------------------------------------------------
# Cross-checks the design-based SEs/CIs from the Python pipeline
# (code/src/nhanes_analysis.py, knhanes_analysis.py) against the established
# R `survey` package, using DOMAIN (subpopulation) estimation on the full design
# and the standard lonely-PSU option -- the two points a survey-methods reviewer
# probes (see paper/REVIEWER_ASSESSMENT.md, M6).
#
# Usage:
#   1) Dump the derived analytic frame from the Python pipeline:
#        python src/knhanes_analysis.py --mapping config/knhanes_mapping.yaml \
#            --data-dir data/raw/knhanes --cycles 2010 2011 2012 \
#            --out outputs/knhanes_results.json \
#            --dump-analytic outputs/knhanes_analytic.csv
#   2) Reproduce here:
#        Rscript src/reproduce_survey.R outputs/knhanes_analytic.csv
#
# Requires: install.packages("survey")
# ---------------------------------------------------------------------------

suppressPackageStartupMessages(library(survey))

args <- commandArgs(trailingOnly = TRUE)
csv  <- if (length(args) >= 1) args[[1]] else "outputs/knhanes_analytic.csv"
d    <- read.csv(csv, stringsAsFactors = FALSE)

# Standard handling of single-PSU ("lonely") strata: center at the grand mean
# (conservative). This matches the Python estimator's default single_psu="center"
# and is the correct alternative to silently dropping the stratum term.
options(survey.lonely.psu = "adjust")

# Full survey design (retain EVERY row so domain estimation keeps the design).
des <- svydesign(ids = ~psu, strata = ~strata, weights = ~weight,
                 data = d, nest = TRUE)

# Domain = the 40-69 analytic band. subset() on a svydesign performs proper
# domain estimation (it does NOT discard the design information).
dom <- subset(des, age >= 40 & age <= 69)

cat("\n== Weighted prevalence (domain 40-69), R survey ==\n")
for (v in c("tinnitus", "bothersome_tinnitus", "hearing_loss",
            "worse_ear_hearing_loss", "hf_hearing_loss",
            "perceived_stress", "depressed")) {
  if (v %in% names(d)) {
    est <- svymean(as.formula(paste0("~", v)), dom, na.rm = TRUE)
    ci  <- confint(est)
    cat(sprintf("  %-24s %.4f  (95%% CI %.4f, %.4f)\n",
                v, coef(est)[1], ci[1, 1], ci[1, 2]))
  }
}

cat("\n== Design-based logistic ORs (domain 40-69), R survey ==\n")
fit_or <- function(outcome, rhs, label) {
  f <- as.formula(paste(outcome, "~", rhs))
  m <- tryCatch(svyglm(f, design = dom, family = quasibinomial()),
                error = function(e) NULL)
  if (is.null(m)) { cat(sprintf("  [skip] %s\n", label)); return(invisible()) }
  or <- exp(cbind(OR = coef(m), confint(m)))
  cat(sprintf("\n  -- %s --\n", label))
  print(round(or, 3))
}

base <- "perceived_stress + occ_noise + age + sex"
fit_or("tinnitus", base, "Tinnitus ~ minimal-sufficient (primary)")
fit_or("tinnitus", paste(base, "+ depressed"), "Tinnitus + depressed (extended)")
fit_or("tinnitus", paste(base, "+ hearing_loss"), "Tinnitus + hearing loss")
fit_or("hearing_loss", base, "Hearing loss (better ear) ~ minimal-sufficient")
fit_or("worse_ear_hearing_loss", base, "Hearing loss (worse ear)")
fit_or("hf_hearing_loss", base, "Hearing loss (high-freq 3/4/6 kHz)")

cat("\nCompare these ORs/CIs to code/outputs/knhanes_results.json. Small SE\n",
    "differences from the Python estimator are expected only at the rounding\n",
    "level; large discrepancies indicate a design-specification error to fix.\n")

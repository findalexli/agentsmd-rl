#!/usr/bin/env bash
set -euo pipefail

cd /workspace/causalpy

# Idempotency guard
if grep -qF "- **Backwards compatibility**: Avoid preserving backwards compatibility for API " "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -43,6 +43,7 @@
 - **Formulas**: Use patsy for formula parsing (via `dmatrices()`)
 - **Custom exceptions**: Use project-specific exceptions from `causalpy.custom_exceptions`: `FormulaException`, `DataException`, `BadIndexException`
 - **File organization**: Experiments in `causalpy/experiments/`, PyMC models in `causalpy/pymc_models.py`, scikit-learn models in `causalpy/skl_models.py`
+- **Backwards compatibility**: Avoid preserving backwards compatibility for API elements introduced within the same PR; only maintain compatibility for previously released APIs.
 
 ## Code quality checks
 
PATCH

echo "Gold patch applied."

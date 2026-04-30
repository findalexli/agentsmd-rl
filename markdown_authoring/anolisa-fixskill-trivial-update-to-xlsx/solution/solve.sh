#!/usr/bin/env bash
set -euo pipefail

cd /workspace/anolisa

# Idempotency guard
if grep -qF "description: \"Comprehensive spreadsheet creation, editing, and analysis with sup" "src/os-skills/others/xlsx/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/os-skills/others/xlsx/SKILL.md b/src/os-skills/others/xlsx/SKILL.md
@@ -1,7 +1,7 @@
 ---
 name: xlsx
 version: 1.0.0
-description: "Comprehensive spreadsheet creation, editing, and analysis with support for formulas, formatting, data analysis, and visualization. When Claude needs to work with spreadsheets (.xlsx, .xlsm, .csv, .tsv, etc) for: (1) Creating new spreadsheets with formulas and formatting, (2) Reading or analyzing data, (3) Modify existing spreadsheets while preserving formulas, (4) Data analysis and visualization in spreadsheets, or (5) Recalculating formulas"
+description: "Comprehensive spreadsheet creation, editing, and analysis with support for formulas, formatting, data analysis, and visualization. When agent needs to work with spreadsheets (.xlsx, .xlsm, .csv, .tsv, etc) for: (1) Creating new spreadsheets with formulas and formatting, (2) Reading or analyzing data, (3) Modify existing spreadsheets while preserving formulas, (4) Data analysis and visualization in spreadsheets, or (5) Recalculating formulas"
 license: Proprietary. LICENSE.txt has complete terms
 ---
 
PATCH

echo "Gold patch applied."

#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-rules-skill

# Idempotency guard
if grep -qF "| `CowriterAjaxController.php` | `AjaxController.php` | **WRONG** - name mismatc" "skills/agents/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/agents/SKILL.md b/skills/agents/SKILL.md
@@ -52,10 +52,43 @@ When checking if AGENTS.md files are up to date, use the freshness checking scri
 |----------|---------------------|
 | Module list | `ls <dir>/*.py` + read docstrings |
 | Script list | `ls scripts/*.sh` + read headers |
-| Commands | `grep` Makefile targets |
+| Commands | `grep` Makefile targets **AND run them** |
 | Test files | `ls tests/*.py` |
 | Data files | `ls *.json` in project root |
 | Config files | Check actual existence |
+| **File names** | **EXACT match required** (not just existence) |
+| **Numeric values** | PHPStan level, coverage %, etc. from actual configs |
+
+### Critical: Exact Name Matching
+
+File names in AGENTS.md must match actual filenames **exactly**:
+
+| Documented | Actual | Status |
+|------------|--------|--------|
+| `CowriterAjaxController.php` | `AjaxController.php` | **WRONG** - name mismatch |
+| `AjaxController.php` | `AjaxController.php` | Correct |
+
+**Real-world example from t3x-cowriter review:**
+- AGENTS.md documented `Controller/CowriterAjaxController.php`
+- Actual file was `Controller/AjaxController.php`
+- This mismatch confused agents trying to find the file
+
+### Critical: Command Verification
+
+Commands documented in AGENTS.md must actually work when run:
+
+```bash
+# BAD: Document without testing
+make test-mutation  # May not exist!
+
+# GOOD: Verify before documenting
+make -n test-mutation 2>/dev/null && echo "EXISTS" || echo "MISSING"
+```
+
+**Real-world example from t3x-cowriter review:**
+- AGENTS.md documented `make test-mutation` and `make phpstan`
+- Neither target existed (actual was `make typecheck`)
+- Agents failed when trying to run documented commands
 
 ### Example Verification Commands
 
PATCH

echo "Gold patch applied."

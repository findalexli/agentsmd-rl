#!/usr/bin/env bash
set -euo pipefail

cd /workspace/flyai-skill

# Idempotency guard
if grep -qF "2. **Diagnose** \u2014 when a command fails or returns unexpected results, check the " "skills/flyai/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/flyai/SKILL.md b/skills/flyai/SKILL.md
@@ -86,6 +86,23 @@ flyai config set FLYAI_API_KEY "your-key"
 - **Marriott hotel search** (`search-marriott-hotel`): structuring Marriott Group's hotel results for deep comparison.
 - **Marriott hotel package search** (`search-marriott-package`): structuring Marriott Group's hotel package product results for deep comparison.
 
+## Error Handling
+
+1. **Validate** — before running a command, check that the inputs are reasonable.
+   - Dates should not be in the past and should match the expected format per the command's reference doc. Use `date +%Y-%m-%d` (see "Time and context support" above) as the baseline.
+   - Ambiguous or vague parameters (e.g. city names) should be confirmed with the user before searching.
+   - Do not guess missing required parameters — ask the user.
+2. **Diagnose** — when a command fails or returns unexpected results, check the output for error messages or status codes. Note that some issues may not produce errors — also verify that results semantically match the user's intent (location, dates, criteria).
+   - Parameter error → re-read the corresponding file in `references/` (see the References table below), fix the parameters, and retry.
+   - Service or network error → retry the command.
+   - Quota or permission error → inform the user and guide them to resolve the access issue.
+3. **Adapt** — if the command succeeds but results are empty or insufficient:
+   - Broaden the search: relax filters, or try `ai-search` / `keyword-search` with the user's original intent as a natural language query.
+   - Do not retry indefinitely — one fallback attempt is enough. If still no results, inform the user and suggest adjusting search criteria.
+4. **Be transparent** — when results appear incomplete or inconsistent with user expectations:
+   - Present available results and let the user know that results may not match the intended location or criteria.
+   - Suggest verifying through other channels if accuracy is critical.
+
 ## References
 Detailed command docs live in **`references/`** (one file per subcommand):
 
PATCH

echo "Gold patch applied."

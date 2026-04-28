#!/usr/bin/env bash
set -euo pipefail

cd /workspace/publications

# Idempotency guard
if grep -qF "- Every table row must have the same number of `|` delimiters as its header \u2014 no" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -37,6 +37,12 @@
 - Within each client subsection, sort reviews by date (newest first)
 - Do NOT include review counts in section headers (e.g., "#### Offchain Labs", not "#### Offchain Labs (32 reviews)")
 
+#### Table Column Structure
+- Security review tables use 5 columns: `| Product | Date | Effort | Announcement | Report |`
+- Every row must have exactly 6 pipe characters (matching the header row)
+- Do not add extra trailing pipes or columns beyond the header
+- Do not leave rows truncated with missing columns — pad with empty cells (`| |`) if data is unavailable
+
 #### Product Column Formatting
 - Product column should contain ONLY the product/project name
   - Do NOT include document types like "Letter of Attestation", "Design Review", "Code Review", "Security Review", "Threat Model"
@@ -121,7 +127,8 @@ bullet lists, sub-talk descriptions, blog links, team lists, etc.
 
 ### General Formatting Guidelines
 - Priority: Keep security review table rows fitting on single lines
-- Use double spaces in empty cells: `|  |` should be `| |`
+- Every table row must have the same number of `|` delimiters as its header — no truncated or extra-long rows
+- Use single space in empty cells: `| |` not `|  |`
 - Fix decimal formatting: `.2` should be `0.2`
 - Ensure proper spacing: `| 4|` should be `| 4 |`
 - When in doubt, favor brevity over verbosity while maintaining clarity
PATCH

echo "Gold patch applied."

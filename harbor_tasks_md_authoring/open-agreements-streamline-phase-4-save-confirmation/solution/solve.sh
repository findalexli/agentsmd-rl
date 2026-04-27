#!/usr/bin/env bash
set -euo pipefail

cd /workspace/open-agreements

# Idempotency guard
if grep -qF "The portal downloads the receipt as `Ecorp_Confirmation_<ServiceRequestNumber>.p" "skills/delaware-franchise-tax/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/delaware-franchise-tax/SKILL.md b/skills/delaware-franchise-tax/SKILL.md
@@ -155,17 +155,26 @@ If the user says "use playwright", "use the browser" or requests similar automat
    - **CRITICAL**: "Once you leave this screen, you will no longer be able to obtain a confirmation copy" — save/email before navigating away
    - Record the Service Request Number from the URL: `srNo=XXXXX`
 
-## Phase 4: Record and Remind
-
-Save a filing record with the following details:
-- Entity name
-- Delaware file number
-- Tax year
-- Calculation method used and intermediate values
-- Amount paid (tax + filing fee)
-- Confirmation number
-- Date filed
-- Next due date (March 1 of next year for corps, June 1 for LLCs)
+## Phase 4: Save Receipt and Remind
+
+### Save the confirmation PDF
+
+The downloaded confirmation PDF **is** the filing record — no need to create a separate one.
+
+The portal downloads the receipt as `Ecorp_Confirmation_<ServiceRequestNumber>.pdf` to the default Downloads folder. Move it to a durable location:
+- `~/Documents/Tax/Delaware/<EntityName>/` on local disk
+- A "Tax" or "Corporate Records" folder in cloud storage if available
+- Keep the original filename — it contains the Service Request Number for future reference
+
+```bash
+# Example
+mkdir -p ~/Documents/Tax/Delaware/My-Corp-Name
+mv ~/Downloads/Ecorp_Confirmation_*.pdf ~/Documents/Tax/Delaware/My-Corp-Name/
+```
+
+Ask the user where they keep tax records and move the file there.
+
+### Set a reminder
 
 Remind the user to set an annual reminder for approximately 2 weeks before the deadline:
 - **Mid-February** for corporations (March 1 deadline)
PATCH

echo "Gold patch applied."

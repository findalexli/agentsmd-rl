#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ai

# Idempotency guard
if grep -qF "reference, Call Control API guidance), messaging, WebRTC, number porting via" "telnyx-twilio-migration/skills/telnyx-twilio-migration/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/telnyx-twilio-migration/skills/telnyx-twilio-migration/SKILL.md b/telnyx-twilio-migration/skills/telnyx-twilio-migration/SKILL.md
@@ -2,9 +2,9 @@
 name: telnyx-twilio-migration
 description: >-
   Migrate from Twilio to Telnyx. Covers voice (TwiML to TeXML with full verb
-  reference), messaging, WebRTC, number porting via FastPort, and Verify.
-  Includes product mapping, migration scripts, and key differences in auth,
-  webhooks, and payload format.
+  reference, Call Control API guidance), messaging, WebRTC, number porting via
+  FastPort, and Verify. Includes product mapping, migration scripts, and key
+  differences in auth, webhooks, and payload format.
 metadata:
   author: telnyx
   product: migration
PATCH

echo "Gold patch applied."

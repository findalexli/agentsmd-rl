#!/usr/bin/env bash
set -euo pipefail

cd /workspace/home-assistant.io

# Idempotency guard
if grep -qF "Write from a second-person perspective, using \"you\" and \"your\" instead of \"the u" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -51,9 +51,8 @@ speakers.
 The writing needs to be inclusive, objective, and not gender biased, polarizing,
 or discriminatory. We want to be welcoming to all users.
 
-Write towards the reader directly, and not a group of users. Write from a second-person perspective, using "you" and "your" instead of "the user"
-second-person perspective, using "you" and "your" instead of "the user"
-or "users".
+Write towards the reader directly, and not a group of users. 
+Write from a second-person perspective, using "you" and "your" instead of "the user" or "users".
 
 Make the text feel personal and friendly, as if you are talking to a friend who
 really enjoys technology and enjoys this hobby of home automation. Write in
PATCH

echo "Gold patch applied."

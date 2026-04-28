#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react-email

# Idempotency guard
if grep -qF "- If the user is asking to use media queries, inform them that not all email cli" "skills/react-email/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/react-email/SKILL.md b/skills/react-email/SKILL.md
@@ -277,7 +277,7 @@ export default function Email() {
 
 ## Behavioral guidelines
 - When re-iterating over the code, make sure you are only updating what the user asked for and keeping the rest of the code intact;
-- If the user is asking to use media queries, inform them that email clients do not support them, and suggest a different approach;
+- If the user is asking to use media queries, inform them that not all email clients support them, and suggest a different approach;
 - Never use template variables (like {{name}}) directly in TypeScript code. Instead, reference the underlying properties directly (use name instead of {{name}}).
 - - For example, if the user explicitly asks for a variable following the pattern {{variableName}}, you should return something like this:
 
PATCH

echo "Gold patch applied."

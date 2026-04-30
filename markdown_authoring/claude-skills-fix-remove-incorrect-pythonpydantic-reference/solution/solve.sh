#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-skills

# Idempotency guard
if grep -qF "skills/php-pro/SKILL.md" "skills/php-pro/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/php-pro/SKILL.md b/skills/php-pro/SKILL.md
@@ -64,7 +64,6 @@ Load detailed guidance based on context:
 
 ### MUST NOT DO
 - Skip type declarations (no mixed types)
-- Use deprecated features or Pydantic V1 patterns
 - Store passwords in plain text (use bcrypt/argon2)
 - Write SQL queries vulnerable to injection
 - Mix business logic with controllers
PATCH

echo "Gold patch applied."

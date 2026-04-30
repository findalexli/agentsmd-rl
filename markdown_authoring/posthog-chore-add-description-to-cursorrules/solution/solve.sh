#!/usr/bin/env bash
set -euo pipefail

cd /workspace/posthog

# Idempotency guard
if grep -qF "description: Rules for writing Python services at PostHog (Python servers powere" ".cursor/rules/django-python.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/django-python.mdc b/.cursor/rules/django-python.mdc
@@ -1,5 +1,5 @@
 ---
-description: 
+description: Rules for writing Python services at PostHog (Python servers powered by the Django framework)
 globs: *.py
 alwaysApply: false
 ---
PATCH

echo "Gold patch applied."

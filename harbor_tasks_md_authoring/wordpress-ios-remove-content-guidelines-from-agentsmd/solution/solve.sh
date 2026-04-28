#!/usr/bin/env bash
set -euo pipefail

cd /workspace/wordpress-ios

# Idempotency guard
if grep -qF "AGENTS.md" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -51,9 +51,3 @@ WordPress-iOS uses a modular architecture with the main app and separate Swift p
 - Branch from `trunk` (main branch)
 - PR target should be `trunk`
 - When writing commit messages, never include references to Claude
-
-### Content Guidelines
-- **Include**: New features, UI improvements, performance enhancements, user experience changes
-- **Exclude**: CI changes, code refactoring, dependency updates, internal technical changes
-- **Language**: Positive sentiment, avoid "fix" terminology, focus on improvements and enhancements
-- **Priority Order**: New features → Improvements → Performance → Other user-facing changes
PATCH

echo "Gold patch applied."

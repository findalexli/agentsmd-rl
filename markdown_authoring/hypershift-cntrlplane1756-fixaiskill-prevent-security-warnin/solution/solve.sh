#!/usr/bin/env bash
set -euo pipefail

cd /workspace/hypershift

# Idempotency guard
if grep -qF "- [ ] Use \"!\" or `BREAKING CHANGE` for breaking changes" ".claude/skills/git-commit-format/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/git-commit-format/SKILL.md b/.claude/skills/git-commit-format/SKILL.md
@@ -123,7 +123,7 @@ When creating commits:
 - [ ] Include `Signed-off-by` footer
 - [ ] Include `Commit-Message-Assisted-by: Claude (via Claude Code)` footer
 - [ ] Validate with `make run-gitlint`
-- [ ] Use `!` or `BREAKING CHANGE` for breaking changes
+- [ ] Use "!" or `BREAKING CHANGE` for breaking changes
 
 ## Reference
 
PATCH

echo "Gold patch applied."

#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cultivation-world-simulator

# Idempotency guard
if grep -qF "gh pr create --head <github-username>/<branch-name> --base main --title \"<type>:" ".claude/skills/git-pr/SKILL.md" && grep -qF "description: Run Python tests using the project venv" ".claude/skills/test-validate/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/git-pr/SKILL.md b/.claude/skills/git-pr/SKILL.md
@@ -0,0 +1,30 @@
+---
+name: git-pr
+description: Create a pull request with proper remote handling
+---
+
+## Pre-flight
+
+```bash
+git remote -v
+# If origin URL is outdated, fix it:
+# git remote set-url origin https://github.com/AI-Cultivation/cultivation-world-simulator.git
+```
+
+## Commands
+
+```bash
+git checkout main && git pull origin main
+git checkout -b <github-username>/<branch-name>
+git add <files>
+git commit -m "<type>: <description>"
+git push -u origin <github-username>/<branch-name>
+gh pr create --head <github-username>/<branch-name> --base main --title "<type>: <description>" --body "<body>"
+```
+
+## Notes
+
+- Always branch off from `main`, not from current branch
+- Follow PR template in `.github/PULL_REQUEST_TEMPLATE.md`
+- `<github-username>`: e.g., `xzhseh`
+- `<type>`: `feat` | `fix` | `refactor` | `test` | `docs`
diff --git a/.claude/skills/test-validate/SKILL.md b/.claude/skills/test-validate/SKILL.md
@@ -0,0 +1,20 @@
+---
+name: test-validate
+description: Run Python tests using the project venv
+---
+
+## Commands
+
+```bash
+# Run all tests
+.venv/bin/pytest
+
+# Run specific test file
+.venv/bin/pytest tests/test_<name>.py -v
+
+# Run with coverage
+.venv/bin/pytest --cov=src
+
+# Run server (dev mode)
+.venv/bin/python src/server/main.py --dev
+```
PATCH

echo "Gold patch applied."

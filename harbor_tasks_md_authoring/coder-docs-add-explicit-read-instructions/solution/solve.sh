#!/usr/bin/env bash
set -euo pipefail

cd /workspace/coder

# Idempotency guard
if grep -qF "- `.claude/docs/ARCHITECTURE.md` \u2014 system overview (orientation or architecture " "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -297,6 +297,27 @@ comments preserve important context about why code works a certain way.
 @.claude/docs/PR_STYLE_GUIDE.md
 @.claude/docs/DOCS_STYLE_GUIDE.md
 
+If your agent tool does not auto-load `@`-referenced files, read these
+manually before starting work:
+
+**Always read:**
+
+- `.claude/docs/WORKFLOWS.md` — dev server, git workflow, hooks
+
+**Read when relevant to your task:**
+
+- `.claude/docs/GO.md` — Go patterns and modern Go usage (any Go changes)
+- `.claude/docs/TESTING.md` — testing patterns, race conditions (any test changes)
+- `.claude/docs/DATABASE.md` — migrations, SQLC, audit table (any DB changes)
+- `.claude/docs/ARCHITECTURE.md` — system overview (orientation or architecture work)
+- `.claude/docs/PR_STYLE_GUIDE.md` — PR description format (when writing PRs)
+- `.claude/docs/OAUTH2.md` — OAuth2 and RFC compliance (when touching auth)
+- `.claude/docs/TROUBLESHOOTING.md` — common failures and fixes (when stuck)
+- `.claude/docs/DOCS_STYLE_GUIDE.md` — docs conventions (when writing `docs/`)
+
+**For frontend work**, also read `site/AGENTS.md` before making any changes
+in `site/`.
+
 ## Local Configuration
 
 These files may be gitignored, read manually if not auto-loaded.
PATCH

echo "Gold patch applied."

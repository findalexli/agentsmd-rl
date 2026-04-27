#!/usr/bin/env bash
set -euo pipefail

cd /workspace/airflow

# Idempotency guard: if the gold patch has already been applied, do nothing.
if grep -q '### Tracking issues for deferred work' AGENTS.md; then
    echo "Patch already applied; skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
index 95fdcb1987fd0..c1a5007bffaa1 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -224,6 +224,55 @@ Remind the user to:
 2. Add a brief description of the changes at the top of the body.
 3. Reference related issues when applicable (`closes: #ISSUE` or `related: #ISSUE`).

+### Tracking issues for deferred work
+
+When a PR applies a **workaround, version cap, mitigation, or partial fix**
+rather than solving the underlying problem (for example: upper-binding a
+dependency to avoid a breaking upstream release, disabling a feature
+behind a flag, reverting a change that needs a better replacement, or
+papering over a bug so a release can ship), the deferred work must be
+captured in a GitHub tracking issue **and** the tracking issue URL must
+appear as a comment at the workaround site in the code.
+
+1. **Open the tracking issue first**, before finalising the PR body.
+2. **Reference it in the PR body by number** — e.g. "full migration is
+   tracked in #65609" — so anyone reviewing the PR can see what was
+   deferred and why.
+3. **Add a link to the tracking issue as a comment at the workaround
+   itself**, so the reference survives after the PR merges and anyone
+   reading the source later can click straight through to the follow-up
+   work. Use the **full issue URL**, not bare `#NNNNN` — bare references
+   do not auto-link outside GitHub's web UI (e.g. when grepping in an
+   editor, browsing a checkout, or reading the file in a terminal).
+   For example:
+
+   ```toml
+   # pyproject.toml
+   # Remove the <1.0 cap after migrating to httpx 1.x;
+   # tracked at https://github.com/apache/airflow/issues/65609
+   "httpx>=0.27.0,<1.0",
+   ```
+
+   ```python
+   # some_module.py
+   # Delete this fallback once the new client is on all workers;
+   # tracked at https://github.com/apache/airflow/issues/65609
+   if old_client:
+       ...
+   ```
+
+4. **Do not** write vague forward-looking phrases like "will open a
+   tracking issue" or "to be filed later" in the PR body or in code
+   comments. Open the issue, link it in both places, then submit the PR.
+5. The tracking issue should describe: what the workaround is, why it
+   was chosen, the concrete follow-up work needed, and any acceptance
+   criteria for removing the workaround.
+
+If a PR you already opened has such forward-looking language, open the
+tracking issue, add a PR comment referencing the issue URL, and push a
+follow-up commit that adds the tracking-issue URL as a comment at the
+workaround site in the code.
+
 ## Boundaries

 - **Ask first**
PATCH

echo "Gold patch applied."

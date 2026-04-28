#!/usr/bin/env bash
set -euo pipefail

cd /workspace/inspect-evals

# Idempotency guard
if grep -qF "- If the session surfaced a durable repo convention, reviewer expectation, or re" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -38,7 +38,7 @@ We recommend starting with these Claude Code permissions to allow workflows to p
       "Bash(uv run inspect:*)",
       "Bash(uv run pytest:*)",
       "Bash(uv run mypy:*)",
-      "Bash(uv run python tools/:*),
+      "Bash(uv run python tools/:*)",
       "WebFetch(domain:inspect.aisi.org.uk)",
       "WebFetch(domain:arxiv.org)"
     ],
@@ -69,6 +69,20 @@ This workflow runs a series of workflows each in turn. Each workflow is to be ru
 
 ## General Agent Tips
 
+### Skill Hygiene
+
+- At a natural stopping point in a session, briefly consider whether any of the work just completed would make a good reusable skill.
+- Also consider whether any skill used during the session is now missing steps, has outdated guidance, or could be made more robust based on what was learned.
+- Do **not** create or update a skill automatically. Ask the user first whether they want you to do that.
+- When asking, give a short recommendation that includes:
+  - what should be created or updated
+  - why it would be useful again
+  - who or what it would apply to
+  - whether this is better handled as a new skill or an update to an existing one
+- Prefer improving an existing skill over creating a new one when there is substantial overlap.
+- Do not suggest a new skill for one-off work, highly personal preferences, or tasks that are too small to justify maintenance overhead.
+- If the session surfaced a durable repo convention, reviewer expectation, or repeated failure mode, consider whether it should also be captured in REPO_CONTEXT.md or AGENTS.md, but ask the user before making that change.
+
 ### PR Guidelines
 
 - Before opening a new PR, run appropriate linting from `.github/workflows/build.yml`.
PATCH

echo "Gold patch applied."

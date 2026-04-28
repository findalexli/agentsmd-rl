#!/usr/bin/env bash
set -euo pipefail

cd /workspace/consensus-specs

# Idempotency guard
if grep -qF "linter makes modifications, stage these fixes. Ensure relevant tests pass if the" ".claude/skills/commit/SKILL.md" && grep -qF "Titles should use sentence case, not title case. Titles must be fewer than 68" ".claude/skills/prepare-release/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/commit/SKILL.md b/.claude/skills/commit/SKILL.md
@@ -0,0 +1,39 @@
+---
+name: commit
+description: >-
+  Commit changes and open pull requests. Follow the project's conventions
+  for scope, formatting, and writing style. Use when the user asks to make
+  a commit or pull request.
+compatibility: Requires make, uv, git
+---
+
+# Committing changes
+
+## Scope
+
+A pull request should have a single, well-defined objective. If a change
+accomplishes multiple unrelated things, split it into separate pull requests.
+For a large change with one objective, break it into multiple commits when
+possible. Each commit should adhere to the preparation steps below.
+
+## Preparation
+
+Check that the branch is up to date with `ethereum/consensus-specs@master`;
+rebase if it is not. Run the linter (`make lint`) and ensure it passes. If the
+linter makes modifications, stage these fixes. Ensure relevant tests pass if the
+specifications or testing framework changed.
+
+## Writing style
+
+The subject line (and PR title) must be written in the imperative mood. It must
+not have component prefixes like the "conventional commit" style. It must be
+less than or equal to 68 characters. Use sentence case, not title case. Code
+(functions, classes, etc) must be wrapped in backticks. There must be no
+terminal punctuation.
+
+The body (and PR description) should describe what and why, not how. Wrap the
+body at 72 characters. Do not use section headers. A single paragraph is ideal,
+but multiple paragraphs are okay if necessary. Keep things simple and try to be
+concise. Mention any relevant information, concerns, or related PRs/issues. Do
+not mention running the linter or tests; CI will show this. Do not include a
+`Co-Authored-By` trailer.
diff --git a/.claude/skills/prepare-release/SKILL.md b/.claude/skills/prepare-release/SKILL.md
@@ -44,7 +44,7 @@ Review the PRs since the last release and provide a list of recommendations to
 the user. If necessary, the user will manually update PR titles prior to
 starting the release action. Titles must be written in the imperative mood.
 Titles must not have component prefixes like the "conventional commit" style.
-Titles should use sentence case, not title case. Titles must be fewer than 72
+Titles should use sentence case, not title case. Titles must be fewer than 68
 characters long. Titles should not be too vague. Words that are clearly code
 (functions, classes, etc) must be wrapped in backticks. There must be no
 terminal punctuation and ideally no punctuation at all. Titles must not contain
PATCH

echo "Gold patch applied."

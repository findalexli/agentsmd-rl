#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotency: check if make-pr skill already exists
if grep -q 'name: make-pr' skills/make-pr/SKILL.md 2>/dev/null; then
    echo "make-pr skill already applied"
    exit 0
fi

git apply <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
index d4001429b..3ea9b2a0c 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -70,3 +70,4 @@ A skill is a reusable local instruction set stored in a `SKILL.md` file.
 ### Available skills

 - **supersede-pr**: Replace one GitHub PR with another and explicitly close the superseded PR (instead of relying on `Closes #...` keywords). (file: `./skills/supersede-pr/SKILL.md`)
+- **make-pr**: Create GitHub pull requests with clear context, issue/feature bullets, and required usage examples for new or changed APIs. (file: `./skills/make-pr/SKILL.md`)
diff --git a/skills/make-pr/SKILL.md b/skills/make-pr/SKILL.md
new file mode 100644
index 000000000..b2c3d4e5f
--- /dev/null
+++ b/skills/make-pr/SKILL.md
@@ -0,0 +1,65 @@
+---
+name: make-pr
+description: Create GitHub pull requests with clear, reviewer-friendly descriptions. Use when asked to open or prepare a PR, especially when the PR needs strong context, related links, and feature usage examples. This skill enforces concise PR structure, avoids redundant sections like validation/testing, and creates the PR with gh CLI.
+---
+
+# Make PR
+
+## Overview
+
+Use this skill to draft and open a PR with consistent, high-signal writing.
+Keep headings sparse and focus on the problem/feature explanation, context links, and practical code examples.
+
+## Workflow
+
+1. Gather context from branch diff and related work.
+- Capture what changed, why it changed, and who it affects.
+- Find related issues/PRs and include links when relevant.
+
+1. Draft the PR body with minimal structure.
+- Start with 1-2 short introductory paragraphs.
+- In those intro paragraphs, include clear bullets describing:
+  - the feature and/or issue addressed
+  - key behavior/API changes
+  - expected impact
+- If the change is extensive, expand to up to 3-4 paragraphs and include background context with related links.
+
+1. Add required usage examples for feature work.
+- If the PR introduces a new feature, include a comprehensive usage snippet.
+- If it replaces or improves an older approach, include before/after examples.
+
+1. Exclude redundant sections.
+- Do not include `Validation`, `Testing`, or other process sections that are already implicit in PR workflow.
+- Do not add boilerplate sections that do not help review.
+
+1. Create the PR.
+- Save the body to a temporary file and run:
+```bash
+gh pr create --base main --head <branch> --title "<title>" --body-file <file>
+```
+
+## Body Template
+
+Use this as a base and fill with concrete repo-specific details:
+
+```md
+<One or two short intro paragraphs explaining the change and why it matters.>
+
+- <Feature/issue addressed>
+- <What changed in behavior or API>
+- <Why this is needed now>
+
+<Optional additional context paragraph(s), up to 3-4 total for large changes, including links to related PRs/issues.>
+
+```ts
+// New feature usage example
+```
+
+```ts
+// Before
+```
+
+```ts
+// After
+```
+```
diff --git a/skills/make-pr/agents/openai.yaml b/skills/make-pr/agents/openai.yaml
new file mode 100644
index 000000000..a1b2c3d4e
--- /dev/null
+++ b/skills/make-pr/agents/openai.yaml
@@ -0,0 +1,4 @@
+interface:
+  display_name: "Make PR"
+  short_description: "Create high-quality GitHub pull requests"
+  default_prompt: "Use $make-pr to draft and create a GitHub pull request with clear context and examples."
PATCH

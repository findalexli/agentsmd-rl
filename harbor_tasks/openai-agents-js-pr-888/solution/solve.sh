#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openai-agents-js

# Apply the gold patch
git apply <<'PATCH'
diff --git a/.codex/skills/changeset-validation/SKILL.md b/.codex/skills/changeset-validation/SKILL.md
index 29ac91610..c3bd5c1c6 100644
--- a/.codex/skills/changeset-validation/SKILL.md
+++ b/.codex/skills/changeset-validation/SKILL.md
@@ -9,6 +9,7 @@ description: Validate changesets in openai-agents-js using LLM judgment against

 This skill validates whether changesets correctly reflect package changes and follow the repository rules. It relies on the shared prompt in `references/validation-prompt.md` so local Codex reviews and GitHub Actions share the same logic.
 Experimental or preview-only feature additions that are explicitly labeled as such in the diff may remain a patch bump when they do not change existing behavior.
+Major bumps are only allowed after the first major release; before that, do not use major bumps for feature-level changes.

 ## Quick start

@@ -33,7 +34,7 @@ CI (Codex Action):

 1. Generate the prompt context via `pnpm changeset:validate`.
 2. Apply the rules in `references/validation-prompt.md` to judge correctness.
-3. Provide a clear verdict and required bump (patch/minor/none).
+3. Provide a clear verdict and required bump (patch/minor/major/none).
 4. If the changeset needs edits, update it and re-run the validation.

 ## Shared source of truth
diff --git a/.codex/skills/changeset-validation/references/validation-prompt.md b/.codex/skills/changeset-validation/references/validation-prompt.md
index 5fea258f3..b03b696f3 100644
--- a/.codex/skills/changeset-validation/references/validation-prompt.md
+++ b/.codex/skills/changeset-validation/references/validation-prompt.md
@@ -7,7 +7,7 @@ Return JSON only. The output must be a JSON object with:
 - ok: boolean
 - errors: string[] (polite, actionable English sentences)
 - warnings: string[] (polite, actionable English sentences)
-- required_bump: "patch" | "minor" | "none"
+- required_bump: "patch" | "minor" | "major" | "none"

 Always use English in errors and warnings, regardless of the conversation language.

@@ -19,7 +19,7 @@ Rules to enforce:
 4. If no packages changed, changesets are optional; if present, they still must be consistent with the diff.
 5. Each changeset summary must be 1-2 non-empty lines.
 6. If the PR body contains GitHub issue references like #123 and a changeset exists, the changeset summary should include those references.
-7. Default bump is patch. Minor is allowed only when changes include breaking changes, dropped support, or a major feature addition. Exception: if the new feature is explicitly labeled experimental/preview in the diff (e.g., module name, docs, comments, or exports) and does not change existing behavior, a patch bump is acceptable.
+7. Default bump is patch. Minor is allowed only when changes include breaking changes, dropped support, or a major feature addition. Major is allowed only after the first major release and only for changes that warrant a major release (breaking changes, dropped support, or significant behavior shifts). Before the first major release, do not use major bumps for feature-level changes. Exception: if the new feature is explicitly labeled experimental/preview in the diff (e.g., module name, docs, comments, or exports) and does not change existing behavior, a patch bump is acceptable.
 8. required_bump must be "none" when there are no package changes.
 9. If unknown package directories are changed, treat it as an error.

diff --git a/.codex/skills/changeset-validation/scripts/changeset-assign-milestone.mjs b/.codex/skills/changeset-validation/scripts/changeset-assign-milestone.mjs
index 5c23d17ab..082c7fc8b 100755
--- a/.codex/skills/changeset-validation/scripts/changeset-assign-milestone.mjs
+++ b/.codex/skills/changeset-validation/scripts/changeset-assign-milestone.mjs
@@ -83,8 +83,8 @@ async function assignMilestone(requiredBump) {
     .filter((entry) => entry.parsed)
     .sort((a, b) => {
       if (a.parsed.major !== b.parsed.major)
-        return b.parsed.major - a.parsed.major;
-      return b.parsed.minor - a.parsed.minor;
+        return a.parsed.major - b.parsed.major;
+      return a.parsed.minor - b.parsed.minor;
     });

   if (parsed.length === 0) {
@@ -94,9 +94,34 @@ async function assignMilestone(requiredBump) {
     return;
   }

-  const patchTarget = parsed[parsed.length - 1];
-  const minorTarget = parsed[1] ?? parsed[0];
-  const targetEntry = requiredBump === 'minor' ? minorTarget : patchTarget;
+  const majors = Array.from(
+    new Set(parsed.map((entry) => entry.parsed.major)),
+  ).sort((a, b) => a - b);
+  const currentMajor = majors[0];
+  const nextMajor = majors[1];
+
+  const currentMajorEntries = parsed.filter(
+    (entry) => entry.parsed.major === currentMajor,
+  );
+  const patchTarget = currentMajorEntries[0];
+  const minorTarget = currentMajorEntries[1] ?? patchTarget;
+
+  let majorTarget;
+  if (nextMajor !== undefined) {
+    const nextMajorEntries = parsed.filter(
+      (entry) => entry.parsed.major === nextMajor,
+    );
+    majorTarget = nextMajorEntries[0];
+  }
+
+  let targetEntry;
+  if (requiredBump === 'major') {
+    targetEntry = majorTarget;
+  } else if (requiredBump === 'minor') {
+    targetEntry = minorTarget;
+  } else {
+    targetEntry = patchTarget;
+  }
   if (!targetEntry) {
     console.warn(
       'Milestone assignment skipped (not enough open milestones for selection).',
diff --git a/.codex/skills/changeset-validation/scripts/changeset-validation-result.mjs b/.codex/skills/changeset-validation/scripts/changeset-validation-result.mjs
index 1f38fb184..950e440fc 100755
--- a/.codex/skills/changeset-validation/scripts/changeset-validation-result.mjs
+++ b/.codex/skills/changeset-validation/scripts/changeset-validation-result.mjs
@@ -17,8 +17,8 @@ function validateShape(data) {
   if (typeof data?.ok !== 'boolean') return 'Missing ok boolean.';
   if (!Array.isArray(data?.errors)) return 'Missing errors array.';
   if (!Array.isArray(data?.warnings)) return 'Missing warnings array.';
-  if (!['patch', 'minor', 'none'].includes(data?.required_bump)) {
-    return 'Missing required_bump with value patch/minor/none.';
+  if (!['patch', 'minor', 'major', 'none'].includes(data?.required_bump)) {
+    return 'Missing required_bump with value patch/minor/major/none.';
   }
   return null;
 }
diff --git a/.github/codex/schemas/changeset-validation.json b/.github/codex/schemas/changeset-validation.json
index 2bec09848..364cb1fe5 100644
--- a/.github/codex/schemas/changeset-validation.json
+++ b/.github/codex/schemas/changeset-validation.json
@@ -19,7 +19,7 @@
     },
     "required_bump": {
       "type": "string",
-      "enum": ["patch", "minor", "none"]
+      "enum": ["patch", "minor", "major", "none"]
     }
   },
   "additionalProperties": false
diff --git a/.github/workflows/changeset.yml b/.github/workflows/changeset.yml
index 0ef470ac8..8f74ffa47 100644
--- a/.github/workflows/changeset.yml
+++ b/.github/workflows/changeset.yml
@@ -60,3 +60,85 @@ jobs:
         env:
           GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
         run: pnpm changeset:assign-milestone -- .github/codex/outputs/changeset-validation.json
+
+      - name: Sync package labels
+        if: ${{ steps.run_codex.conclusion == 'success' }}
+        uses: actions/github-script@v8
+        with:
+          github-token: ${{ secrets.GITHUB_TOKEN }}
+          script: |
+            const fs = require('fs');
+            const { execSync } = require('child_process');
+
+            const baseSha = context.payload.pull_request.base.sha;
+            const headSha = context.payload.pull_request.head.sha;
+
+            const diff = execSync(
+              `git diff --name-only ${baseSha} ${headSha} -- .changeset`,
+              { encoding: 'utf8' },
+            ).trim();
+            const files = diff ? diff.split(/\r?\n/).filter(Boolean) : [];
+            const changesetFiles = files.filter(
+              (file) => file.endsWith('.md') && !file.endsWith('README.md'),
+            );
+
+            const packageToLabel = {
+              '@openai/agents-core': 'package:agents-core',
+              '@openai/agents-openai': 'package:agents-openai',
+              '@openai/agents-realtime': 'package:agents-realtime',
+              '@openai/agents-extensions': 'package:agents-extensions',
+            };
+
+            const desired = new Set();
+            for (const file of changesetFiles) {
+              if (!fs.existsSync(file)) {
+                continue;
+              }
+              const content = fs.readFileSync(file, 'utf8');
+              const parts = content.split('---');
+              if (parts.length < 3) {
+                continue;
+              }
+              const frontmatter = parts[1];
+              for (const line of frontmatter.split(/\r?\n/)) {
+                const match = line.match(/["']?([^"':]+)["']?\s*:/);
+                if (!match) continue;
+                const pkg = match[1].trim();
+                const label = packageToLabel[pkg];
+                if (label) desired.add(label);
+              }
+            }
+
+            const packageLabels = new Set(Object.values(packageToLabel));
+            const { data: issue } = await github.rest.issues.get({
+              owner: context.repo.owner,
+              repo: context.repo.repo,
+              issue_number: context.issue.number,
+            });
+            const existing = issue.labels.map((label) =>
+              typeof label === 'string' ? label : label.name,
+            );
+            const preserved = existing.filter(
+              (label) => !packageLabels.has(label),
+            );
+            const finalLabels = Array.from(new Set([...preserved, ...desired]));
+
+            const normalize = (labels) => labels.slice().sort();
+            const same =
+              normalize(existing).join('\n') === normalize(finalLabels).join('\n');
+
+            if (same) {
+              console.log('Package labels already up to date.');
+              return;
+            }
+
+            await github.rest.issues.setLabels({
+              owner: context.repo.owner,
+              repo: context.repo.repo,
+              issue_number: context.issue.number,
+              labels: finalLabels,
+            });
+
+            console.log(
+              `Updated labels: ${finalLabels.join(', ') || '(none)'}`,
+            );
PATCH

# Verify idempotency marker
grep -q "Major bumps are only allowed after the first major release" .codex/skills/changeset-validation/SKILL.md

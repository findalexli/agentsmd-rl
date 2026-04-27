#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "Otherwise, run the full decision: if the branch diff changes observable behavior" "plugins/compound-engineering/skills/ce-commit-push-pr/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-commit-push-pr/SKILL.md b/plugins/compound-engineering/skills/ce-commit-push-pr/SKILL.md
@@ -192,7 +192,13 @@ git diff <base-remote>/<base-branch>...HEAD
 
 Use this branch diff (not the working-tree diff) for the evidence decision. If the branch diff is empty (e.g., HEAD is already merged into the base or the branch has no unique commits), skip the evidence prompt and continue to delegation.
 
-**Evidence decision (before delegation).** If the branch diff changes observable behavior (UI, CLI output, API behavior with runnable code, generated artifacts, workflow output) and evidence is not otherwise blocked (unavailable credentials, paid services, deploy-only infrastructure, hardware), ask: "This PR has observable behavior. Capture evidence for the PR description?"
+**Evidence decision (before delegation).** Before running the full decision, two short-circuits:
+
+1. **User explicitly asked for evidence.** If the user's invocation requested it ("ship with a demo", "include a screenshot"), proceed directly to capture. If capture turns out to be not possible (no runnable surface, missing credentials, docs-only diff) or clearly not useful, note that briefly and proceed without evidence — do not force capture for its own sake.
+
+2. **Agent judgment on authored changes.** If you authored the commits in this session and know the change is clearly non-observable (internal plumbing, backend refactor without user-facing effect, type-level changes, etc.), skip the prompt without asking. The categorical skip list below is not exhaustive — trust judgment about the change you just wrote.
+
+Otherwise, run the full decision: if the branch diff changes observable behavior (UI, CLI output, API behavior with runnable code, generated artifacts, workflow output) and evidence is not otherwise blocked (unavailable credentials, paid services, deploy-only infrastructure, hardware), ask: "This PR has observable behavior. Capture evidence for the PR description?"
 
 - **Capture now** -- load the `ce-demo-reel` skill with a target description inferred from the branch diff. ce-demo-reel returns `Tier`, `Description`, `URL`, and `Path`. Exactly one of `URL` or `Path` contains a real value; the other is `"none"`. If capture returns a public URL, pass it as steering to `ce-pr-description` (e.g., "include the captured demo: <URL> as a `## Demo` section") or splice into the returned body before apply. If capture returns a local `Path` instead (user chose local save), pass steering that notes evidence was captured but is local-only (e.g., "evidence was captured locally — note in the PR that a demo was recorded but is not embedded because the user chose local save"). If capture returns `Tier: skipped` or both `URL` and `Path` are `"none"`, proceed with no evidence.
 - **Use existing evidence** -- ask for the URL or markdown embed, then pass it as free-text steering to `ce-pr-description` or splice in before apply.
PATCH

echo "Gold patch applied."

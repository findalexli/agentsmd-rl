#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gsd-2

# Idempotency guard
if grep -qF "description: \"Block completion claims until verification evidence has been produ" "src/resources/skills/verify-before-complete/SKILL.md" && grep -qF "description: \"Collaborative document authoring workflow for proposals, technical" "src/resources/skills/write-docs/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/resources/skills/verify-before-complete/SKILL.md b/src/resources/skills/verify-before-complete/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: verify-before-complete
-description: Block completion claims until verification evidence has been produced in the current message. Use before marking a task/slice/milestone complete, before creating a commit or PR, before saying "it works" or "tests pass", and any time you are about to claim work is done. The rule is: evidence before claims, always — running the verification must happen now, not "earlier in the session". Fresh output or no claim.
+description: "Block completion claims until verification evidence has been produced in the current message. Use before marking a task/slice/milestone complete, before creating a commit or PR, before saying \"it works\" or \"tests pass\", and any time you are about to claim work is done. The rule is: evidence before claims, always — running the verification must happen now, not \"earlier in the session\". Fresh output or no claim."
 ---
 
 <objective>
diff --git a/src/resources/skills/write-docs/SKILL.md b/src/resources/skills/write-docs/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: write-docs
-description: Collaborative document authoring workflow for proposals, technical specs, decision docs, README sections, ADRs, and long-form prose that must work for fresh readers. Use when asked to "write the docs", "draft a proposal", "write a spec", "write an RFC", "write the README", or when a document needs to be understandable by someone without this session's context. Three stages: gather context, iterate on structure, reader-test for a stranger.
+description: "Collaborative document authoring workflow for proposals, technical specs, decision docs, README sections, ADRs, and long-form prose that must work for fresh readers. Use when asked to \"write the docs\", \"draft a proposal\", \"write a spec\", \"write an RFC\", \"write the README\", or when a document needs to be understandable by someone without this session's context. Three stages: gather context, iterate on structure, reader-test for a stranger."
 ---
 
 <objective>
PATCH

echo "Gold patch applied."

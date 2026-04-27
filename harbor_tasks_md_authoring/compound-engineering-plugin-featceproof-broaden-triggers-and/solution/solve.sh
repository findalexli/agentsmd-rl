#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "description: Create, share, view, comment on, edit, and run human-in-the-loop re" "plugins/compound-engineering/skills/ce-proof/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-proof/SKILL.md b/plugins/compound-engineering/skills/ce-proof/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: ce-proof
-description: Create, edit, comment on, share, and run human-in-the-loop iteration loops over markdown documents via Proof's web API. Use when asked to "proof", "share a doc", "create a proof doc", "comment on a document", "suggest edits", "review in proof", "iterate on this doc in proof", "HITL this doc", "sync a Proof doc to local", when a caller needs an HITL review loop over a local markdown file (e.g., ce-brainstorm, ce-ideate, or ce-plan handoff), or when given a proofeditor.ai URL. Prefer this skill for any workflow whose output is a Proof URL or that uses a Proof doc as the review surface, even when not named explicitly.
+description: Create, share, view, comment on, edit, and run human-in-the-loop review loops over markdown documents via Proof — the collaborative markdown editor and renderer at proofeditor.ai (also called "Proof editor"). Use this skill whenever the user wants to view or render a local markdown file in Proof for easier reading, share a markdown file to Proof to get a shareable URL, iterate on a Proof doc collaboratively, comment on or suggest edits in a Proof doc, HITL a spec/plan/draft for human review, sync a Proof doc back to local, or when given a proofeditor.ai URL. Common phrasings include "view this in proof", "render this markdown in proof", "open this md file in proof", "share it to proof", "share to proof editor", "iterate with proof", "HITL this doc". Upstream handoffs from ce-brainstorm / ce-ideate / ce-plan for human review also belong here. Match these intents even when the user doesn't name Proof, as long as they clearly want a rendered/shared markdown surface. Do NOT trigger on "proof" meaning evidence, a mathematical/logical proof, burden of proof, proof-of-concept, or a bare "proofread this" request where the model is expected to review text inline.
 allowed-tools:
   - Bash
   - Read
@@ -26,7 +26,10 @@ Set the display name once per doc session by posting to presence with the `X-Age
 
 ## Human-in-the-Loop Review Mode
 
-When a caller (e.g., `ce-brainstorm`, `ce-plan`) needs to upload a local markdown doc, collect structured human feedback in Proof, and sync the final doc back to disk, load `references/hitl-review.md` for the full loop spec: invocation contract, mark classification (change / question / objection / ambiguous), idempotent ingest passes, exception-based terminal reporting, and end-sync atomic write.
+Human-in-the-loop iteration over an existing local markdown file: upload to Proof, let the user annotate in Proof's web UI, ingest feedback as in-thread replies and tracked edits, and sync the final doc back to disk. Two entry points, identical mechanics — load `references/hitl-review.md` for the full loop spec (invocation contract, mark classification, idempotent ingest passes, exception-based terminal reporting, end-sync atomic write) in either case:
+
+- **Direct user request** — a bare user phrase naming a local markdown file and asking to iterate collaboratively via Proof: "share this to proof so we can iterate", "iterate with proof on this doc", "HITL this file with me", "let's get feedback on this in proof", "open this in proof editor so I can review". The file is whichever markdown the user just created, edited, or referenced; if ambiguous, ask which file. This is a first-class entry point — do not require an upstream caller.
+- **Upstream skill handoff** — `ce-brainstorm`, `ce-ideate`, or `ce-plan` finishes a draft and hands it off for human review before the next phase, passing the file path and title explicitly.
 
 ## Web API (Primary for Sharing)
 
PATCH

echo "Gold patch applied."

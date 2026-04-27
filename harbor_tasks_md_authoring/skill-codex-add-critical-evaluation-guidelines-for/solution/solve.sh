#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skill-codex

# Idempotency guard
if grep -qF "echo \"This is Claude (Opus 4.5) following up. I disagree with [X] because [evide" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -35,6 +35,29 @@ description: Use when the user asks to run Codex CLI (codex exec, codex resume)
 - When resuming, pipe the new prompt via stdin: `echo "new prompt" | codex exec resume --last 2>/dev/null`. The resumed session automatically uses the same model, reasoning effort, and sandbox mode from the original session.
 - Restate the chosen model, reasoning effort, and sandbox mode when proposing follow-up actions.
 
+## Critical Evaluation of Codex Output
+
+Codex is powered by OpenAI models with their own knowledge cutoffs and limitations. Treat Codex as a **colleague, not an authority**.
+
+### Guidelines
+- **Trust your own knowledge** when confident. If Codex claims something you know is incorrect (e.g., "Claude Opus 4.5 doesn't exist"), push back directly.
+- **Research disagreements** using WebSearch or documentation before accepting Codex's claims. Share findings with Codex via resume if needed.
+- **Remember knowledge cutoffs** - Codex may not know about recent releases, APIs, or changes that occurred after its training data.
+- **Don't defer blindly** - Codex can be wrong. Evaluate its suggestions critically, especially regarding:
+  - Model names and capabilities
+  - Recent library versions or API changes
+  - Best practices that may have evolved
+
+### When Codex is Wrong
+1. State your disagreement clearly to the user
+2. Provide evidence (your own knowledge, web search, docs)
+3. Optionally resume the Codex session to discuss the disagreement. **Identify yourself as Claude** so Codex knows it's a peer AI discussion:
+   ```bash
+   echo "This is Claude (Opus 4.5) following up. I disagree with [X] because [evidence]. What's your take on this?" | codex exec --skip-git-repo-check resume --last 2>/dev/null
+   ```
+4. Frame disagreements as discussions, not corrections - either AI could be wrong
+5. Let the user decide how to proceed if there's genuine ambiguity
+
 ## Error Handling
 - Stop and report failures whenever `codex --version` or a `codex exec` command exits non-zero; request direction before retrying.
 - Before you use high-impact flags (`--full-auto`, `--sandbox danger-full-access`, `--skip-git-repo-check`) ask the user for permission using AskUserQuestion unless it was already given.
PATCH

echo "Gold patch applied."

#!/usr/bin/env bash
set -euo pipefail

cd /workspace/spawn

# Idempotency guard
if grep -qF "{a short casual reply, written like a real dev on reddit. Keep it TIGHT: 1-3 sen" ".claude/skills/setup-agent-team/growth-prompt.md" && grep -qF "- **BANNED terms in tweets**: `ps aux`, `OAuth`, `SigV4`, `TLS`, `CORS`, `RBAC`," ".claude/skills/setup-agent-team/tweet-prompt.md" && grep -qF "- Add \"(disclosure: i help build this)\" ONLY if it fits \u2014 if the reply is too sh" ".claude/skills/setup-agent-team/x-engage-prompt.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/setup-agent-team/growth-prompt.md b/.claude/skills/setup-agent-team/growth-prompt.md
@@ -99,7 +99,7 @@ Poster qualification:
 Relevance score: {score}/10
 
 Draft reply:
-{a short casual reply the team could use, written like a real dev on reddit. 2-3 sentences. **ABSOLUTELY NO em dashes (—) or en dashes (–) — use periods, commas, or rephrase. This is non-negotiable, em dashes are an AI tell.** No corporate speak, lowercase ok. end with "disclosure: i help build this" if mentioning spawn}
+{a short casual reply, written like a real dev on reddit. Keep it TIGHT: 1-3 sentences max. Lowercase is fine. No corporate speak, no feature lists, no "one command to provision". Sound like you're typing a quick comment, not writing marketing copy. **ABSOLUTELY NO em dashes (—) or en dashes (–). Use periods, commas, or rephrase.** End with "disclosure: i help build this" when mentioning spawn.}
 === END CANDIDATE ===
 ```
 
diff --git a/.claude/skills/setup-agent-team/tweet-prompt.md b/.claude/skills/setup-agent-team/tweet-prompt.md
@@ -1,8 +1,10 @@
 # Tweet Draft — Daily Spawn Update
 
-You are a developer advocate composing a single tweet (max 280 characters) about the Spawn project (<https://github.com/OpenRouterTeam/spawn>).
+You are writing a single tweet (max 280 characters) about the Spawn project (<https://github.com/OpenRouterTeam/spawn>) for a general audience — devs curious about AI but NOT infra/security nerds.
 
-Spawn is a matrix of **agents x clouds** — it provisions a cloud VM, installs a coding agent (Claude Code, Codex, OpenCode, etc.), injects OpenRouter credentials, and drops you into an interactive session. One `curl | bash` command.
+Spawn lets anyone spin up an AI coding agent (Claude, Codex, etc.) on a cheap cloud server with one command. That's it. Think "AI coding assistant in the cloud, ready in 30 seconds."
+
+**Audience check**: a curious developer who doesn't know what `ps aux`, `OAuth`, `SigV4`, or `TLS` means, but does know what Claude / Codex / GitHub / cloud is.
 
 ## Past Tweet Decisions
 
@@ -16,22 +18,23 @@ GIT_DATA_PLACEHOLDER
 
 ## Your Task
 
-1. **Scan the git data** for the single most tweet-worthy item. Prioritize:
-   - New user-facing features (`feat(...)` commits) — most valuable
-   - Interesting bug fixes that show engineering rigor or security awareness
-   - Developer workflow improvements, CLI enhancements
-   - Best practices demonstrated in how issues were triaged and resolved
+1. **Scan the git data** for the single most tweet-worthy item. Prioritize what a non-technical dev would care about:
+   - New user-facing features (`feat(...)` commits) — MOST valuable, easiest to explain
+   - New agent/cloud additions (T3 Code, Hetzner, etc.) — concrete and exciting
+   - Avoid: low-level security fixes, OAuth changes, type-safety refactors, CI tweaks, internal plumbing
+   - If the only notable commits are internal/infra, output `found: false` — no tweet is better than a boring technical tweet
 
 2. **Draft exactly 1 tweet**, max 280 characters. Rules:
-   - Write like a developer sharing something cool, not a marketing team
-   - No corporate speak, no buzzwords, no "excited to announce"
-   - **NEVER use em dashes (—) or en dashes (–).** Use a period, comma, or rephrase. This is non-negotiable — em dashes are a tell that AI wrote it.
+   - Casual, short, and plain-English. No jargon a beginner wouldn't get.
+   - **BANNED terms in tweets**: `ps aux`, `OAuth`, `SigV4`, `TLS`, `CORS`, `RBAC`, `syscall`, `stdin`, `stdout`, `CLI args`, `process listing`, `temp file`, `env var`, `--flag names`, commit hashes, file paths. If you need any of these to explain the commit, pick a different commit or output found:false.
+   - Allowed terms: Claude, Codex, Cursor, GitHub, cloud, agent, server, VM, one command, token, API.
+   - Write like you're texting a friend who likes tech. "just added X", "now you can Y", "spin up a whole AI coding setup in 30 seconds"
+   - No corporate speak, no "excited to announce", no "we're thrilled"
+   - **NEVER use em dashes (—) or en dashes (–).** Use a period, comma, or rephrase.
    - At most 1 hashtag (only if it fits naturally)
-   - Mention `@OpenRouterTeam` only if it fits naturally
-   - OK to include a short URL like `https://openrouter.ai/spawn`
-   - If referencing a specific feature, be concrete ("added Hetzner support" not "expanded cloud coverage")
+   - OK to include `https://openrouter.ai/spawn`
 
-3. **If nothing is tweet-worthy** (no notable changes, or all recent commits are internal/infra), output `found: false`.
+3. **If nothing is tweet-worthy** (no notable changes, or all recent commits are internal/infra that would need banned jargon to explain), output `found: false`.
 
 ## Output Format
 
diff --git a/.claude/skills/setup-agent-team/x-engage-prompt.md b/.claude/skills/setup-agent-team/x-engage-prompt.md
@@ -23,14 +23,20 @@ X_DATA_PLACEHOLDER
 
 2. **Pick exactly 1 best engagement opportunity** (score 7+ to qualify).
 
-3. **Draft a reply** (max 280 characters):
-   - Be helpful first, promotional second
-   - Answer their question or add to the conversation
-   - Mention Spawn only if it genuinely fits what they are discussing
-   - Casual, developer-to-developer tone
-   - **NEVER use em dashes (—) or en dashes (–).** Use a period, comma, or rephrase. Em dashes are an AI tell and must be avoided.
-   - Include `https://openrouter.ai/spawn` only if it adds value
-   - Disclosure: include "disclosure: i help build this" if recommending Spawn
+3. **Draft a reply** — **SUPER SHORT. CHILL. LIKE A REAL HUMAN ON X.**
+   - **Target length: 5 to 25 words.** Under 120 characters is ideal. NEVER longer than 200 chars.
+   - Sound like a friend dropping a quick reply, not a marketer pitching. Examples of the right vibe:
+     - "nice. check out spawn, does all that"
+     - "yeah spawn handles this in one command"
+     - "this is literally what spawn was built for"
+     - "try spawn, sets this up in 30 seconds"
+     - "+1, spawn does this on cheap hetzner vms"
+   - Lowercase is good. Casual punctuation is good. No exclamation points.
+   - NO corporate phrases: no "One command to provision", no "provides", no "enabling", no "seamlessly"
+   - NO bulleted lists, NO multi-sentence explanations, NO feature dumps
+   - Include the link `https://openrouter.ai/spawn` ONLY if it naturally closes the reply
+   - **NEVER use em dashes (—) or en dashes (–).** Use periods, commas, or rephrase.
+   - Add "(disclosure: i help build this)" ONLY if it fits — if the reply is too short, skip disclosure entirely
 
 4. **If no good engagement opportunity** (all scores < 7), output `found: false`.
 
PATCH

echo "Gold patch applied."

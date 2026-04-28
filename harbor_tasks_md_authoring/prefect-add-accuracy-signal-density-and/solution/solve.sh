#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "- Don't suggest adding content that's obvious from the code itself. AGENTS.md ca" ".claude/skills/agents-md-sync/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/agents-md-sync/SKILL.md b/.claude/skills/agents-md-sync/SKILL.md
@@ -104,7 +104,30 @@ AGENTS.md files form a hierarchy — when an agent loads any file, all ancestor
 
 **Upward propagation**: When a child AGENTS.md changes (or a new one is created), check whether the parent needs updating — either to add a cross-reference to the new child, or to re-summarize what the child directory does. Parent nodes should summarize their children's responsibilities, not duplicate their details.
 
-For each AGENTS.md in scope, read it fully, then compare its claims against the diff. Look for these categories of staleness:
+For each AGENTS.md in scope, read it fully, then compare its claims against the diff **and** the current source code. Look for these categories of issues:
+
+**Accuracy** — claims in AGENTS.md that don't match the actual code, regardless of whether the diff caused the discrepancy:
+- Described behaviors that don't match what the code actually does (e.g., "renews at 75% of duration" when it actually renews immediately then sleeps 75%)
+- Function signatures or parameters listed that are wrong or incomplete
+- Responsibilities attributed to the wrong layer or module
+- Error handling or failure modes described incorrectly
+
+For claims that are verifiable (specific behaviors, function signatures, which module does what), read the source file and confirm. Don't trust that existing AGENTS.md content was ever correct — it may have been wrong from the start.
+
+**Signal density** — content that duplicates what's discoverable from code rather than surfacing hidden knowledge:
+- Full function signatures that just repeat the code (the *contracts* and *gotchas* around those functions are the high-signal parts)
+- Trivial usage examples that match what's in docstrings or is obvious from the API
+- File-by-file directory listings that `ls` would show — the *layering concept* or *architectural invariant* matters, not the enumeration
+- Content that a developer would learn in 30 seconds of reading the source
+
+AGENTS.md should capture what's *not* visible in the code: invariants, hidden contracts, non-obvious failure modes, things that look one way but behave another.
+
+**Missing invariants** — implicit contracts the code relies on that aren't documented:
+- Parallel implementations that must stay in sync (e.g., sync and async versions of the same module)
+- Ordering requirements or sequencing constraints
+- Singleton behaviors or shared mutable state
+- Cleanup responsibilities and what happens when they're skipped
+- "This looks stateless but actually depends on X"
 
 **Structural drift** — the AGENTS.md describes a directory layout, file list, or module structure that no longer matches reality:
 - Directories or files added/removed/renamed but not reflected in documented trees
@@ -151,14 +174,20 @@ This directory contains 12 modules but has no AGENTS.md. Sibling directories (`s
 
 ### `src/prefect/server/AGENTS.md`
 
-1. **[Structural]** New directory `src/prefect/server/events/` not listed in directory structure
+1. **[Accuracy]** Lease renewal described as "renews at 75% of duration" but code renews immediately then sleeps 75%
+   - Caused by: incorrect from initial creation
+   - Suggested fix: "renews immediately on entry, then sleeps for 75% of `lease_duration` between renewals"
+
+2. **[Signal density]** Full function signatures duplicate the code — remove parameter lists, keep contracts
+   - Suggested fix: Replace `concurrency(names, occupy=1, ...)` with `concurrency()` and describe the non-obvious behaviors instead
+
+3. **[Missing invariant]** Sync and async implementations must stay in lockstep but this isn't documented
+   - Suggested fix: Add "Any behavior change to `_asyncio.py` must be mirrored in `_sync.py`"
+
+4. **[Structural]** New directory `src/prefect/server/events/` not listed in directory structure
    - Caused by: `src/prefect/server/events/` added in this branch
    - Suggested fix: Add `events/` to the directory listing with description
 
-2. **[Command]** Test command references `pytest tests/server/` but new test file uses different path
-   - Caused by: test reorganization in `tests/server/`
-   - Suggested fix: Update command to `pytest tests/server/events/`
-
 ### `./AGENTS.md` (root)
 No changes needed.
 ```
@@ -201,7 +230,9 @@ Should I add this?
 ## Important guidelines
 
 - Be conservative — only flag things that are genuinely wrong or missing. AGENTS.md files are intentionally concise and don't need to document every file.
-- Don't suggest adding content that's obvious from the code itself. AGENTS.md captures non-obvious patterns, gotchas, and high-level structure.
-- Don't suggest stylistic rewrites. Focus on factual accuracy.
+- Don't suggest adding content that's obvious from the code itself. AGENTS.md captures non-obvious patterns, gotchas, and high-level structure. Equally, flag *existing* content that merely restates the code — full function signatures, trivial examples, and file enumerations are low-signal and should be trimmed or replaced with the hidden knowledge around them.
+- Don't trust that existing AGENTS.md content was ever correct. Verify factual claims (behaviors, signatures, responsibility attribution) against the source code, not just against the diff. Content can be wrong from day one.
+- Don't suggest stylistic rewrites. Focus on factual accuracy and signal density.
 - When in doubt about whether something is stale, check the filesystem to confirm rather than guessing from the diff alone.
 - Respect the existing level of detail in each AGENTS.md. If a file only lists top-level directories, don't suggest adding individual files.
+- Look for undocumented invariants — parallel implementations that must stay in sync, ordering constraints, singleton behaviors, cleanup responsibilities. These are the highest-value additions because they're invisible in code and cause the most breakage when violated.
PATCH

echo "Gold patch applied."

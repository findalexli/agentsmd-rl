#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pro-workflow

# Idempotency guard
if grep -qF "**Source:** Adapted from [Andrej Karpathy's observations](https://x.com/karpathy" "rules/pre-flight-discipline.mdc" && grep -qF "Karpathy's [observations on LLM coding pitfalls](https://x.com/karpathy/status/2" "skills/pro-workflow/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/rules/pre-flight-discipline.mdc b/rules/pre-flight-discipline.mdc
@@ -0,0 +1,62 @@
+---
+description: Pre-flight discipline - prevent silent assumptions, scope creep, and drive-by edits before they happen
+alwaysApply: true
+---
+
+Quality gates and self-correction catch mistakes after the fact. These rules prevent the upstream failures.
+
+## 1. Surface, don't assume
+
+- State assumptions explicitly. If uncertain, ask before coding.
+- If the request has multiple interpretations, present them - never pick silently.
+- If a simpler approach exists than what was asked, say so.
+- If something is unclear, stop. Name what's confusing. Ask.
+
+## 2. Minimum viable code
+
+- No features beyond what was asked.
+- No abstractions for single-use code.
+- No "flexibility" or configurability that wasn't requested.
+- No error handling for scenarios that cannot happen.
+- If the diff is 200 lines and 50 would do, rewrite it.
+
+Senior-engineer test: would they call this overcomplicated? If yes, simplify before showing.
+
+## 3. Stay in your lane
+
+Every changed line must trace to the user's request.
+
+- Don't "improve" adjacent code, comments, or formatting.
+- Don't refactor things that aren't broken.
+- Match existing style even if you'd write it differently.
+- Notice unrelated dead code? Mention it. Don't delete it.
+
+When your changes orphan something:
+- Remove imports/symbols that *your* edit made unused.
+- Leave pre-existing dead code alone unless asked.
+
+## 4. Verifiable goals over imperatives
+
+Convert tasks into verification loops:
+
+| Imperative | Verifiable goal |
+|------------|-----------------|
+| "Add validation" | "Write tests for invalid inputs, then make them pass" |
+| "Fix the bug" | "Write a failing test that reproduces it, then make it pass" |
+| "Refactor X" | "Tests pass before and after; behavior unchanged" |
+
+For multi-step work, plan as `step → verify`:
+
+```
+1. [step] → verify: [check]
+2. [step] → verify: [check]
+3. [step] → verify: [check]
+```
+
+Strong success criteria let the loop run independently. "Make it work" requires constant re-clarification.
+
+---
+
+**Tradeoff:** These rules bias toward caution over speed. For trivial fixes (typos, one-liners, obvious renames), use judgment - not every change needs the full rigor.
+
+**Source:** Adapted from [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876) on LLM coding pitfalls, via [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) (MIT).
diff --git a/skills/pro-workflow/SKILL.md b/skills/pro-workflow/SKILL.md
@@ -62,6 +62,32 @@ Should I add this?
 
 ---
 
+## 1b. Pre-Flight Discipline
+
+**Self-correction catches mistakes after the fact. This catches them before.**
+
+Karpathy's [observations on LLM coding pitfalls](https://x.com/karpathy/status/2015883857489522876) name the upstream failures: silent assumptions, overcomplicated diffs, drive-by edits, vague success criteria. Four rules prevent each one.
+
+| Rule | Prevents |
+|------|----------|
+| **Surface, don't assume** | Wrong interpretation, hidden confusion, missing tradeoffs |
+| **Minimum viable code** | 200-line diffs that should be 50, speculative abstractions |
+| **Stay in your lane** | Drive-by refactors, "improvements" to adjacent code |
+| **Verifiable goals** | Endless re-clarification, "make it work" loops |
+
+Full rules in `rules/pre-flight-discipline.mdc` (`alwaysApply: true`). Pairs with self-correction: pre-flight stops the mistake, self-correction captures the lesson when one slips through.
+
+### Add to CLAUDE.md
+
+```markdown
+## Pre-Flight Discipline
+Before coding: state assumptions, present ambiguity, push back if simpler exists.
+Every changed line traces to the request - no drive-by edits.
+Convert imperatives to verifiable goals: "fix bug" → "failing test → make it pass".
+```
+
+---
+
 ## 2. Parallel Sessions with Worktrees
 
 **Zero dead time.** While one Claude thinks, work on something else.
PATCH

echo "Gold patch applied."

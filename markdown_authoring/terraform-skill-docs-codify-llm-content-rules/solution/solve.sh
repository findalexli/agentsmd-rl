#!/usr/bin/env bash
set -euo pipefail

cd /workspace/terraform-skill

# Idempotency guard
if grep -qF "**1. Shape \u2014 decision table before playbook.** The LLM retrieval path is: classi" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -127,6 +127,34 @@ When adding content, ask: **Does this belong in SKILL.md (decision frameworks, k
 - **Version-specific features** clearly marked (e.g., `Terraform 1.6+`)
 - **Token budget:** SKILL.md target <500 lines; current 524 is justified but don't grow further
 
+### LLM Consumption Rules (enforce in every PR review)
+
+These rules tune content for the **primary reader: an LLM retrieving facts to answer a user query**, not a human reading the guide end-to-end. They are **mandatory** for every addition to `SKILL.md` and `references/*.md`. Reviewers must reject PRs that violate them.
+
+**1. Shape — decision table before playbook.** The LLM retrieval path is: classify intent → pick branch → execute. When a topic has multiple viable approaches, open the section with a decision table (`Goal | Use | Tradeoff`) before any phase steps or default procedure. Never bury branching in prose or push alternatives to the end.
+
+**2. Cut human scaffolding.** Before/after config diffs, "Why this matters" paragraphs, and pedagogical asides are human-only signal. If the phase steps already name the required action, a before/after diff is redundant and must be dropped. Teaching tone ≠ retrieval value.
+
+**3. Compress prose → ❌/✅ Rules.** Any sentence starting with "You should...", "Note that...", "Keep in mind...", "It's important to..." — rewrite as terse imperative ❌/✅ bullet. One fact per bullet. Direct verbs only: `Keep`, `Remove`, `Run`, `Confirm`, `Use`, `Avoid`, `Scope`.
+
+**4. Every artifact earns its tokens.** Every code block, table, and example must add a fact not present in the prose. If it only restates, cut it. No "for completeness" content.
+
+**5. Anchor stability.** SKILL.md routes to specific `#anchor` headings in reference files. Rewrites may restructure internal subsections, but must preserve the top-level `### Heading` that the SKILL.md diagnose table points to.
+
+**6. Retrieval-first ordering.** Within a section, order content by what the LLM needs first: (a) decision table, (b) default procedure, (c) alternatives, (d) rules/gotchas as ❌/✅. Rationale lives in ≤1 opening sentence, never a closing "Why this matters" block.
+
+**Token target per reference subsection:** under 400 tokens (~1,600 chars). If larger, split or compress — do not ship a 600-token walkthrough when 350 tokens carries the same decision value.
+
+**Pre-merge checklist for any content PR:**
+
+- [ ] Decision table precedes playbook (if multiple approaches exist)
+- [ ] No before/after diff that merely restates the phase steps
+- [ ] No paragraph starting with "Why this matters" / "Note" / "Keep in mind" — all converted to ❌/✅
+- [ ] Every code block / table adds a fact not in surrounding prose
+- [ ] Subsection under 400 tokens
+- [ ] Anchors referenced from SKILL.md remain stable
+- [ ] For substantive new sections, consult an external LLM expert (e.g. GPT via `mcp__codex__codex`) for format/compression review before merge
+
 ## PR Requirements
 
 PRs must include testing evidence showing baseline behavior (before) vs. compliance behavior (after) for affected scenarios from `tests/baseline-scenarios.md`. See `.github/PULL_REQUEST_TEMPLATE.md` for the full checklist.
PATCH

echo "Gold patch applied."

#!/usr/bin/env bash
set -euo pipefail

cd /workspace/marketingskills

# Idempotency guard
if grep -qF "Use this after completing the Seven Sweeps for an additional quality gate. For h" "skills/copy-editing/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/copy-editing/SKILL.md b/skills/copy-editing/SKILL.md
@@ -2,7 +2,7 @@
 name: copy-editing
 description: "When the user wants to edit, review, or improve existing marketing copy. Also use when the user mentions 'edit this copy,' 'review my copy,' 'copy feedback,' 'proofread,' 'polish this,' 'make this better,' 'copy sweep,' 'tighten this up,' 'this reads awkwardly,' 'clean up this text,' 'too wordy,' or 'sharpen the messaging.' Use this when the user already has copy and wants it improved rather than rewritten from scratch. For writing new copy, see copywriting."
 metadata:
-  version: 1.1.0
+  version: 1.2.0
 ---
 
 # Copy Editing
@@ -256,6 +256,57 @@ For every statement, ask "Okay, so what?" If the copy doesn't answer that questi
 
 ---
 
+## Expert Panel Scoring
+
+Use this after completing the Seven Sweeps for an additional quality gate. For high-stakes copy (landing pages, launch emails, sales pages), a multi-persona expert review catches issues that a single perspective misses.
+
+### How It Works
+
+1. **Assemble 3-5 expert personas** relevant to the copy type
+2. **Each persona scores the copy 1-10** on their area of expertise
+3. **Collect specific critiques** — not just scores, but what to fix
+4. **Revise based on feedback** — address the lowest-scoring areas first
+5. **Re-score after revisions** — iterate until all personas score 7+, with an average of 8+ across the panel
+
+### Recommended Expert Panels
+
+**Landing page copy:**
+- Conversion copywriter (clarity, CTA strength, benefit hierarchy)
+- UX writer (scannability, cognitive load, user flow)
+- Target customer persona (does this speak to me? do I trust it?)
+- Brand strategist (voice consistency, positioning accuracy)
+
+**Email sequence:**
+- Email marketing specialist (subject lines, open/click optimization)
+- Copywriter (hooks, storytelling, persuasion)
+- Spam filter analyst (deliverability red flags, trigger words)
+- Target customer persona (relevance, value, unsubscribe risk)
+
+**Sales page / long-form:**
+- Direct response copywriter (offer structure, objection handling, urgency)
+- Skeptical buyer persona (proof gaps, trust issues, red flags)
+- Editor (flow, readability, conciseness)
+- SEO specialist (keyword coverage, search intent alignment)
+
+### Scoring Rubric
+
+| Score | Meaning |
+|-------|---------|
+| 9-10 | Publish-ready. No meaningful improvements. |
+| 7-8 | Strong. Minor tweaks only. |
+| 5-6 | Functional but has clear gaps. Needs another pass. |
+| 3-4 | Significant issues. Major revision needed. |
+| 1-2 | Fundamentally broken. Rethink approach. |
+
+### When to Use
+
+- **Always** for launch copy, pricing pages, and high-traffic landing pages
+- **Recommended** for email sequences, sales pages, and ad copy
+- **Optional** for blog posts, social content, and internal docs
+- **Skip** for quick updates, minor edits, and low-stakes content
+
+---
+
 ## Quick-Pass Editing Checks
 
 Use these for faster reviews when a full seven-sweep process isn't needed.
PATCH

echo "Gold patch applied."

#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sanity

# Idempotency guard
if grep -qF "**Length test:** if a sentence would tell the reviewer something they could dedu" ".agents/skills/pr-description/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/pr-description/SKILL.md b/.agents/skills/pr-description/SKILL.md
@@ -33,15 +33,29 @@ type(scope): lowercase description
 
 ### 3. Write the PR body
 
-**Be terse.** Don't describe things the reviewer can trivially see from the diff (e.g. "renamed variable X to Y", "added import for Z"). Focus on context and intent that _isn't_ obvious from the code.
+**Lead with why. Only elaborate on the non-obvious.** The reviewer can read the diff — they need the context the diff can't give them. Default to terse; expand only where a reader would genuinely wonder.
+
+Priorities for the Description section:
+
+- **Heavy on _why_** — the motivation, the problem being solved, the constraint or incident that forced this change
+- **Cover _why not_** — alternatives considered and rejected, one sentence each. This is often the most valuable part: it prevents the reviewer from suggesting a path you've already ruled out. Skip if there were no real alternatives worth mentioning
+- **Light on _how_** — only call out approach when it's non-obvious, novel, or a reviewer might reasonably have picked a different path. Skip it for routine changes where the diff speaks for itself
+- **Minimal _what_** — the diff shows what changed. One sentence of orientation at most; don't restate file-by-file changes the reviewer can see
+
+**Length test:** if a sentence would tell the reviewer something they could deduce in 10 seconds from the diff, cut it. A good PR description is often 3–5 sentences total. Bulleted lists of "alternatives considered" should be one line per alternative, not a paragraph.
+
+If you catch yourself writing "this PR renames X to Y" or "adds a new function Z", delete it. If you're explaining _why_ X needed to be renamed or _why_ Z exists (and why the obvious alternative wasn't chosen), keep it — but stay brief.
 
 Use all four sections:
 
 #### Description
 
-- **What** changed — be concrete and specific
-- **Why** — motivation, context, linked issue if any
-- Use bullet points for multiple changes
+Focus on **why** and **why not**, tersely:
+
+- The problem or context the diff doesn't reveal (one short paragraph)
+- Alternatives considered and why rejected (one line each, only if they were real candidates)
+- _How_ only when non-obvious or debatable
+- _What_ reduced to a one-line orientation
 
 #### What to review
 
PATCH

echo "Gold patch applied."

#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-toolkit

# Idempotency guard
if grep -qF "**`user_invocable` default is `false`.** New skills are agent-facing by default:" "skills/skill-creator/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/skill-creator/SKILL.md b/skills/skill-creator/SKILL.md
@@ -30,6 +30,23 @@ allowed-tools:
 
 Create skills and iteratively improve them through measurement.
 
+## Output style directive (applies to every generated skill/agent)
+
+Generated SKILL.md and agent bodies must be written as **dense informational
+text focused on accuracy**. Minimize prose, maximize signal, no filler.
+
+- No motivational framing, no pep talk, no "this will help you...".
+- No repeated restatement of the same constraint in different words.
+- Prefer tables, numbered phases, and bullet lists over paragraphs.
+- Every sentence must carry information the model will act on; cut anything
+  that is only atmosphere.
+- Explanations of "why" stay short and attached to the rule they justify --
+  one clause, not a paragraph.
+
+This is a generation constraint on the outputs of this skill, not a style note
+for this skill's own prose. Enforce it during the "Write the SKILL.md" phase
+and during any agent scaffolding.
+
 The process:
 
 - Decide what the skill should do and how it should work
@@ -109,6 +126,27 @@ skill-name/
 
 **Frontmatter** -- name, description, routing metadata. Description caps: 60 chars max for non-invocable skills, 120 chars for user-invocable. No "Use when:", "Use for:", or "Example:" in the description. The `/do` router has its own routing tables.
 
+**`user_invocable` default is `false`.** New skills are agent-facing by default:
+the `/do` router dispatches them, and the user never types the skill name. Emit
+the frontmatter field explicitly so the default is visible:
+
+```yaml
+user_invocable: false  # default -- router-dispatched, not user-typed
+```
+
+Flipping to `true` requires an explicit justification comment in the
+frontmatter naming the user-facing trigger phrases and why routing through
+`/do` is insufficient. Example:
+
+```yaml
+user_invocable: true  # justification: users type "/pr-workflow" directly as
+                      # a slash-command entry point; /do dispatch is bypassed
+                      # because the user is already scoped to the PR lifecycle.
+```
+
+No justification = leave it `false`. User-invocable expands the system-prompt
+surface and the slash-command namespace; both are scarce.
+
 > See `references/skill-template.md` for the complete frontmatter template with all fields and valid values.
 
 The description is the primary triggering mechanism. Claude tends to undertrigger skills -- be explicit about trigger contexts. Include "Use for" with concrete phrases users would say.
@@ -172,6 +210,48 @@ the skill's workflow.
 | Agent shared across skills | Keep in repo `agents/` directory |
 | Agent needs routing metadata | Keep in repo `agents/` directory |
 
+### Post-scaffold: regenerate skills INDEX.json (mandatory)
+
+After the skill directory + SKILL.md are on disk, regenerate the skills index.
+Without this step the router cannot discover the new skill and requests that
+should match it fall through to the fallback handler.
+
+```bash
+python3 scripts/generate-skill-index.py
+```
+
+Run it from the repo root. Treat it as a commit-gating step: the scaffold is
+not complete until INDEX.json reflects the new skill. Diff the file before
+staging to confirm exactly one new entry was added.
+
+### Post-scaffold: joy-check + do-pair validation
+
+Before declaring the skill shippable, run both checks. They catch different
+failure modes: joy-check catches grievance-mode framing that drags the model
+toward pessimism; do-pair validation catches anti-patterns with no paired
+"Do instead" counterpart.
+
+**Joy-check** (framing). Invoke the `joy-check` skill on the SKILL.md and each
+`references/*.md` file. The accepted deterministic substitute is:
+
+```bash
+python3 scripts/validate-references.py --check-do-framing
+```
+
+This script enforces the positive-pairing rule that joy-check encodes
+structurally: every anti-pattern gets a constructive counterpart. Use it when
+dispatching the full `joy-check` skill is disproportionate (small edits,
+CI contexts, or when only structural pairing matters). For any new skill that
+ships prose-heavy references, prefer the full `joy-check` skill -- tone drift
+is not caught by the pairing script.
+
+**Do-pair validation** (structural). Same command, different failure class.
+Ship the skill only after this exits 0:
+
+```bash
+python3 scripts/validate-references.py --check-do-framing
+```
+
 ---
 
 ## Testing the skill
PATCH

echo "Gold patch applied."

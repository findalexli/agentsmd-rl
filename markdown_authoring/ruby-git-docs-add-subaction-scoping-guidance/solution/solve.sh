#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruby-git

# Idempotency guard
if grep -qF "| **Exclude (wrong sub-action)** | Option belongs to a different sub-action than" ".github/skills/command-implementation/REFERENCE.md" && grep -qF "- [Options excluded because they belong to a different sub-action](#options-excl" ".github/skills/review-arguments-dsl/CHECKLIST.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/command-implementation/REFERENCE.md b/.github/skills/command-implementation/REFERENCE.md
@@ -22,6 +22,7 @@ by subagents during the [Command Implementation](SKILL.md) workflow.
 - [`Base#with_stdin` mechanics](#basewith_stdin-mechanics)
 - [Options completeness — consult the latest-version docs first](#options-completeness--consult-the-latest-version-docs-first)
   - [`requires_git_version` convention](#requires_git_version-convention)
+  - [Scoping options to sub-command classes](#scoping-options-to-sub-command-classes)
   - [Execution-model conflicts](#execution-model-conflicts)
 - [`end_of_options` placement](#end_of_options-placement)
   - [Rule 1 — SYNOPSIS shows `--`: mirror the SYNOPSIS](#rule-1--synopsis-shows----mirror-the-synopsis)
@@ -496,11 +497,12 @@ on an older git installation, git itself will produce its native "unknown option
 error. This is acceptable and expected; the ruby-git library does not gate individual
 options by version.
 
-For each option, make one of two decisions:
+For each option, make one of three decisions:
 
 | Decision | Reason | Action |
 |---|---|---|
 | **Include** | All behavioral options — including output-format flags (`--pretty=`, `--patch`, `--numstat`, `--name-only`, etc.) and filtering/selection flags | Add to `arguments do` |
+| **Exclude (wrong sub-action)** | Option belongs to a different sub-action than the one this class implements | Omit — see [Scoping options to sub-command classes](#scoping-options-to-sub-command-classes) below |
 | **Exclude (execution-model conflict)** | Requires TTY input or otherwise makes the command incompatible with non-interactive subprocess execution | Omit — see [Execution-model conflicts](#execution-model-conflicts) below |
 
 Group related options with a comment in the DSL (e.g. `# Ref inclusion`, `# Date
@@ -557,6 +559,45 @@ This step is required. A command class that only exposes the options that happen
 be used today in `Git::Lib` is incomplete — callers of the future API should not need
 to re-open the docs just because the scaffold only covered current usage.
 
+### Scoping options to sub-command classes
+
+When a git command is split into sub-command classes (e.g., `Branch::Create`,
+`Branch::List`, `Branch::Delete`), each class must include **only** the options that
+apply to the sub-action it implements. Do **not** enumerate every option on the man
+page — most git commands document options for all modes on a single page, and adding
+options that belong to a different mode produces a class that accepts arguments git
+will reject or misinterpret.
+
+**How to determine which options belong to a sub-action:**
+
+1. **Read the SYNOPSIS** — git man pages list separate SYNOPSIS lines per mode
+   (e.g., `git branch [--list]`, `git branch -d`, `git branch -m`). Only options
+   shown on the SYNOPSIS line for the target sub-action are candidates.
+
+2. **Cross-reference the DESCRIPTION and OPTIONS sections** — some options are
+   described generally but only apply to specific modes. Check each option's
+   description for phrases like "only useful with `--list`" or "when used with
+   `-d`". If the docs explicitly tie an option to a different mode, exclude it.
+
+3. **Common/shared options** — options that appear on every SYNOPSIS line or are
+   described as applying to the command as a whole (e.g., `--quiet`, `--verbose`)
+   should be included in every sub-command class where they are meaningful.
+
+**Example — `git branch`:**
+
+| Option | Create | List | Delete | Move/Copy |
+|---|---|---|---|---|
+| `--track` | Yes | — | — | — |
+| `--force` | Yes | — | Yes | Yes |
+| `--sort` | — | Yes | — | — |
+| `--format` | — | Yes | — | — |
+| `--merged` | — | Yes | — | — |
+| `--quiet` | Yes | — | Yes | — |
+| `--color` | — | Yes | — | — |
+
+This rule applies **only** when the command is split into sub-command classes. For
+single-class commands, include all options as described in the decision table above.
+
 ### Execution-model conflicts
 
 Command classes are neutral — they never hardcode policy choices. Policy defaults
diff --git a/.github/skills/review-arguments-dsl/CHECKLIST.md b/.github/skills/review-arguments-dsl/CHECKLIST.md
@@ -1,6 +1,7 @@
 # Arguments DSL Checklist
 
 - [1. Determine scope and exclusions](#1-determine-scope-and-exclusions)
+  - [Options excluded because they belong to a different sub-action](#options-excluded-because-they-belong-to-a-different-sub-action)
   - [Options excluded due to execution-model conflicts](#options-excluded-due-to-execution-model-conflicts)
 - [2. Verify DSL method per option type](#2-verify-dsl-method-per-option-type)
   - [Recognizing `flag_or_value_option` from the git docs](#recognizing-flag_or_value_option-from-the-git-docs)
@@ -32,6 +33,27 @@
 Before auditing individual DSL entries, determine which git options are in scope.
 Reference documents and source files are loaded during the [Input phase](SKILL.md#input).
 
+### Options excluded because they belong to a different sub-action
+
+When a command is split into sub-command classes (e.g., `Branch::Create` vs.
+`Branch::List`), each class includes **only** the options that apply to its
+sub-action. Do **not** add every option from the man page — git documents all modes
+on a single page.
+
+To determine which options belong to a sub-action:
+
+1. **Read the SYNOPSIS** — git man pages list separate SYNOPSIS lines per mode.
+   Only options shown on the SYNOPSIS line for the target sub-action are candidates.
+2. **Cross-reference DESCRIPTION and OPTIONS sections** — check each option's
+   description for phrases like "only useful with `--list`" or "when used with
+   `-d`". If the docs explicitly tie an option to a different mode, exclude it.
+3. **Common/shared options** — options on every SYNOPSIS line or described as
+   applying to the command as a whole (e.g., `--quiet`, `--verbose`) belong in
+   every sub-command class where they are meaningful.
+
+This rule applies **only** to split commands. For single-class commands, include all
+options (subject to execution-model exclusions below).
+
 ### Options excluded due to execution-model conflicts
 
 Include ALL git options in the DSL by default — including output-format flags such as
PATCH

echo "Gold patch applied."

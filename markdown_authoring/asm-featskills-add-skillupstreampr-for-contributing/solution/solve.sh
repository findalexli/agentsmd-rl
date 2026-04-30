#!/usr/bin/env bash
set -euo pipefail

cd /workspace/asm

# Idempotency guard
if grep -qF "You are contributing quality improvements to someone else's open-source skill. T" "skills/skill-upstream-pr/SKILL.md" && grep -qF "> Contribute improvements to an open-source skill on GitHub: evaluate it, lift i" "skills/skill-upstream-pr/docs/README.md" && grep -qF "Hi! \ud83d\udc4b I came across **<skill-name>** while browsing skills and really appreciate" "skills/skill-upstream-pr/references/pr-template.md" && grep -qF "> Hi! \ud83d\udc4b I came across **code-review** while browsing the collection and really l" "skills/skill-upstream-pr/references/tone-guide.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/skill-upstream-pr/SKILL.md b/skills/skill-upstream-pr/SKILL.md
@@ -0,0 +1,232 @@
+---
+name: skill-upstream-pr
+description: "Improve an open-source GitHub skill and open a friendly suggestion PR upstream: fork, run skill-auto-improver, attach asm eval before/after metrics. Don't use for local-only skills, authoring from scratch, bulk repos, or registry publish."
+license: MIT
+compatibility: Claude Code
+allowed-tools: Bash Read Write Edit Grep Glob
+effort: high
+metadata:
+  version: 1.0.0
+  author: luongnv89
+---
+
+# Skill Upstream PR
+
+You are contributing quality improvements to someone else's open-source skill. The workflow is: fork → clone → improve via `skill-auto-improver` → push to fork → open a friendly suggestion PR upstream. You do not own the target repo. Every step assumes you are a polite contributor, not a maintainer.
+
+## Repo Sync Before Edits (mandatory)
+
+Before any modification to the cloned fork, pull the latest from the fork's tracked branch:
+
+```bash
+branch="$(git rev-parse --abbrev-ref HEAD)"
+git fetch origin
+git pull --rebase origin "$branch"
+```
+
+If the working tree is dirty: stash, sync, pop. If `origin` is missing or conflicts occur: stop and ask the user. A stale fork that PRs yesterday's tree is worse than no PR.
+
+## When to Use
+
+- User shares a GitHub URL to a public skill repo and asks to "improve", "level up", or "contribute to" it
+- User says "open a PR to this skill" or "suggest improvements upstream"
+- The target skill scores below 85/8 on `asm eval` and the user wants the upstream author to benefit
+
+Do **not** trigger for: editing a local skill with no upstream, authoring a brand-new skill, publishing to the ASM registry, or bulk-improving many repos in one pass. One skill → one PR.
+
+## Prerequisites
+
+Verify each before cloning anything. Stop and tell the user if any fails.
+
+- `asm` on PATH (`command -v asm`)
+- `gh` on PATH and authenticated (`gh auth status`)
+- `git` on PATH
+- Network access to GitHub
+- Write access to your own GitHub account (for the fork)
+
+## Input
+
+The user provides a GitHub reference to a skill. Accept any of:
+
+- `https://github.com/owner/repo`
+- `https://github.com/owner/repo/tree/<branch>/<path/to/skill>`
+- `github:owner/repo[#ref][:path]`
+
+Normalize to `owner`, `repo`, optional `ref`, optional `path`. If `path` is not given and the repo has multiple `SKILL.md` files, ask the user which one.
+
+## Workflow
+
+Execute phases in order. Do not skip or reorder.
+
+### Phase 0 — Fork and clone
+
+```bash
+cd "$(mktemp -d)"
+gh repo fork "$OWNER/$REPO" --clone --remote
+cd "$REPO"
+# If a ref was provided:
+git checkout "$REF"
+```
+
+`gh repo fork --clone --remote` creates the fork under your account, clones it locally, sets `origin` to your fork and `upstream` to the original repo. Verify with `git remote -v` before continuing.
+
+Create a dedicated branch for the improvement:
+
+```bash
+git checkout -b "skill-upstream-pr/improve-$(date +%Y%m%d-%H%M%S)"
+```
+
+### Phase 1 — Locate the target SKILL.md
+
+If the user gave a `path`, use it. Otherwise:
+
+```bash
+find . -maxdepth 5 -name "SKILL.md" -type f
+```
+
+If more than one match and no `path` was given, list the candidates and ask the user to pick. Never guess — a wrong PR is worse than a delayed one.
+
+Set `SKILL_PATH` to the **directory** containing the chosen SKILL.md (not the file itself) — `asm eval` takes a directory.
+
+### Phase 2 — Delegate to skill-auto-improver
+
+This skill does not reimplement the improvement loop. Follow the workflow in `skills/skill-auto-improver/SKILL.md` with `$SKILL_PATH` as the target:
+
+1. Phase 0 of that skill: capture `.asm-improver/baseline.json`
+2. Phase 1: `asm eval --fix`
+3. Phases 2-4: category-by-category loop with the 85/8 floor
+4. Phase 5: `.asm-improver/report.md`
+
+If the baseline already passes 85/8, stop and tell the user — no PR needed for a skill that already meets the floor. Offer to find a different skill or a different target.
+
+### Phase 3 — Harvest metrics for the PR
+
+Read two files produced by the auto-improver:
+
+- `.asm-improver/baseline.json` — the before snapshot
+- The latest `.asm-improver/iter-N.json` — the after snapshot
+
+Extract for both:
+
+- `overallScore`, `grade`
+- Every `categories[].score` (7 categories)
+- `topSuggestions` summary (for context, not quoted verbatim)
+
+Compute deltas. If the overall score did not improve by at least 3 points **or** no category moved from below 8 to at least 8, stop and tell the user — the change isn't meaningful enough to justify a PR. Offer the auto-improver report as feedback they can share informally instead.
+
+### Phase 4 — Build the PR body
+
+Read `references/pr-template.md` and fill it in. The template enforces friendly, suggestion-style tone. Key sections:
+
+- **What changed** — one-sentence summary
+- **Before/after metrics** — table with overallScore, grade, and all 7 categories
+- **Files touched** — list every modified path under `$SKILL_PATH`
+- **Iterations taken** — N of 8 from the auto-improver loop
+- **How to verify** — the `asm eval` command the maintainer can run locally
+
+Tone rules (read `references/tone-guide.md`):
+
+- Lead with "Hi — noticed X, wanted to share Y"
+- Frame as a suggestion, not a fix: "happy to adjust if the direction doesn't fit"
+- Never imply the maintainer did something wrong
+- Thank them for open-sourcing the skill
+- Close with "no obligation to merge — totally fine to close if this isn't the right direction"
+
+### Phase 5 — Last-mile confirmation (mandatory)
+
+Opening a PR on someone else's repo is public and hard to reverse. Before pushing anything, show the user:
+
+1. The PR title
+2. The full PR body (rendered markdown)
+3. The exact diff (`git diff upstream/<default-branch>`)
+4. The commands you are about to run
+
+Ask the user to confirm. If they want edits, apply them and re-preview. Do not push until the user says "go" or equivalent.
+
+### Phase 6 — Push and open the PR
+
+After approval:
+
+```bash
+# Commit the changes
+git add -A
+git commit -m "$(cat <<'EOF'
+improve SKILL.md: clarify triggers, add acceptance criteria, fix frontmatter
+
+Suggested via skill-upstream-pr. See PR body for before/after metrics.
+EOF
+)"
+
+# Push to the fork
+git push -u origin "$(git rev-parse --abbrev-ref HEAD)"
+
+# Open the PR upstream
+gh pr create \
+  --repo "$OWNER/$REPO" \
+  --title "$PR_TITLE" \
+  --body-file .asm-improver/pr-body.md
+```
+
+Never push to `upstream`. Never use `--no-verify` or other hook-skip flags. If `gh pr create` fails, stop and report — do not retry in a loop.
+
+Print the PR URL returned by `gh pr create` so the user can open it.
+
+## Step Completion Reports (mandatory)
+
+Emit a compact status block after each phase:
+
+```
+◆ Phase N — [phase name] ([N of 6])
+··································································
+  [check 1]:         √ pass
+  [check 2]:         √ pass (note if relevant)
+  [check 3]:         × fail — [reason]
+  Criteria:          √ M/K met
+  ______________________________
+  Result:            PASS | FAIL | PARTIAL
+```
+
+Checks per phase:
+
+- **Phase 0** — `Fork created`, `Clone succeeded`, `Branch created`, `Remotes correct`
+- **Phase 1** — `SKILL.md located`, `Path unambiguous`
+- **Phase 2** — `Baseline captured`, `Auto-improver ran`, `Final score >= 85`, `All categories >= 8`
+- **Phase 3** — `Before/after delta >= 3 points OR category promoted`
+- **Phase 4** — `PR body rendered`, `Tone checks passed`
+- **Phase 5** — `User approved`
+- **Phase 6** — `Push succeeded`, `PR opened`, `URL printed`
+
+## Acceptance Criteria
+
+- Fork + clone done via `gh repo fork --clone --remote` — never a direct clone of upstream
+- Dedicated feature branch created before any edits
+- `skill-auto-improver` workflow run on the target; baseline + final JSON captured under `.asm-improver/`
+- Overall score improved by ≥ 3 points, OR at least one category moved from below 8 to ≥ 8
+- PR body built from `references/pr-template.md` with the full before/after table
+- User explicitly approved the PR preview before push
+- `git push` targets `origin` (the fork), never `upstream`
+- `gh pr create --repo $OWNER/$REPO` used — the PR targets the upstream repo
+- PR URL printed to the user at the end
+
+### Expected output
+
+- A new branch on the user's fork of `$OWNER/$REPO`
+- A public PR on `$OWNER/$REPO` with a before/after metrics table and friendly tone
+- A local `.asm-improver/` directory with baseline, iterations, report, and `pr-body.md`
+
+## Edge Cases
+
+- **Skill already passes 85/8** — stop at Phase 2; do not open a PR for a skill that already meets the floor
+- **Improvement too small** (< 3 point overall delta AND no category promoted) — stop at Phase 3; offer the auto-improver report as informal feedback instead
+- **Multiple SKILL.md files in the repo** — ask the user which one; never batch
+- **Fork already exists from a prior run** — `gh repo fork --clone --remote` reuses it; rebase on upstream's default branch before editing
+- **Upstream force-pushed or rewrote history** — stop and ask the user; do not force-push the fork to "catch up"
+- **`asm eval --fix` writes changes you disagree with** — revert `SKILL.md.bak` and do targeted edits only; don't ship the auto-fix if it harms the skill
+- **Maintainer has a CONTRIBUTING.md or PR template** — read it before Phase 4 and align the PR body with their conventions; their template wins over ours
+
+## References
+
+- `references/pr-template.md` — PR title + body template with before/after table
+- `references/tone-guide.md` — wording patterns for friendly, suggestion-style contributions
+- `skills/skill-auto-improver/SKILL.md` — the improvement loop this skill delegates to
+- `asm eval --help` — flag reference for the evaluator
diff --git a/skills/skill-upstream-pr/docs/README.md b/skills/skill-upstream-pr/docs/README.md
@@ -0,0 +1,61 @@
+<!--
+  DO NOT READ THIS FILE — This README.md is for human catalog browsing only.
+  It ships inside the .skill package but is NEVER auto-loaded into agent context.
+  The runtime loader only reads SKILL.md + references/ + scripts/ + agents/ when the skill triggers.
+  If you're an AI agent, read the SKILL.md file instead for skill instructions.
+-->
+
+# Skill Upstream PR
+
+> Contribute improvements to an open-source skill on GitHub: evaluate it, lift its scores via `skill-auto-improver`, and open a friendly suggestion PR back to the upstream author with a before/after metrics table.
+
+## Highlights
+
+- Forks the target repo via `gh`, never pushes to upstream
+- Delegates the improvement loop to `skill-auto-improver` — no logic duplication
+- Builds a PR body from a template with the full `asm eval` before/after table
+- Enforces a "preview and confirm" step before any public action
+- Friendly, suggestion-style tone — maintainers can close without guilt
+
+## When to Use
+
+| Say this...                                               | Skill will...                                           |
+| --------------------------------------------------------- | ------------------------------------------------------- |
+| "Improve this skill and open a PR: github.com/owner/repo" | Fork, clone, auto-improve, preview PR, push on approval |
+| "Contribute to this upstream skill"                       | Same flow with preview before any push                  |
+| "Suggest improvements to github:owner/repo"               | Runs eval → improves → drafts suggestion PR             |
+
+Don't use for: local skills you own (use `skill-auto-improver` directly), authoring new skills (use `skill-creator`), or publishing to the ASM registry (use `asm publish`).
+
+## How It Works
+
+```mermaid
+graph TD
+    A["Fork & clone via gh"] --> B["Locate target SKILL.md"]
+    B --> C["Run skill-auto-improver loop"]
+    C --> D["Harvest before/after metrics"]
+    D --> E["Build PR body from template"]
+    E --> F["Preview & wait for user OK"]
+    F --> G["Push fork + gh pr create"]
+    style A fill:#4CAF50,color:#fff
+    style G fill:#2196F3,color:#fff
+```
+
+## Usage
+
+```
+/skill-upstream-pr github.com/owner/repo
+```
+
+## Resources
+
+| Path                        | Description                                                    |
+| --------------------------- | -------------------------------------------------------------- |
+| `references/pr-template.md` | PR title + body template with the before/after metrics table   |
+| `references/tone-guide.md`  | Friendly, suggestion-style wording patterns for the PR comment |
+
+## Output
+
+- A dedicated branch on your GitHub fork of the target repo
+- A public pull request on the upstream repo with an `asm eval` before/after metrics table and suggestion-style tone
+- A local `.asm-improver/` directory containing `baseline.json`, per-iteration JSON, `report.md`, and `pr-body.md`
diff --git a/skills/skill-upstream-pr/references/pr-template.md b/skills/skill-upstream-pr/references/pr-template.md
@@ -0,0 +1,76 @@
+# PR Template
+
+Fill in the placeholders below. Write the final body to `.asm-improver/pr-body.md` and pass it to `gh pr create --body-file`.
+
+## Title
+
+```
+Suggest SKILL.md improvements for <skill-name> (+<N> overall, <weakest-category> +<M>)
+```
+
+Keep it under 72 chars. Lead with "Suggest" so the reader immediately sees this is a suggestion PR, not a drive-by rewrite.
+
+## Body
+
+````markdown
+Hi! 👋 I came across **<skill-name>** while browsing skills and really appreciated <one specific thing you liked>. Wanted to share a few suggestions that surfaced when I ran the skill through [`asm eval`](https://github.com/luongnv89/agent-skill-manager) — totally happy to adjust or drop any of this if it doesn't fit your direction.
+
+## What I suggested
+
+<One or two sentences describing the main focus of the changes. E.g. "Tightened the description for better triggering, added an Acceptance Criteria section, and moved the long example list into `references/` to keep the body under the context-efficiency budget.">
+
+## Before / after metrics (`asm eval`)
+
+| Metric              | Before  | After   | Δ           |
+| ------------------- | ------- | ------- | ----------- |
+| **Overall score**   | <X>/100 | <Y>/100 | **+<Y-X>**  |
+| **Grade**           | <old>   | <new>   | <old → new> |
+| Structure           | <a>/10  | <b>/10  | <b-a>       |
+| Description quality | <a>/10  | <b>/10  | <b-a>       |
+| Prompt engineering  | <a>/10  | <b>/10  | <b-a>       |
+| Context efficiency  | <a>/10  | <b>/10  | <b-a>       |
+| Safety              | <a>/10  | <b>/10  | <b-a>       |
+| Testability         | <a>/10  | <b>/10  | <b-a>       |
+| Naming conventions  | <a>/10  | <b>/10  | <b-a>       |
+
+<Note: delete category rows that didn't change, or keep the full table — maintainer's call. Bold the ones that moved.>
+
+## Files touched
+
+- `<path/to/SKILL.md>`
+- `<path/to/references/new-file.md>` (new)
+- `<path/to/other-file>`
+
+## How to verify locally
+
+```bash
+# From the repo root
+asm eval <path-to-skill>          # human-readable score
+asm eval <path-to-skill> --json   # full JSON report
+```
+````
+
+The full iteration log and before/after JSON snapshots are attached as commits on this branch under `.asm-improver/` — feel free to delete them before merging if you don't want them in the repo.
+
+## Why these changes
+
+<One short paragraph per category that moved, in plain language. Avoid quoting the evaluator verbatim — translate the finding into human terms.>
+
+- **<category>** — <human-readable reason, e.g. "The description was missing a 'Don't use for' clause, which helps Claude skip the skill on adjacent queries. Added one naming the nearby domains.">
+
+## Notes
+
+- These are suggestions, not prescriptions — happy to revise based on your preferences, or close this if the direction isn't right for the project.
+- Thanks for open-sourcing <skill-name>! It's a useful skill and hope this is helpful.
+
+_Opened via [skill-upstream-pr](https://github.com/luongnv89/asm/tree/main/skills/skill-upstream-pr). No obligation to merge._
+
+```
+
+## Rendering rules
+
+- Always render the full metrics table, even when only one or two categories changed — maintainers appreciate the complete picture
+- Bold the **Overall score** row; bold any category that moved more than 1 point
+- If `overallScore` dropped on any category, mention it up front in "What I suggested" so the maintainer isn't surprised — honesty beats tidy numbers
+- Strip trailing whitespace and ensure one trailing newline in `pr-body.md` before passing it to `gh`
+```
diff --git a/skills/skill-upstream-pr/references/tone-guide.md b/skills/skill-upstream-pr/references/tone-guide.md
@@ -0,0 +1,58 @@
+# Tone Guide
+
+You are a contributor to someone else's public project. They did not ask you to submit this PR. The tone must reflect that.
+
+## Core principles
+
+1. **Frame as a suggestion, not a correction.** Never imply the author made a mistake.
+2. **Acknowledge the author's work first.** Call out one specific thing you liked before suggesting changes.
+3. **Offer an easy exit.** Make it obvious they can close the PR without explanation and nobody will be upset.
+4. **Be specific.** "Improved prompt engineering" is noise. "Added a negative-trigger clause to skip Vue/Svelte queries" is signal.
+5. **No jargon dumps.** Translate eval-speak into plain English. A maintainer may not know what "context efficiency" means in `asm eval` terms.
+
+## Phrases to use
+
+- "Hi 👋 — noticed X while browsing skills"
+- "Wanted to share a few suggestions"
+- "Happy to adjust if the direction doesn't fit"
+- "Totally fine to close this if it's not the right direction for the project"
+- "Thanks for open-sourcing this"
+- "No obligation to merge"
+- "Really appreciated <specific thing>"
+- "Let me know what you think"
+
+## Phrases to avoid
+
+- "You should" / "You need to"
+- "This is wrong" / "This is broken"
+- "Best practices" (preachy — name the concrete benefit instead)
+- "Required" / "Must" (they don't owe you anything)
+- "I noticed some issues" (frame positively — "a few things that might tighten the triggering")
+- "Before my changes it was bad" (never put the baseline down)
+
+## Example openers
+
+**Good:**
+
+> Hi! 👋 I came across **code-review** while browsing the collection and really liked how the detail-level tiers are structured. Wanted to share a few small suggestions that came up when I ran it through `asm eval` — totally happy to adjust or drop any of these.
+
+**Bad:**
+
+> Your SKILL.md has several issues that need fixing. I've applied the fixes in this PR.
+
+## Handling the score table
+
+The before/after table is the heart of the PR, but it can feel like a report card. Soften it:
+
+- Keep the "Before" numbers in the table — no need to hide them — but never narrate them ("was only 62/100" is rude)
+- In the "Why these changes" section, focus on **what the fix unlocks for users** of the skill, not what was "wrong"
+  - Good: "Added a 'Don't use for' clause — helps Claude skip this skill on Vue/Svelte queries so it triggers more reliably on the React ones you actually want."
+  - Bad: "The description was missing negative triggers, which lowered the description score."
+
+## Closing
+
+End with a short, human line — not a sales pitch. One of:
+
+- "Let me know what you think — happy to iterate."
+- "No obligation to merge; feel free to cherry-pick or rework."
+- "Hope this is useful — thanks again for the skill."
PATCH

echo "Gold patch applied."

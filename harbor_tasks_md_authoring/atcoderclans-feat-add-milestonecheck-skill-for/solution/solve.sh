#!/usr/bin/env bash
set -euo pipefail

cd /workspace/atcoderclans

# Idempotency guard
if grep -qF "- `milestone-check` \u2014 detect users who newly crossed a rating threshold after a " ".claude/rules/architecture.md" && grep -qF "After an AtCoder contest, use `/milestone-check <contest_id>` to detect newly el" ".claude/rules/workflow.md" && grep -qF "AtCoder contest, validate whether they are listed on the site's blog pages, and " ".claude/skills/milestone-check/SKILL.md" && grep -qF "| **Listed, section correct**        | Listed section matches current highest ra" ".claude/skills/milestone-check/instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/rules/architecture.md b/.claude/rules/architecture.md
@@ -31,3 +31,9 @@ and further grouped by language or purpose when counts are large.
 
 Links are validated automatically via GitHub Actions (`.github/` workflows).
 Do not run link checks locally with `curl` or `wget`.
+
+## AI support structure
+
+- `.claude/rules/` — persistent behavioral rules loaded in every session
+- `.claude/skills/` — invocable skills (use `/skill-name` to trigger)
+  - `milestone-check` — detect users who newly crossed a rating threshold after a contest
diff --git a/.claude/rules/workflow.md b/.claude/rules/workflow.md
@@ -26,3 +26,8 @@ Documentation that describes structure is part of the code, not an afterthought.
 Always confirm the purpose of a file with the user before deleting it,
 even if a plan explicitly lists it for deletion.
 The actual role may differ from what the plan assumes.
+
+## Milestone check after contests
+
+After an AtCoder contest, use `/milestone-check <contest_id>` to detect newly eligible
+blog candidates. See `.claude/skills/milestone-check/` for details.
diff --git a/.claude/skills/milestone-check/SKILL.md b/.claude/skills/milestone-check/SKILL.md
@@ -0,0 +1,24 @@
+---
+name: milestone-check
+description: >
+  Detect users who newly crossed a rating threshold (2000/2400/2800/3200) in a given
+  AtCoder contest, validate whether they are listed on the site's blog pages, and report
+  candidates for addition. Does not modify any files.
+---
+
+## Overview
+
+Validate an AtCoder contest for users who newly reached a rating milestone, and report
+blog listing candidates. Both Algorithm and Heuristic divisions are covered.
+
+## Input
+
+```
+/milestone-check <contest_id>
+```
+
+Examples: `/milestone-check abc399`, `/milestone-check ahc040`
+
+## Process
+
+Read `.claude/skills/milestone-check/instructions.md` and follow Steps 1–5 in order.
diff --git a/.claude/skills/milestone-check/instructions.md b/.claude/skills/milestone-check/instructions.md
@@ -0,0 +1,84 @@
+# milestone-check: Detailed Instructions
+
+## Step 1: Identify threshold crossers
+
+Fetch: `https://atcoder.jp/contests/{contest_id}/results`
+
+Extract users who satisfy any of the following. Fetch all result pages if paginated.
+
+| Threshold | Color  | Condition                                    |
+|-----------|--------|----------------------------------------------|
+| 2000      | Yellow | `new_rating >= 2000` and `old_rating < 2000` |
+| 2400      | Orange | `new_rating >= 2400` and `old_rating < 2400` |
+| 2800      | Red    | `new_rating >= 2800` and `old_rating < 2800` |
+| 3200      | Crown  | `new_rating >= 3200` and `old_rating < 3200` |
+
+- Skip rows where rating is hidden (`----`).
+- A user who crosses multiple thresholds in one contest (e.g. 1999→2402) counts only for
+  the highest threshold crossed (Orange in this example).
+
+---
+
+## Step 2: Check existing blog listings
+
+Search all of the following files for each username from Step 1:
+
+- `docs/blogs/algorithm/*.md` (C, C++, C#, Crystal, Java, Nim, Python, Ruby, Rust)
+- `docs/blogs/heuristic/*.md` (C, C++, C#, Crystal, D, Go, Java, Nim, Python, Rust)
+
+Classify each user as one of:
+
+| Status                             | Description                                                    |
+|------------------------------------|----------------------------------------------------------------|
+| **Unlisted**                       | Not found in any file → proceed to Step 4                      |
+| **Listed, section correct**        | Listed section matches current highest rating → no change needed |
+| **Listed, section upgrade needed** | Newly crossed a higher threshold → section move required       |
+
+---
+
+## Step 3: Detect primary language
+
+Fetch: `https://atcoder.jp/contests/{contest_id}/submissions?f.User={username}`
+
+- Use the most frequently submitted language in this contest as the primary language.
+- Tie-break: prefer the language used for the hardest problem solved
+  (latest letter in the alphabet, e.g. F > D).
+- If zero submissions (e.g. virtual participation): fetch `https://atcoder.jp/users/{username}`
+  and check the last 10 contest entries to determine language.
+
+---
+
+## Step 4: Blog search (unlisted users only)
+
+Check in order; record all found URLs — do not stop at the first match.
+
+1. Profile page `https://atcoder.jp/users/{username}` — look for any listed blog URL
+2. `https://qiita.com/{username}` — HTTP 404 means not present
+3. `https://zenn.dev/{username}` — HTTP 404 means not present
+4. `https://note.com/{username}` — HTTP 404 means not present
+5. Web search: `"{username}" AtCoder はてなブログ`
+
+---
+
+## Step 5: Report
+
+Output in the following structure:
+
+```markdown
+## Results: {contest_id}
+
+### Unlisted
+
+| Username | Threshold     | Primary Language | Blog URL    |
+|----------|---------------|------------------|-------------|
+| foo      | Yellow (2000) | C++              | https://... |
+| baz      | Yellow (2000) | Rust             | Not found   |
+
+### Listed (section upgrade needed)
+
+- bar
+- qux
+```
+
+Include all detected users. For Unlisted, include every candidate even if no blog was found.
+For Listed, names only — details are already in the site.
PATCH

echo "Gold patch applied."

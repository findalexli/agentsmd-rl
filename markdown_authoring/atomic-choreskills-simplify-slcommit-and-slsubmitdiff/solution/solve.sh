#!/usr/bin/env bash
set -euo pipefail

cd /workspace/atomic

# Idempotency guard
if grep -qF "- `sl diff` - View pending changes" ".claude/skills/sl-commit/SKILL.md" && grep -qF "2. Submit commits to Phabricator using `jf submit --draft`. Submit for review us" ".claude/skills/sl-submit-diff/SKILL.md" && grep -qF "- `sl diff` - View pending changes" ".github/skills/sl-commit/SKILL.md" && grep -qF "2. Submit commits to Phabricator using `jf submit --draft`. Submit for review us" ".github/skills/sl-submit-diff/SKILL.md" && grep -qF "- `sl diff` - View pending changes" ".opencode/skills/sl-commit/SKILL.md" && grep -qF "2. Submit commits to Phabricator using `jf submit --draft`. Submit for review us" ".opencode/skills/sl-submit-diff/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/sl-commit/SKILL.md b/.claude/skills/sl-commit/SKILL.md
@@ -24,18 +24,14 @@ Create well-formatted commits following the Conventional Commits specification u
 ## Commands to Use
 
 - `sl status` - Check repository state
-- `sl bookmark` - Get current bookmark
-- `sl smartlog -l 5` - View recent commits with graphical history
-- `sl diff --stat` - View pending changes
+- `sl diff` - View pending changes
 - `sl add <files>` - Add untracked files
 - `sl commit -m "<message>"` - Create commit
 
 ## Key Sapling Differences from Git
 
 - **No staging area**: Sapling commits all pending changes directly
 - **Amend with auto-restack**: `sl amend` automatically rebases descendant commits
-- **Smartlog**: Use `sl smartlog` or `sl ssl` for graphical commit history
-- **Absorb**: Use `sl absorb` to intelligently integrate pending changes
 - **Stacked Diffs**: Each commit becomes a separate Phabricator diff
 
 ## Sapling Commit Commands Reference
@@ -46,28 +42,6 @@ Create well-formatted commits following the Conventional Commits specification u
 | `sl commit -A`           | Add untracked files and commit                  |
 | `sl amend`               | Amend current commit (auto-rebases descendants) |
 | `sl amend --to COMMIT`   | Amend changes to a specific commit in stack     |
-| `sl absorb`              | Intelligently absorb changes into stack commits |
-
-## Conventional Commits Format
-
-```
-<type>[optional scope]: <description>
-
-[optional body]
-
-[optional footer(s)]
-```
-
-**Types:**
-
-- `feat:` - New feature (MINOR version bump)
-- `fix:` - Bug fix (PATCH version bump)
-- `docs:` - Documentation changes
-- `style:` - Code style changes
-- `refactor:` - Code refactoring
-- `perf:` - Performance improvements
-- `test:` - Adding or updating tests
-- `chore:` - Maintenance tasks
 
 ## Important Notes
 
diff --git a/.claude/skills/sl-submit-diff/SKILL.md b/.claude/skills/sl-submit-diff/SKILL.md
@@ -5,7 +5,7 @@ description: Submit commits as Phabricator diffs for code review using Sapling.
 
 # Submit Diff (Sapling + Phabricator)
 
-Submit commits to Phabricator for code review using `jf submit` (Meta) or `arc diff` (open-source).
+Submit commits to Phabricator for code review using `jf submit` (Meta).
 
 <EXTREMELY_IMPORTANT>
 
@@ -15,26 +15,22 @@ Submit commits to Phabricator for code review using `jf submit` (Meta) or `arc d
 ## What This Skill Does
 
 1. If there are uncommitted changes, first run `/commit` to create a commit
-2. Submit commits to Phabricator using `jf submit` (or `arc diff`)
+2. Submit commits to Phabricator using `jf submit --draft`. Submit for review using DRAFT mode
 3. Each commit in the stack becomes a separate Phabricator diff (D12345)
 4. Commit messages are updated with `Differential Revision:` link
 
 ## Commands to Use
 
 - `sl status` - Check for uncommitted changes
-- `sl ssl` - View commits with diff status
-- `jf submit` - Submit commits to Phabricator
+- `jf submit --draft` - Submit commits to Phabricator in DRAFT mode
 - `sl diff --since-last-submit` - View changes since last submission
 
 ## Common Operations
 
 | Task                    | Command                           |
 | ----------------------- | --------------------------------- |
-| Submit current commit   | `jf submit`                       |
-| Update diff after amend | `sl amend && jf submit`           |
-| View diff status        | `sl ssl`                          |
-| Check sync status       | `sl log -T '{syncstatus}\n' -r .` |
-| Get diff ID             | `sl log -T '{phabdiff}\n' -r .`   |
+| Submit current commit   | `jf submit --draft`               |
+| Update diff after amend | `sl amend && jf submit --draft`   |
 
 ## Diff Status Values
 
@@ -52,12 +48,6 @@ Sapling naturally supports stacked commits. When submitting:
 - Diffs are linked with proper dependency relationships
 - Reviewers can review each diff independently
 
-## Prerequisites
-
-1. **`.arcconfig`** must exist in repository root with Phabricator URL
-2. **`~/.arcrc`** must contain authentication credentials
-3. **`fbcodereview`** extension must be enabled in Sapling config
-
 ## Important Notes
 
 - Unlike GitHub PRs, Phabricator diffs are tied to commits via `Differential Revision:`
diff --git a/.github/skills/sl-commit/SKILL.md b/.github/skills/sl-commit/SKILL.md
@@ -24,18 +24,14 @@ Create well-formatted commits following the Conventional Commits specification u
 ## Commands to Use
 
 - `sl status` - Check repository state
-- `sl bookmark` - Get current bookmark
-- `sl smartlog -l 5` - View recent commits with graphical history
-- `sl diff --stat` - View pending changes
+- `sl diff` - View pending changes
 - `sl add <files>` - Add untracked files
 - `sl commit -m "<message>"` - Create commit
 
 ## Key Sapling Differences from Git
 
 - **No staging area**: Sapling commits all pending changes directly
 - **Amend with auto-restack**: `sl amend` automatically rebases descendant commits
-- **Smartlog**: Use `sl smartlog` or `sl ssl` for graphical commit history
-- **Absorb**: Use `sl absorb` to intelligently integrate pending changes
 - **Stacked Diffs**: Each commit becomes a separate Phabricator diff
 
 ## Sapling Commit Commands Reference
@@ -46,28 +42,6 @@ Create well-formatted commits following the Conventional Commits specification u
 | `sl commit -A`           | Add untracked files and commit                  |
 | `sl amend`               | Amend current commit (auto-rebases descendants) |
 | `sl amend --to COMMIT`   | Amend changes to a specific commit in stack     |
-| `sl absorb`              | Intelligently absorb changes into stack commits |
-
-## Conventional Commits Format
-
-```
-<type>[optional scope]: <description>
-
-[optional body]
-
-[optional footer(s)]
-```
-
-**Types:**
-
-- `feat:` - New feature (MINOR version bump)
-- `fix:` - Bug fix (PATCH version bump)
-- `docs:` - Documentation changes
-- `style:` - Code style changes
-- `refactor:` - Code refactoring
-- `perf:` - Performance improvements
-- `test:` - Adding or updating tests
-- `chore:` - Maintenance tasks
 
 ## Important Notes
 
diff --git a/.github/skills/sl-submit-diff/SKILL.md b/.github/skills/sl-submit-diff/SKILL.md
@@ -5,7 +5,7 @@ description: Submit commits as Phabricator diffs for code review using Sapling.
 
 # Submit Diff (Sapling + Phabricator)
 
-Submit commits to Phabricator for code review using `jf submit` (Meta) or `arc diff` (open-source).
+Submit commits to Phabricator for code review using `jf submit` (Meta).
 
 <EXTREMELY_IMPORTANT>
 
@@ -15,26 +15,22 @@ Submit commits to Phabricator for code review using `jf submit` (Meta) or `arc d
 ## What This Skill Does
 
 1. If there are uncommitted changes, first run `/commit` to create a commit
-2. Submit commits to Phabricator using `jf submit` (or `arc diff`)
+2. Submit commits to Phabricator using `jf submit --draft`. Submit for review using DRAFT mode
 3. Each commit in the stack becomes a separate Phabricator diff (D12345)
 4. Commit messages are updated with `Differential Revision:` link
 
 ## Commands to Use
 
 - `sl status` - Check for uncommitted changes
-- `sl ssl` - View commits with diff status
-- `jf submit` - Submit commits to Phabricator
+- `jf submit --draft` - Submit commits to Phabricator in DRAFT mode
 - `sl diff --since-last-submit` - View changes since last submission
 
 ## Common Operations
 
 | Task                    | Command                           |
 | ----------------------- | --------------------------------- |
-| Submit current commit   | `jf submit`                       |
-| Update diff after amend | `sl amend && jf submit`           |
-| View diff status        | `sl ssl`                          |
-| Check sync status       | `sl log -T '{syncstatus}\n' -r .` |
-| Get diff ID             | `sl log -T '{phabdiff}\n' -r .`   |
+| Submit current commit   | `jf submit --draft`               |
+| Update diff after amend | `sl amend && jf submit --draft`   |
 
 ## Diff Status Values
 
@@ -52,12 +48,6 @@ Sapling naturally supports stacked commits. When submitting:
 - Diffs are linked with proper dependency relationships
 - Reviewers can review each diff independently
 
-## Prerequisites
-
-1. **`.arcconfig`** must exist in repository root with Phabricator URL
-2. **`~/.arcrc`** must contain authentication credentials
-3. **`fbcodereview`** extension must be enabled in Sapling config
-
 ## Important Notes
 
 - Unlike GitHub PRs, Phabricator diffs are tied to commits via `Differential Revision:`
diff --git a/.opencode/skills/sl-commit/SKILL.md b/.opencode/skills/sl-commit/SKILL.md
@@ -24,18 +24,14 @@ Create well-formatted commits following the Conventional Commits specification u
 ## Commands to Use
 
 - `sl status` - Check repository state
-- `sl bookmark` - Get current bookmark
-- `sl smartlog -l 5` - View recent commits with graphical history
-- `sl diff --stat` - View pending changes
+- `sl diff` - View pending changes
 - `sl add <files>` - Add untracked files
 - `sl commit -m "<message>"` - Create commit
 
 ## Key Sapling Differences from Git
 
 - **No staging area**: Sapling commits all pending changes directly
 - **Amend with auto-restack**: `sl amend` automatically rebases descendant commits
-- **Smartlog**: Use `sl smartlog` or `sl ssl` for graphical commit history
-- **Absorb**: Use `sl absorb` to intelligently integrate pending changes
 - **Stacked Diffs**: Each commit becomes a separate Phabricator diff
 
 ## Sapling Commit Commands Reference
@@ -46,28 +42,6 @@ Create well-formatted commits following the Conventional Commits specification u
 | `sl commit -A`           | Add untracked files and commit                  |
 | `sl amend`               | Amend current commit (auto-rebases descendants) |
 | `sl amend --to COMMIT`   | Amend changes to a specific commit in stack     |
-| `sl absorb`              | Intelligently absorb changes into stack commits |
-
-## Conventional Commits Format
-
-```
-<type>[optional scope]: <description>
-
-[optional body]
-
-[optional footer(s)]
-```
-
-**Types:**
-
-- `feat:` - New feature (MINOR version bump)
-- `fix:` - Bug fix (PATCH version bump)
-- `docs:` - Documentation changes
-- `style:` - Code style changes
-- `refactor:` - Code refactoring
-- `perf:` - Performance improvements
-- `test:` - Adding or updating tests
-- `chore:` - Maintenance tasks
 
 ## Important Notes
 
diff --git a/.opencode/skills/sl-submit-diff/SKILL.md b/.opencode/skills/sl-submit-diff/SKILL.md
@@ -5,7 +5,7 @@ description: Submit commits as Phabricator diffs for code review using Sapling.
 
 # Submit Diff (Sapling + Phabricator)
 
-Submit commits to Phabricator for code review using `jf submit` (Meta) or `arc diff` (open-source).
+Submit commits to Phabricator for code review using `jf submit` (Meta).
 
 <EXTREMELY_IMPORTANT>
 
@@ -15,26 +15,22 @@ Submit commits to Phabricator for code review using `jf submit` (Meta) or `arc d
 ## What This Skill Does
 
 1. If there are uncommitted changes, first run `/commit` to create a commit
-2. Submit commits to Phabricator using `jf submit` (or `arc diff`)
+2. Submit commits to Phabricator using `jf submit --draft`. Submit for review using DRAFT mode
 3. Each commit in the stack becomes a separate Phabricator diff (D12345)
 4. Commit messages are updated with `Differential Revision:` link
 
 ## Commands to Use
 
 - `sl status` - Check for uncommitted changes
-- `sl ssl` - View commits with diff status
-- `jf submit` - Submit commits to Phabricator
+- `jf submit --draft` - Submit commits to Phabricator in DRAFT mode
 - `sl diff --since-last-submit` - View changes since last submission
 
 ## Common Operations
 
 | Task                    | Command                           |
 | ----------------------- | --------------------------------- |
-| Submit current commit   | `jf submit`                       |
-| Update diff after amend | `sl amend && jf submit`           |
-| View diff status        | `sl ssl`                          |
-| Check sync status       | `sl log -T '{syncstatus}\n' -r .` |
-| Get diff ID             | `sl log -T '{phabdiff}\n' -r .`   |
+| Submit current commit   | `jf submit --draft`               |
+| Update diff after amend | `sl amend && jf submit --draft`   |
 
 ## Diff Status Values
 
@@ -52,12 +48,6 @@ Sapling naturally supports stacked commits. When submitting:
 - Diffs are linked with proper dependency relationships
 - Reviewers can review each diff independently
 
-## Prerequisites
-
-1. **`.arcconfig`** must exist in repository root with Phabricator URL
-2. **`~/.arcrc`** must contain authentication credentials
-3. **`fbcodereview`** extension must be enabled in Sapling config
-
 ## Important Notes
 
 - Unlike GitHub PRs, Phabricator diffs are tied to commits via `Differential Revision:`
PATCH

echo "Gold patch applied."

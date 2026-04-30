#!/usr/bin/env bash
set -euo pipefail

cd /workspace/redpanda

# Idempotency guard
if grep -qF "**Optional: machine-readable report.** If the `SKILL_REPORT_FILE` env var is set" ".claude/skills/create-backport-branch/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/create-backport-branch/SKILL.md b/.claude/skills/create-backport-branch/SKILL.md
@@ -37,9 +37,11 @@ git checkout -b $backport_branch_name $target_branch
 Get the list of commit SHAs from the PR:
 
 ```bash
-gh api "repos/redpanda-data/redpanda/pulls/$pr_number/commits" --paginate --jq '[.[].sha[0:10]]|join(" ")'
+gh api "repos/{owner}/{repo}/pulls/$pr_number/commits" --paginate --jq '[.[].sha[0:10]]|join(" ")'
 ```
 
+`gh` resolves the `{owner}` and `{repo}` placeholders from the git remote of the current directory (see [`gh api` docs](https://cli.github.com/manual/gh_api)). Run this from a checkout of the repo that owns the PR.
+
 Save the full list of commits as `git_commits` and report how many commits were found.
 
 ### 4. Cherry-pick commits
@@ -126,27 +128,37 @@ A cherry-pick can also be empty without any conflict — git will report "The pr
 
 ### 6. Final report
 
-After all commits are cherry-picked successfully, report:
+After all commits are cherry-picked successfully, resolve the source-PR URL dynamically:
+
+```bash
+pr_url=$(gh pr view $pr_number --json url --jq .url)
+```
+
+Then emit this report to stdout:
 
 ```
-Backport of PR https://github.com/redpanda-data/redpanda/pull/${pr_number}
+Backport of PR ${pr_url}
 
 - Command: git cherry-pick -x ${git_commits}
 - Commits backported: ${total_commits}
 - Conflicts resolved: ${conflicts_resolved}
 - Commits skipped (already on target): ${commits_skipped}
 - Backport branch: ${backport_branch_name}
 
-Conflict details:
+## Conflict details
+
 - ${commit_sha} (${file}): one-line explanation of what conflicted and how it was resolved
 ```
 
 For each conflict resolved, include a one-line explanation covering what conflicted and how you resolved it. This helps PR reviewers understand the backport without reading every diff.
 
-If `generated_files_touched` is non-empty, append a warning section:
+If `generated_files_touched` is non-empty, append this warning section:
 
 ```
-⚠️  Generated files were cherry-picked and may need regeneration:
+## ⚠️ Generated files
+
+The following files were cherry-picked and may need regeneration:
+
 - ${file_1}
 - ${file_2}
 
@@ -157,6 +169,8 @@ regenerate them on the target branch to ensure they're correct. For example:
 - go.sum: run `go mod tidy`
 ```
 
+**Optional: machine-readable report.** If the `SKILL_REPORT_FILE` env var is set (callers like GitHub Actions workflows use this), write the exact same report text to that file path. The file content is designed to be usable verbatim as the body of the backport PR. Humans invoking the skill directly do not set this variable and simply read the report on stdout.
+
 ## Rules
 
 - NEVER guess at conflict resolutions. If uncertain, abort immediately using the abort procedure.
PATCH

echo "Gold patch applied."

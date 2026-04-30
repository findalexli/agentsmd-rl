#!/usr/bin/env bash
set -euo pipefail

cd /workspace/grafana

# Idempotency guard
if grep -qF "When working on issues, PRs, or needing repository context, use the GitHub CLI (" "public/app/features/alerting/unified/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/public/app/features/alerting/unified/CLAUDE.md b/public/app/features/alerting/unified/CLAUDE.md
@@ -417,6 +417,60 @@ Check https://testing-library.com/docs/queries/about/ for what selectors to pref
 - [ ] Async operations use `await` and `findBy*`
 - [ ] Permissions tested with `grantUserPermissions`
 
+## Using GitHub CLI for Context
+
+When working on issues, PRs, or needing repository context, use the GitHub CLI (`gh`) to fetch information directly:
+
+### Common Commands
+
+```bash
+# View issue details
+gh issue view <issue-number>
+
+# View PR details and diff
+gh pr view <pr-number>
+gh pr diff <pr-number>
+
+# List recent issues
+gh issue list --limit 10
+
+# List PRs with specific labels
+gh pr list --label "alerting"
+
+# Search issues
+gh issue list --search "keyword"
+
+# View PR reviews and comments
+gh pr view <pr-number> --comments
+
+# Check CI status
+gh pr checks <pr-number>
+
+# View repository info
+gh repo view
+```
+
+### When to Use
+
+- **Understanding issue context**: Fetch issue descriptions, comments, and linked PRs
+- **Reviewing PR changes**: Get diffs, review comments, and CI status
+- **Finding related work**: Search for similar issues or existing implementations
+- **Checking project status**: List open issues/PRs for the alerting team
+
+### Example Workflow
+
+```bash
+# Working on issue #12345
+gh issue view 12345
+
+# Check if there's an existing PR
+gh pr list --search "fixes #12345"
+
+# Review a related PR
+gh pr view 67890
+gh pr diff 67890
+```
+
 ## Getting Help
 
 - Check patterns in existing `components/` code
@@ -425,6 +479,7 @@ Check https://testing-library.com/docs/queries/about/ for what selectors to pref
 - See `mocks.ts` for data factories
 - Read [./TESTING.md](./TESTING.md) for testing details
 - Review Grafana style guides (linked at top)
+- Use `gh` CLI to fetch issue/PR context from GitHub
 
 ---
 
PATCH

echo "Gold patch applied."

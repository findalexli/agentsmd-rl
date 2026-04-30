#!/usr/bin/env bash
set -euo pipefail

cd /workspace/causalpy

# Idempotency guard
if grep -qF "2. **User review**: Always present the draft issue to the user for review before" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -59,3 +59,55 @@
     - `ignore-missing-imports`: Enabled to allow for gradual adoption of type hints without requiring all third-party libraries to have stubs.
     - `additional_dependencies`: Includes `numpy` and `pandas-stubs` to provide type information for these libraries.
 - **Execution**: Run automatically via `pre-commit run --all-files` or on commit.
+
+## GitHub Issue Creation
+
+When you or the user identify an issue (bug, enhancement, or task), you can automatically create a GitHub issue using the GitHub CLI.
+
+### Prerequisites
+
+- **Install GitHub CLI**: If `gh` is not available, install it:
+  - macOS: `brew install gh`
+  - Linux: See https://github.com/cli/cli/blob/trunk/docs/install_linux.md
+  - Windows: `winget install --id GitHub.cli`
+- **Authenticate**: Run `gh auth login` and follow the prompts to authorize access to the repository.
+
+### Creating an Issue
+
+1. **Generate the issue body**: Create a markdown file (e.g., `issue.md`) describing the issue with:
+   - A clear problem statement or feature request
+   - Steps to reproduce (for bugs)
+   - Expected vs actual behavior (for bugs)
+   - Relevant code snippets or error messages
+   - Proposed solution (if applicable)
+
+2. **User review**: Always present the draft issue to the user for review before filing. The user should have the opportunity to view, modify, or approve the issue content before it is submitted.
+
+3. **Create the issue**: After the user approves, run the following command:
+   ```bash
+   gh issue create --title "<descriptive title>" --body-file issue.md
+   ```
+
+   **Adding labels**: Use the `--label` flag to categorize the issue appropriately:
+   ```bash
+   gh issue create --title "<descriptive title>" --body-file issue.md --label "<label>"
+   ```
+
+   Common labels include:
+   - `bug` - Something isn't working correctly
+   - `enhancement` - New feature or improvement request
+   - `documentation` - Documentation improvements or additions
+   - `question` - Further information is requested
+
+   Multiple labels can be added by repeating the flag: `--label "bug" --label "high priority"`
+
+   **Discovering available labels**: To see what labels are available in the repository:
+   ```bash
+   # List all labels defined in the repo, along with their descriptions
+   gh label list --limit 100
+
+   # Find unique labels from existing issues
+   gh issue list --state all --limit 100 --json labels --jq '.[].labels[].name' | sort -u
+   ```
+
+4. **Clean up**: Delete the temporary `issue.md` file after the issue is created.
PATCH

echo "Gold patch applied."

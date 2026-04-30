#!/usr/bin/env bash
set -euo pipefail

cd /workspace/github-misc-scripts

# Idempotency guard
if grep -qF "- Include the header `-H \"X-Github-Next-Global-ID: 1\"` in GraphQL queries to ret" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -2,15 +2,19 @@
 
 ## scripts in the `gh-cli` and `scripts` directories
 
-When creating or modifying scripts in the `gh-cli` directory, ensure:
+When creating or modifying scripts in the `gh-cli` and `scripts` directories:
 
-- The script has input parameters
-- The script has a basic description and usage examples at the top
-- We make sure to paginate (`--paginate`) when retrieving results
+- Ensure the script has input parameters
+- Include input validation and meaningful error messages
+- Ensure the script has a basic description and usage examples at the top
+- Make sure to paginate (`--paginate` and/or `octokit.paginate`) when retrieving results
 - Note any special permissions/token requirements
 - If modifying input parameters to a script, make sure to update the respective `README.md` in the script directory (if applicable)
 - Use only `2` spaces for indentation - not `4`
 - Do not leave any trailing whitespace at the end of lines
+- With `gh api` commands, prefer `--jq` versus piping to `jq` when possible
+- Include the header `-H "X-Github-Next-Global-ID: 1"` in GraphQL queries to retrieve the new global ID format - see the [GitHub migration guide for global node IDs](https://docs.github.com/en/graphql/guides/migrating-graphql-global-node-ids) for details
+- Complex scripts in the `./scripts` directory should have its own folder (so a `package.json` can be included for example)
 
 ## README.md documentation
 
@@ -23,8 +27,10 @@ When adding new scripts to any directory:
 - Use proper kebab-case naming convention for script files
 - Avoid short words like "repo" (use "repository"), "org" (use "organization")
 - Test that the entry passes `lint-readme.js` validation
+- Don't be too verbose - keep descriptions and usage instructions concise and to the point
+- Don't use periods after bullet points for consistency
 
-## Script naming and structure
+## script naming and structure
 
 - Use kebab-case for all script filenames (e.g., `get-organization-repositories.sh`)
 - Include appropriate file extensions (.sh, .ps1, .js, .py)
@@ -39,3 +45,27 @@ When adding new scripts to any directory:
 - Document required scopes and permissions in script comments
 - Use environment variables or parameters for sensitive data (never hardcode tokens)
 - For scripts requiring special permissions, mention this in both script comments and README
+- Add hostname support for GitHub Enterprise instances / ghe.com when applicable
+
+## commit messages
+
+Prefer the Conventional Commits specification:
+
+- Format: `<type>(<scope>): <description>`
+- Types:
+  - `feat`: New feature
+  - `fix`: Bug fix
+  - `refactor`: Code change that neither fixes a bug nor adds a feature
+  - `docs`: Documentation only changes
+  - `chore`: Changes to build process or auxiliary tools
+  - `ci`: Changes to CI configuration files and scripts
+  - `style`: Code style changes (formatting, missing semicolons, etc.)
+  - `test`: Adding or updating tests
+- Scopes (optional):
+  - `scripts`: Changes in the scripts directory
+  - `gh-cli`: Changes in the gh-cli directory
+  - `ci`: Changes to CI/linting tools
+- Description: Short, imperative tense summary (e.g., "add feature" not "added feature")
+- Body (optional): Provide additional context with bullet points
+- Keep it concise but descriptive
+- Append `!` to the type if it's a breaking change (e.g., `feat!: add additional required input parameters`)
PATCH

echo "Gold patch applied."

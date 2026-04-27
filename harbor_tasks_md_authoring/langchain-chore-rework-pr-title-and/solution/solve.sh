#!/usr/bin/env bash
set -euo pipefail

cd /workspace/langchain

# Idempotency guard
if grep -qF "- Start the text after `type(scope):` with a lowercase letter, unless the first " "AGENTS.md" && grep -qF "- Start the text after `type(scope):` with a lowercase letter, unless the first " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -79,23 +79,48 @@ uv run --group lint mypy .
 - uv.lock: Locked dependencies for reproducible builds
 - Makefile: Development tasks
 
-#### Commit standards
+#### PR and commit titles
 
-Suggest PR titles that follow Conventional Commits format. Refer to .github/workflows/pr_lint for allowed types and scopes. Note that all commit/PR titles should be in lowercase with the exception of proper nouns/named entities. All PR titles should include a scope with no exceptions. For example:
+Follow Conventional Commits. See `.github/workflows/pr_lint.yml` for allowed types and scopes. All titles must include a scope with no exceptions — even for the main `langchain` package.
+
+- Start the text after `type(scope):` with a lowercase letter, unless the first word is a proper noun (e.g. `Azure`, `GitHub`, `OpenAI`) or a named entity (class, function, method, parameter, or variable name).
+- Wrap named entities in backticks so they render as code. Proper nouns are left unadorned.
+- Keep titles short and descriptive — save detail for the body.
+
+Examples:
 
 ```txt
 feat(langchain): add new chat completion feature
 fix(core): resolve type hinting issue in vector store
 chore(anthropic): update infrastructure dependencies
+feat(langchain): `ls_agent_type` tag on `create_agent` calls
+fix(openai): infer Azure chat profiles from model name
 ```
 
-Note how `feat(langchain)` includes a scope even though it is the main package and name of the repo.
+#### PR descriptions
+
+The description *is* the summary — do not add a `# Summary` header.
+
+- When the PR closes an issue, lead with the closing keyword on its own line at the very top, followed by a horizontal rule and then the body:
+
+  ```txt
+  Closes #123
+
+  ---
+
+  <rest of description>
+  ```
 
-#### Pull request guidelines
+  Only `Closes`, `Fixes`, and `Resolves` auto-close the referenced issue on merge. `Related:` or similar labels are informational and do not close anything.
 
-- Always add a disclaimer to the PR description mentioning how AI agents are involved with the contribution.
-- Describe the "why" of the changes, why the proposed solution is the right one. Limit prose.
-- Highlight areas of the proposed changes that require careful review.
+- Explain the *why*: the motivation and why this solution is the right one. Limit prose.
+- Write for readers who may be unfamiliar with this area of the codebase. Avoid insider shorthand and prefer language that is friendly to public viewers — this aids interpretability.
+- Do **not** cite line numbers; they go stale as soon as the file changes.
+- Rarely include full file paths or filenames. Reference the affected symbol, class, or subsystem by name instead.
+- Wrap class, function, method, parameter, and variable names in backticks.
+- Skip dedicated "Test plan" or "Testing" sections in most cases. Mention tests only when coverage is non-obvious, risky, or otherwise notable.
+- Call out areas of the change that require careful review.
+- Add a brief disclaimer noting AI-agent involvement in the contribution.
 
 ## Core development principles
 
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -79,23 +79,48 @@ uv run --group lint mypy .
 - uv.lock: Locked dependencies for reproducible builds
 - Makefile: Development tasks
 
-#### Commit standards
+#### PR and commit titles
 
-Suggest PR titles that follow Conventional Commits format. Refer to .github/workflows/pr_lint for allowed types and scopes. Note that all commit/PR titles should be in lowercase with the exception of proper nouns/named entities. All PR titles should include a scope with no exceptions. For example:
+Follow Conventional Commits. See `.github/workflows/pr_lint.yml` for allowed types and scopes. All titles must include a scope with no exceptions — even for the main `langchain` package.
+
+- Start the text after `type(scope):` with a lowercase letter, unless the first word is a proper noun (e.g. `Azure`, `GitHub`, `OpenAI`) or a named entity (class, function, method, parameter, or variable name).
+- Wrap named entities in backticks so they render as code. Proper nouns are left unadorned.
+- Keep titles short and descriptive — save detail for the body.
+
+Examples:
 
 ```txt
 feat(langchain): add new chat completion feature
 fix(core): resolve type hinting issue in vector store
 chore(anthropic): update infrastructure dependencies
+feat(langchain): `ls_agent_type` tag on `create_agent` calls
+fix(openai): infer Azure chat profiles from model name
 ```
 
-Note how `feat(langchain)` includes a scope even though it is the main package and name of the repo.
+#### PR descriptions
+
+The description *is* the summary — do not add a `# Summary` header.
+
+- When the PR closes an issue, lead with the closing keyword on its own line at the very top, followed by a horizontal rule and then the body:
+
+  ```txt
+  Closes #123
+
+  ---
+
+  <rest of description>
+  ```
 
-#### Pull request guidelines
+  Only `Closes`, `Fixes`, and `Resolves` auto-close the referenced issue on merge. `Related:` or similar labels are informational and do not close anything.
 
-- Always add a disclaimer to the PR description mentioning how AI agents are involved with the contribution.
-- Describe the "why" of the changes, why the proposed solution is the right one. Limit prose.
-- Highlight areas of the proposed changes that require careful review.
+- Explain the *why*: the motivation and why this solution is the right one. Limit prose.
+- Write for readers who may be unfamiliar with this area of the codebase. Avoid insider shorthand and prefer language that is friendly to public viewers — this aids interpretability.
+- Do **not** cite line numbers; they go stale as soon as the file changes.
+- Rarely include full file paths or filenames. Reference the affected symbol, class, or subsystem by name instead.
+- Wrap class, function, method, parameter, and variable names in backticks.
+- Skip dedicated "Test plan" or "Testing" sections in most cases. Mention tests only when coverage is non-obvious, risky, or otherwise notable.
+- Call out areas of the change that require careful review.
+- Add a brief disclaimer noting AI-agent involvement in the contribution.
 
 ## Core development principles
 
PATCH

echo "Gold patch applied."

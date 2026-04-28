#!/usr/bin/env bash
set -euo pipefail

cd /workspace/selenium

# Idempotency guard
if grep -qF "After any code change, run or suggest running `./go format` to prevent CI failur" ".github/copilot-instructions.md" && grep -qF "- Runs formatters for all bindings by default (pass `-<lang>` flags to skip spec" "AGENTS.md" && grep -qF "After any code change, run or suggest running `./go format` to prevent CI failur" "CLAUDE.local.md" && grep -qF "After any code change, run or suggest running `./go format` to prevent CI failur" "CLAUDE.md" && grep -qF "- **Using directives**: placed **outside** the namespace block; `System` namespa" "dotnet/AGENTS.md" && grep -qF "Java files are formatted with **google-java-format** (Google Java Style Guide)." "java/AGENTS.md" && grep -qF "- `trailingComma`: **\"all\"** (trailing commas everywhere ES5+ allows)" "javascript/selenium-webdriver/AGENTS.md" && grep -qF "Run `./go format` after changes; it will auto-fix formatting. Then check `git di" "py/AGENTS.md" && grep -qF "- RuboCop plugins active: `rubocop-performance`, `rubocop-rake`, `rubocop-rspec`" "rb/AGENTS.md" && grep -qF "Rust files are formatted with **rustfmt** (standard Rust formatting, no custom c" "rust/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -1 +1,2 @@
-Always read AGENTS.md before answering
+Always read AGENTS.md before answering.
+After any code change, run or suggest running `./go format` to prevent CI failures from formatter checks.
diff --git a/AGENTS.md b/AGENTS.md
@@ -66,12 +66,27 @@ See language-specific AGENTS.md for applicable logging usage
 This project does not follow semantic versioning (semver); before removing public functionality, mark it as deprecated with a message pointing to the alternative.
 See language-specific AGENTS.md for applicable deprecation usage
 
+## Formatting
+After making code changes, always run (or instruct the user to run):
+```
+./go format
+```
+This invokes the Rake `:format` task, which:
+- Runs `buildifier` on all Bazel (`BUILD`, `*.bzl`, `WORKSPACE`) files — always, for every change
+- Runs `update_copyright` to add/refresh Apache license headers — always, for every change
+- Runs formatters for all bindings by default (pass `-<lang>` flags to skip specific ones, e.g. `-java`)
+
+`./go format` auto-fixes files in place. After running it, check `git diff` to see if any files were
+modified — if so, those changes must be committed. CI runs `./go format` then fails if `git diff` is
+non-empty, so un-formatted code will fail CI.
+For stricter lint checks beyond formatting, use `./go lint`.
+
 ## General Guidelines
 - Comments should explain *why*, not *what* - prefer well-named methods over comments
 - PRs should focus on one thing; we squash PRs to default `trunk` branch
 - Prefer copying files to deleting and recreating to maintain git history
 - Avoid running `bazel clean --expunge`
-- Run or suggest running `./scripts/format.sh` or `./go all:lint` before pushing to prevent CI failures
+- Run or suggest running `./go format` before pushing to prevent CI failures
 
 ## High risk changes (request verification before modifying unless explicitly instructed)
 - Everything referenced above as high risk
diff --git a/CLAUDE.local.md b/CLAUDE.local.md
@@ -1 +1,3 @@
 @.local/AGENTS.md
+
+After any code change, run or suggest running `./go format` to prevent CI failures from formatter checks.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1 +1,3 @@
 @AGENTS.md
+
+After any code change, run or suggest running `./go format` to prevent CI failures from formatter checks.
diff --git a/dotnet/AGENTS.md b/dotnet/AGENTS.md
@@ -42,3 +42,14 @@ Use XML documentation comments for public APIs:
 /// <returns>Description.</returns>
 /// <exception cref="ExceptionType">When condition.</exception>
 ```
+
+## Formatting
+C# files are formatted with **`dotnet format`** (style + whitespace).
+Run `./go format` after changes; it will auto-fix most violations.
+
+Key rules enforced (from `dotnet/.editorconfig`):
+- **Namespaces**: file-scoped (`namespace Foo.Bar;` not block-wrapped)
+- **Using directives**: placed **outside** the namespace block; `System` namespaces sorted first
+- **Braces**: Allman style — opening brace on its own line for all blocks
+- **Spacing**: no space after cast, space after commas, space around binary operators
+- Remove unnecessary `using` directives (IDE0005 treated as warning)
diff --git a/java/AGENTS.md b/java/AGENTS.md
@@ -43,3 +43,13 @@ Use Javadoc for public APIs:
  * @throws ExceptionType when condition
  */
 ```
+
+## Formatting
+Java files are formatted with **google-java-format** (Google Java Style Guide).
+Run `./go format` after changes; it will auto-fix all style issues.
+
+Key rules enforced:
+- 2-space indentation (no tabs)
+- Column limit: 100 characters
+- Braces on the same line (K&R style), including single-statement bodies
+- Imports: organized and sorted consistently
diff --git a/javascript/selenium-webdriver/AGENTS.md b/javascript/selenium-webdriver/AGENTS.md
@@ -47,3 +47,16 @@ Use JSDoc for public APIs:
  * @throws {ErrorType} when condition
  */
 ```
+
+## Formatting
+
+JavaScript files are formatted with **Prettier**.
+Run `./go format` after changes; it will auto-fix all style issues.
+
+Active Prettier config (`.prettierrc`):
+
+- `printWidth`: **120** characters
+- `singleQuote`: **true** (use `'` not `"`)
+- `semi`: **false** (no semicolons)
+- `trailingComma`: **"all"** (trailing commas everywhere ES5+ allows)
+- `endOfLine`: **"lf"** (Unix line endings only)
diff --git a/py/AGENTS.md b/py/AGENTS.md
@@ -90,3 +90,17 @@ def method(param: str) -> bool:
         ValueError: When condition.
     """
 ```
+
+## Formatting
+
+Python files are formatted with **ruff format** and checked with **ruff check**.
+Run `./go format` after changes; it will auto-fix formatting. Then check `git diff` to see what changed.
+Run `./go lint` to also run linting (stricter).
+
+Key rules enforced (from `py/pyproject.toml`):
+- Line length: **120 characters**
+- Target version: Python 3.10+
+- Ruff lint rules active: `D, E, F, I, PT, UP, RUF, TID252`
+  - `I` = import ordering (imports must be sorted; `isort`-compatible)
+  - `UP` = use modern Python idioms (e.g. `X | None` instead of `Optional[X]`)
+  - `E/F` = pycodestyle / pyflakes errors (unused imports, undefined names, etc.)
diff --git a/rb/AGENTS.md b/rb/AGENTS.md
@@ -49,3 +49,13 @@ Use YARD for public APIs:
 # @return [Type] description
 # @raise [ErrorClass] when condition
 ```
+
+## Formatting
+Ruby files are formatted with **RuboCop** (target Ruby 3.2).
+Run `./go format` after changes; it will auto-fix most violations (`-a` flag).
+
+Key rules enforced (from `rb/.rubocop.yml`):
+- No spaces inside hash literal braces: `{key: val}` not `{ key: val }`
+- Line length limit applies (comments excluded); keep lines reasonably short
+- RuboCop plugins active: `rubocop-performance`, `rubocop-rake`, `rubocop-rspec`
+- Any violation at `Fatal` severity (`--fail-level F`) blocks CI
diff --git a/rust/AGENTS.md b/rust/AGENTS.md
@@ -42,3 +42,11 @@ Use doc comments for public APIs:
 /// # Errors
 /// Returns `ErrorType` when condition.
 ```
+
+## Formatting
+Rust files are formatted with **rustfmt** (standard Rust formatting, no custom config).
+Run `./go format` after changes; it will auto-fix all style issues.
+
+Key rules enforced:
+- Standard Rust style (rustfmt defaults): 4-space indentation, 100-char line length
+- `use` statements grouped and sorted per standard conventions
PATCH

echo "Gold patch applied."

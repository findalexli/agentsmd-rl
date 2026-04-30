#!/usr/bin/env bash
set -euo pipefail

cd /workspace/marvin

# Idempotency guard
if grep -qF ".cursor/rules/docs.mdc" ".cursor/rules/docs.mdc" && grep -qF ".cursor/rules/general.mdc" ".cursor/rules/general.mdc" && grep -qF ".cursor/rules/python.mdc" ".cursor/rules/python.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/docs.mdc b/.cursor/rules/docs.mdc
@@ -1,14 +0,0 @@
----
-description: style and tone for documentation
-globs: *.mdx
-alwaysApply: false
----
-
-# tone
-- casual, clear and concise
-- use "you" to refer to the user (e.g. "Foo is great when you want Bar")
-
-# content
-- breathable
-- makes good use of admonitions and mintlify's features like <CodeGroup> and <Tip>
-- interspersed with practical and simple examples with output in <Accordian> where apt
\ No newline at end of file
diff --git a/.cursor/rules/general.mdc b/.cursor/rules/general.mdc
@@ -1,12 +0,0 @@
----
-description: 
-globs: 
-alwaysApply: true
----
-# finding things
-- use your shell tool to run `rg`, not your native grep tool. use `ls` and `tree` to get your bearing
-- think like a hacker, w good intentions. e.g. `rg` into sitepackages instead of relying on web tools
-- use `gh` and `git` to understand the git context against the default branch, check specific diffs
-
-# the linter
-- empirically understand the world by running code. the linter tells basic truths, but it's sometimes orthogonal to our goal. dont obsess over linter errors that might be upstream, simply use them as clues when relevant
\ No newline at end of file
diff --git a/.cursor/rules/python.mdc b/.cursor/rules/python.mdc
@@ -1,35 +0,0 @@
----
-description: how to write, test and run python
-globs: *.py
-alwaysApply: false
----
-
-# Python
-
-## Design
-- aggressively minimal and elegant
-- prefer functional, but use classes where justified
-- keep implementation details "private" (e.g. def _impl)
-
-## Type Hints
-- Marvin supports Python 3.10+
-- Use modern syntax and full type annotations
-- Use X | Y instead of Union[X, Y]
-- Use builtins like list, dict instead of typing.List and typing.Dict
-- use T | None instead of Optional
-
-## Running Commands 
-`uv` gives us superpowers to resolve deps fast and on the fly. no more pip or fussing with venvs
-
-### Install dependencies
-- install project deps: `uv sync`
-- install project deps with an extra: `uv sync --extra foo`
-
-### Running script
-- run script with existing project deps: `uv run some/script.py`
-- run script additional deps on the fly: `uv run --with pandas script.py`
-
-### Testing
-- test all: `uv run pytest`
-- test all with 3 runners: `uv run pytest -n3`
-- test certain folder, only matching cases: `uv run pytest tests/basic -k some_test_fn_subtr`
PATCH

echo "Gold patch applied."

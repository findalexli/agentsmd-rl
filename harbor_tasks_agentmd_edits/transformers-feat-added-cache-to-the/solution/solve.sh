#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotent: skip if already applied
if grep -q '_content_hash' utils/check_modeling_structure.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.ai/AGENTS.md b/.ai/AGENTS.md
index c404c050d2a1..e2baaa788d4f 100644
--- a/.ai/AGENTS.md
+++ b/.ai/AGENTS.md
@@ -1,7 +1,8 @@
 ## Useful commands
-- `make style`: runs formatters, linters and type checker, necessary to pass code style checks
+- `make style`: runs formatters and linters (ruff), necessary to pass code style checks
+- `make typing`: runs the ty type checker and model structure rules
 - `make fix-repo`: auto-fixes copies, modular conversions, doc TOCs, docstrings in addition to the `make style` fixes
-- `make check-repo` — CI-style consistency checks
+- `make check-repo` — CI-style consistency checks (includes `make typing`)
 - Many tests are marked as 'slow' and skipped by default in the CI. To run them, use: `RUN_SLOW=1 pytest ...`

 `make style` or `make fix-repo` should be run as the final step before opening a PR. The CI will run `make check-repo` and fail if any issues are found.
diff --git a/.ai/skills/add-or-fix-type-checking/SKILL.md b/.ai/skills/add-or-fix-type-checking/SKILL.md
index 1c92c85e826a..324751bcec97 100644
--- a/.ai/skills/add-or-fix-type-checking/SKILL.md
+++ b/.ai/skills/add-or-fix-type-checking/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: add-or-fix-type-checking
-description: Fixes broken typing checks detected by ty, make style, or make check-repo. Use when typing errors appear in local runs, CI, or PR logs.
+description: Fixes broken typing checks detected by ty, make typing, or make check-repo. Use when typing errors appear in local runs, CI, or PR logs.
 ---

 # Add Or Fix Type Checking
@@ -8,15 +8,15 @@ description: Fixes broken typing checks detected by ty, make style, or make chec
 ## Input

 - `<target>`: module or directory to type-check (if known).
-- Optional `make style` or CI output showing typing failures.
+- Optional `make typing` or CI output showing typing failures.

 ## Workflow

 1. **Identify scope from the failing run**:
-   - If you already have `make style` or CI output, extract the failing file/module paths.
+   - If you already have `make typing` or CI output, extract the failing file/module paths.
    - If not, run:
      ```bash
-     make style
+     make typing
      ```
    - Choose the narrowest target that covers the failures.

@@ -207,7 +207,7 @@ description: Fixes broken typing checks detected by ty, make style, or make chec

 7. **Verify and close the PR loop**:
    - Re-run `ty check` on the same `<target>`
-   - Re-run `make style` to confirm the full style/type step passes
+   - Re-run `make typing` to confirm the type/model-rules step passes
    - If working toward merge readiness, run `make check-repo`
    - Ensure runtime behavior did not change and run relevant tests

diff --git a/.gitignore b/.gitignore
index 73b9cd0955ac..527d18de6692 100644
--- a/.gitignore
+++ b/.gitignore
@@ -170,6 +170,9 @@ tags
 # ruff
 .ruff_cache

+# modeling structure lint cache
+utils/.check_modeling_structure_cache.json
+
 # modular conversion
 *.modular_backup

diff --git a/Makefile b/Makefile
index f8168fef8418..0c91da7d9e2c 100644
--- a/Makefile
+++ b/Makefile
@@ -1,7 +1,7 @@
 # make sure to test the local checkout in scripts and not the pre-installed one (don't use quotes!)
 export PYTHONPATH = src

-.PHONY: style check-repo check-model-rules check-model-rules-pr check-model-rules-all fix-repo test test-examples benchmark codex claude clean-ai
+.PHONY: style typing check-repo fix-repo test test-examples benchmark codex claude clean-ai

 check_dirs := examples tests src utils scripts benchmark benchmark_v2
 exclude_folders :=  ""
@@ -16,7 +16,11 @@ style:
 	ruff format $(check_dirs) setup.py conftest.py --exclude $(exclude_folders)
 	python utils/custom_init_isort.py
 	python utils/sort_auto_mappings.py
+
+# Run ty type checker and model structure rules
+typing:
 	python utils/check_types.py $(ty_check_dirs)
+	python utils/check_modeling_structure.py

 # Check that the repo is in a good state (both style and consistency CI checks)
 # Note: each line is run in its own shell, and doing `-` before the command ignores the errors if any, continuing with next command
@@ -24,6 +28,7 @@ check-repo:
 	ruff check $(check_dirs) setup.py conftest.py
 	ruff format --check $(check_dirs) setup.py conftest.py
 	python utils/check_types.py $(ty_check_dirs)
+	python utils/check_modeling_structure.py
 	-python utils/custom_init_isort.py --check_only
 	-python utils/sort_auto_mappings.py --check_only
 	-python -c "from transformers import *" || (echo '🚨 import failed, this means you introduced unprotected imports! 🚨'; exit 1)
@@ -33,7 +38,6 @@ check-repo:
 	-python utils/check_docstrings.py
 	-python utils/check_dummies.py
 	-python utils/check_repo.py
-	-python utils/check_modeling_structure.py
 	-python utils/check_inits.py
 	-python utils/check_pipeline_typing.py
 	-python utils/check_config_docstrings.py
@@ -49,16 +53,7 @@ check-repo:
 	}


-check-model-rules:
-	python utils/check_modeling_structure.py --changed-only --base-ref origin/main
-

-check-model-rules-pr:
-	python utils/check_modeling_structure.py --changed-only --base-ref origin/main --github-annotations
-
-
-check-model-rules-all:
-	python utils/check_modeling_structure.py


 # Run all repo checks for which there is an automatic fix, most notably modular conversions
diff --git a/docs/source/en/pr_checks.md b/docs/source/en/pr_checks.md
index 1ecf9da1322e..6c713a97ec4a 100644
--- a/docs/source/en/pr_checks.md
+++ b/docs/source/en/pr_checks.md
@@ -92,6 +92,12 @@ Code formatting is applied to all the source files, the examples and the tests u
 make style
 ```

+Type checking (via `ty`) and model structure rules are run separately with:
+
+```bash
+make typing
+```
+
 The CI checks those have been applied inside the `ci/circleci: check_code_quality` check. It also runs `ruff`, that will have a basic look at your code and will complain if it finds an undefined variable, or one that is not used. To run that check locally, use

 ```bash
diff --git a/utils/check_modeling_structure.py b/utils/check_modeling_structure.py
index 8bb57e584f46..44157cf72fa1 100644
--- a/utils/check_modeling_structure.py
+++ b/utils/check_modeling_structure.py
@@ -52,6 +52,8 @@

 import argparse
 import ast
+import hashlib
+import json
 import subprocess
 import sys
 from collections.abc import Callable
@@ -120,6 +122,27 @@ def _load_rule_specs() -> dict[str, dict]:
     rule_id: spec["allowlist_models"] for rule_id, spec in TRF_RULE_SPECS.items() if spec["allowlist_models"]
 }
 CONSOLE = Console(stderr=True)
+CACHE_PATH = Path(__file__).with_name(".check_modeling_structure_cache.json")
+
+
+def _content_hash(text: str, enabled_rules: set[str]) -> str:
+    h = hashlib.sha256(text.encode("utf-8"))
+    h.update(",".join(sorted(enabled_rules)).encode("utf-8"))
+    return h.hexdigest()
+
+
+def _load_cache() -> dict[str, str]:
+    try:
+        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
+    except (FileNotFoundError, json.JSONDecodeError, OSError):
+        return {}
+
+
+def _save_cache(cache: dict[str, str]) -> None:
+    try:
+        CACHE_PATH.write_text(json.dumps(cache, sort_keys=True, indent=2) + "\n", encoding="utf-8")
+    except OSError:
+        pass


 @dataclass(frozen=True)
@@ -946,6 +969,11 @@ def parse_args() -> argparse.Namespace:
         action="store_true",
         help="Disable interactive progress animation.",
     )
+    parser.add_argument(
+        "--no-cache",
+        action="store_true",
+        help="Ignore the lint cache and re-check every file.",
+    )
     parser.add_argument(
         "--enable-all-trf-rules",
         action="store_true",
@@ -1052,14 +1080,34 @@ def main() -> int:
         else nullcontext()
     )

+    use_cache = not args.no_cache
+    cache = _load_cache() if use_cache else {}
+    new_cache: dict[str, str] = {}
+    skipped = 0
+
     with status_ctx:
         for file_path in modeling_files:
             try:
                 text = file_path.read_text(encoding="utf-8")
-                violations.extend(analyze_file(file_path, text, enabled_rules=enabled_rules))
+                file_key = str(file_path)
+                digest = _content_hash(text, enabled_rules)
+
+                if use_cache and cache.get(file_key) == digest:
+                    new_cache[file_key] = digest
+                    skipped += 1
+                    continue
+
+                file_violations = analyze_file(file_path, text, enabled_rules=enabled_rules)
+                violations.extend(file_violations)
+
+                if not file_violations:
+                    new_cache[file_key] = digest
             except Exception as exc:
                 violations.append(Violation(file_path=file_path, line_number=1, message=f"failed to parse ({exc})."))

+    if use_cache:
+        _save_cache(new_cache)
+
     if len(violations) > 0:
         violations = sorted(violations, key=lambda v: (str(v.file_path), v.line_number, v.message))
         for violation in violations:

PATCH

echo "Patch applied successfully."

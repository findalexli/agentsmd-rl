#!/usr/bin/env bash
set -euo pipefail

cd /workspace/olmo-core

# Idempotency guard
if grep -qF "- Name individual test functions `test_*` and prefer `pytest.mark.parametrize` t" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -16,7 +16,10 @@ pip install -e '.[all]'
 pytest -v src/
 
 # Run a specific test file
-pytest src/test/path/to/test_file.py
+pytest -v src/test/path/to/test_file.py
+
+# Filter to specific tests by keywords
+pytest -v src/test/path/to/test_file.py -k 'keyword'
 
 # Auto-format code
 make style
@@ -35,6 +38,35 @@ make type-check      # mypy
 - Linting: `ruff` (ignores F403, F405, E501; F401 ignored in `__init__.py`)
 - Type checking: `mypy` with `ignore_missing_imports = true`
 
+## Docstrings
+
+- Docstrings should be included on all public classes, methods, and functions.
+- We use Sphinx to automatically build API docs by pulling from those docstrings.
+- The syntax of the docstrings is a superset of reStructuredText with additional Sphinx-specific syntax for things like:
+  - Cross-document links, e.g.:
+    ```
+    :class:`foo.Foo`  <- links to the class named 'Foo' in the module 'foo'
+    :mod:`foo`        <- links to the module named 'foo'
+    :func:`foo.bar`   <- links to the function named 'bar' in the module named 'foo'
+    ```
+  - Documenting parameters (`:param ...:`), return values (`:returns:`), or expected exceptions (`:raises ...:`).
+
+Here's a toy example for a function:
+
+```python
+def read_file(path: str) -> str:
+    """
+    Read a file from disk.
+
+    :param path: The path to the file.
+
+    :returns: The contents of the file.
+
+    :raises FileNotFoundError: If the file doesn't exist.
+    """
+    pass
+```
+
 ## Architecture
 
 ### Configuration System (`src/olmo_core/config.py`)
@@ -73,6 +105,10 @@ Everything is configured via `@dataclass` classes inheriting from `Config`. This
 - Optimizer configs (`AdamWConfig`, `SkipStepAdamWConfig`, `LionConfig`) and LR schedulers (`CosWithWarmup`, etc.).
 - `SkipStepOptimizer`: Wrapper for gradient clipping with loss spike detection.
 
+### Examples (src/examples)
+
+Runnable, self-contained examples and reference scripts.
+
 ### Training Scripts
 
 Two patterns exist:
@@ -119,5 +155,6 @@ Pre-built images are listed in the `OLMoCoreBeakerImage` enum in `src/olmo_core/
 ## Testing
 
 - Tests in `src/test/` mirror the source structure.
+- Name individual test functions `test_*` and prefer `pytest.mark.parametrize` to cover multiple inputs or configurations without duplicating code.
 - GPU tests use `@pytest.mark.gpu` and are skipped without a GPU.
 - Distributed tests use helpers in `src/olmo_core/testing/distributed.py`.
PATCH

echo "Gold patch applied."

#!/usr/bin/env bash
set -euo pipefail

cd /workspace/noether

# Idempotency guard
if grep -qF "when appropriate include Examples in Sphinx syntax with the testcode directive." "AGENTS.md" && grep -qF "See @AGENTS.md for project setup, testing, formatting, and documentation standar" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,5 +1,6 @@
 Hello agent. You are one of the most talented programmers of your generation.
-# Contribution Guide
+Noether is a ML research framework for Engineering AI.
+# Project setup
 
 The project is managed with `uv` and `pyproject.toml`
 **ALWAYS use `uv run` for all Python commands and tools.**
@@ -19,18 +20,10 @@ Examples:
 - **Running with Coverage**: `uv run pytest --cov=src`
 
 **Write testable code and add unit tests where it makes sense.**
+Don't test trivial code or external libraries
+Tests for erroneous logic must fail.
 
-Guidelines:
-- Add unit tests for new functions, classes, and methods
-- Test edge cases and error conditions
-- Keep tests focused and isolated
-- Use descriptive test names that explain what's being tested
-- Mock external dependencies to keep tests fast and reliable
-- Don't test trivial code or external libraries
-
-## Code Quality
-
-### Formatting and Linting
+## Formatting and Linting
 
 Use **ruff** for both formatting and linting:
 
@@ -45,26 +38,20 @@ uv run ruff check --fix .
 uv run ruff format .
 ```
 
-### Type Checking
+## Type Checking
 
 When appropriate, write **typed Python code** and check with **mypy**:
 
 ```bash
 uv run mypy src/
 ```
 
-Use type hints for:
-- Function parameters and return values
-- Class attributes
-- Variables when the type is not obvious
-
-## Documentation
-
-### Docstrings
+## Docstrings
 
 **ALWAYS update Python docstrings** when modifying code.
 
-Follow Google-style or NumPy-style docstring conventions:
+Follow Google-style or NumPy-style docstring conventions,
+when appropriate include Examples in Sphinx syntax with the testcode directive.
 
 ```python
 def example_function(param1: str, param2: int) -> bool:
@@ -79,82 +66,22 @@ def example_function(param1: str, param2: int) -> bool:
     Returns:
         Description of return value
 
+    Example:
+    
+        .. testcode::
+
+        print("Hello World")
+
     Raises:
         ValueError: Description of when this is raised
     """
 ```
 
-### Sphinx Documentation
+## Sphinx Documentation
 
 **ALWAYS update Sphinx documentation** when changing functionality.
 
 - Documentation location: `docs/`
 - Keep documentation **concise and clear**
 - Update relevant `.rst` files when adding or modifying features
 - Build docs locally to verify: `uv run sphinx-build -b html docs/source docs/_build/html`
-
-## API Compatibility
-
-### Breaking Changes
-
-**Avoid interface-breaking changes unless necessary.**
-
-When a breaking change is required:
-1. **Clearly state to the user** that the change is breaking
-2. **Specify that it requires a major version jump** (semantic versioning)
-3. Document the migration path for users
-4. Consider deprecation warnings before removal
-
-Examples of breaking changes:
-- Removing or renaming public functions, classes, or methods
-- Changing function signatures (parameters, return types)
-- Changing expected behavior of public APIs
-- Removing or renaming configuration options
-
-### Non-Breaking Changes
-
-Prefer:
-- Adding new optional parameters with defaults
-- Adding new functions/classes/methods
-- Deprecation warnings before removal
-- Backward-compatible extensions
-
-## Code Style
-
-### Readability First
-
-**Prefer readability over cleverness.**
-
-Guidelines:
-- Write clear, self-documenting code
-- Use descriptive variable and function names
-- Break complex logic into smaller, named functions
-- Only add code comments for non-obvious business logic
-- Avoid overly clever one-liners when they harm clarity
-- Explicit is better than implicit
-
-Example:
-```python
-# Good: Clear and readable
-def calculate_total_price(items: list[Item]) -> float:
-    subtotal = sum(item.price for item in items)
-    tax = subtotal * TAX_RATE
-    return subtotal + tax
-
-# Avoid: Too clever
-def calc(i): return sum(x.p for x in i) * 1.1
-```
-
-## Workflow Summary
-
-When making changes:
-
-1. ✅ Write or update code with type hints
-2. ✅ Write unit tests for new functionality
-3. ✅ Update docstrings
-4. ✅ Update Sphinx documentation if functionality changed
-5. ✅ Run formatters: `uv run ruff format .`
-6. ✅ Run linting: `uv run ruff check --fix .`
-7. ✅ Run type checking: `uv run mypy src/` (when appropriate)
-8. ✅ Run tests: `uv run pytest`
-9. ✅ Check if changes are breaking and inform user if major version bump needed
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+See @AGENTS.md for project setup, testing, formatting, and documentation standards.
PATCH

echo "Gold patch applied."

#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vision-agents

# Idempotency guard
if grep -qF "- Don't add error handling, logging, validation, comments, abstractions, config " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -33,8 +33,11 @@ uv run --no-sync mypy
 - Framework: pytest. Never mock.
 - `@pytest.mark.asyncio` is not needed (asyncio_mode = auto).
 - Integration tests use `@pytest.mark.integration`.
-- Never adjust `sys.path`.
+- NEVER adjust `sys.path`.
 - Keep unit-tests for the class under the same test class. Do not spread them around different test classes. For example, tests for `Agent` must be inside `TestAgent`, etc.
+- ALWAYS test behavior, not calling a path.
+- Use pytest.fixture for test setup, not helper methods
+- NEVER observe method calls in tests; assert on outputs and state.
 
 ## Python rules
 
@@ -51,40 +54,51 @@ uv run --no-sync mypy
 
 ## Code style
 
-**Imports**:
+### Imports:
 
 - ordered as: stdlib, third-party, local package, relative. Use `TYPE_CHECKING` guard for imports only needed by type annotations.
 - Never import from private modules (`_foo`) outside of the package's own `__init__.py`. Use the public re-export (e.g. `from vision_agents.testing import TestResponse`, not
   `from vision_agents.testing._run_result import TestResponse`).
 
-**Naming**:
+### Naming:
 
 - private attributes and methods use a leading underscore (`_sessions`, `_warmup_agent`). Public API is plain snake_case.
 
-**Type annotations**:
+### Type annotations:
 
 - use them everywhere. Modern syntax: `X | Y` unions, `dict[str, T]` generics, full `Callable` signatures, `Optional` for nullable params.
 
-**Logging**:
+### Logging:
+
 module-level `logger = logging.getLogger(__name__)`. Use `debug` for lifecycle, `info` for notable events, `error` for failures without a traceback,
 `exception` for errors with traceback.
 
 - In hot paths (audio processing, event handling), guard debug logging behind `if logger.isEnabledFor(logging.DEBUG):` to avoid formatting overhead when debug is disabled.
 
-**Constructor validation**:
+### Constructor validation:
 
 - raise `ValueError` with a descriptive message for invalid args. Prefer custom domain exceptions over generic ones.
 
-**Async patterns**:
+### Async patterns:
 
 - async-first lifecycle methods (`start`/`stop`). Support `__aenter__`/`__aexit__` for context manager usage.
 - Use `asyncio.Lock`, `asyncio.Task`, `asyncio.gather` for concurrency.
 - Clean up resources in `finally` blocks.
 
-**Method order**:
+### Method order:
 
 - `__init__`, public lifecycle methods, properties, public feature methods, private helpers, dunder methods.
 
+### Other
+
+- Smallest possible diff. Prefer deleting code over adding it.
+- Don't add error handling, logging, validation, comments, abstractions, config options, or "future-proofing" I didn't
+  ask for.
+- Match the style and abstraction level of surrounding code. Don't introduce new patterns or helpers unless asked.
+- Fix root causes, not symptoms. No try/except to swallow bugs.
+- Change only what I asked for. Don't refactor adjacent code — ask first.
+- Do not remove valid comments when editing/refactoring code.
+
 ## Token efficiency
 
 - When making multiple related changes to the same file, combine them into fewer Edit calls with enough surrounding context, rather than one edit per change.
PATCH

echo "Gold patch applied."

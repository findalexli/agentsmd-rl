#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cocoindex

# Idempotency guard
if grep -qF "We prefer end-to-end tests on user-facing APIs, over unit tests on smaller inter" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -160,13 +160,28 @@ app = coco.App(
 app.update(report_to_stdout=True)
 ```
 
-## Principles
+## Code Conventions
 
-* We prefer end-to-end tests on user-facing APIs, over unit tests on smaller internal functions. With this said, there're cases where unit tests are necessary, e.g. for internal logic with various situations and edge cases, in which case it's usually easier to cover various scenarios with unit tests.
+### Internal vs External Modules
 
-## Python Code Conventions
+We distinguish between **internal modules** (under packages with `_` prefix, e.g. `_internal.*`) and **external modules** (which users can directly import).
 
-* Avoid leaking internal symbols in public modules. Import modules with underscore prefix and reference their symbols:
-  * `import typing as _typing`, then reference as `_typing.Literal`, `_typing.Optional`, etc.
-  * `from cocoindex._internal import core as _core`
-  * `from cocoindex.resources import chunk as _chunk`
+**External modules** (user-facing, e.g. `cocoindex/ops/sentence_transformers.py`):
+
+* Be strict about not leaking implementation details
+* Use `__all__` to explicitly list public exports
+* Prefix ALL non-public symbols with `_`, including:
+  * Standard library imports: `import threading as _threading`, `import typing as _typing`
+  * Third-party imports: `import numpy as _np`, `from numpy.typing import NDArray as _NDArray`
+  * Internal package imports: `from cocoindex.resources import schema as _schema`
+* Exception: `TYPE_CHECKING` imports for type hints don't need prefixing
+
+**Internal modules** (e.g. `cocoindex/_internal/component_ctx.py`):
+
+* Less strict since users shouldn't import these directly
+* Standard library and internal imports don't need underscore prefix
+* Only prefix symbols that are truly private to the module itself (e.g. `_context_var` for a module-private ContextVar)
+
+### Testing Guidelines
+
+We prefer end-to-end tests on user-facing APIs, over unit tests on smaller internal functions. With this said, there're cases where unit tests are necessary, e.g. for internal logic with various situations and edge cases, in which case it's usually easier to cover various scenarios with unit tests.
PATCH

echo "Gold patch applied."

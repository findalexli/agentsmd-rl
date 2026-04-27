#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agents

# Idempotency guard
if grep -qF "**Note:** The `type Alias = ...` statement syntax (PEP 695) was introduced in **" "plugins/python-development/skills/python-type-safety/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/python-development/skills/python-type-safety/SKILL.md b/plugins/python-development/skills/python-type-safety/SKILL.md
@@ -331,24 +331,28 @@ class Comparable(Protocol):
 
 Create meaningful type names.
 
-**Note:** The `type` statement was introduced in Python 3.10 for simple aliases. Generic type statements require Python 3.12+.
+**Note:** The `type Alias = ...` statement syntax (PEP 695) was introduced in **Python 3.12**, not 3.10. For projects targeting earlier versions (including 3.10/3.11), use the `TypeAlias` annotation (PEP 613, available since Python 3.10).
 
 ```python
-# Python 3.10+ type statement for simple aliases
+# Python 3.12+ type statement (PEP 695)
 type UserId = str
 type UserDict = dict[str, Any]
 
-# Python 3.12+ type statement with generics
+# Python 3.12+ type statement with generics (PEP 695)
 type Handler[T] = Callable[[Request], T]
 type AsyncHandler[T] = Callable[[Request], Awaitable[T]]
+```
 
-# Python 3.9-3.11 style (needed for broader compatibility)
+```python
+# Python 3.10-3.11 style (needed for broader compatibility)
 from typing import TypeAlias
 from collections.abc import Callable, Awaitable
 
 UserId: TypeAlias = str
 Handler: TypeAlias = Callable[[Request], Response]
+```
 
+```python
 # Usage
 def register_handler(path: str, handler: Handler[Response]) -> None:
     ...
PATCH

echo "Gold patch applied."

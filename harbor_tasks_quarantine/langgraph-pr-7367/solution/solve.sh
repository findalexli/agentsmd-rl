#!/bin/bash
set -e

REPO=/workspace/langgraph

# Patch the main source file
cd "$REPO/libs/langgraph/langgraph/_internal"

# Check if already applied
if grep -q "def _exclude_as_metadata" _config.py; then
    cat <<'PATCH' | git apply -
diff --git a/libs/langgraph/langgraph/_internal/_config.py b/libs/langgraph/langgraph/_internal/_config.py
index fe1aad509..e841d7b0a 100644
--- a/libs/langgraph/langgraph/_internal/_config.py
+++ b/libs/langgraph/langgraph/_internal/_config.py
@@ -1,7 +1,7 @@
 from __future__ import annotations

 from collections import ChainMap
-from collections.abc import Mapping, Sequence
+from collections.abc import Sequence
 from os import getenv
 from typing import Any, cast

@@ -308,22 +308,4 @@ def ensure_config(*configs: RunnableConfig | None) -> RunnableConfig:
         for k, v in config.items():
             if _is_not_empty(v) and k not in CONFIG_KEYS:
                 empty[CONF][k] = v
-    _empty_metadata = empty["metadata"]
-    for key, value in empty[CONF].items():
-        if _exclude_as_metadata(key, value, _empty_metadata):
-            continue
-        _empty_metadata[key] = value
     return empty
-
-
-_OMIT = ("key", "token", "secret", "password", "auth")
-
-
-def _exclude_as_metadata(key: str, value: Any, metadata: Mapping[str, Any]) -> bool:
-    key_lower = key.casefold()
-    return (
-        key.startswith("__")
-        or not isinstance(value, (str, int, float, bool))
-        or key in metadata
-        or any(substr in key_lower for substr in _OMIT)
-    )
PATCH
    echo "Source patch applied successfully"
else
    echo "Source patch already applied or not needed"
fi

# Patch the test file
cd "$REPO/libs/langgraph/tests"

if grep -q 'expected = {"includeme", "andme", "nooverride"}' test_utils.py; then
    cat <<'TESTPATCH' | git apply -
diff --git a/libs/langgraph/tests/test_utils.py b/libs/langgraph/tests/test_utils.py
index c965a483e..e841d7b0a 100644
--- a/libs/langgraph/tests/test_utils.py
+++ b/libs/langgraph/tests/test_utils.py
@@ -312,7 +312,7 @@ def test_configurable_metadata():
         },
         "metadata": {"nooverride": 18},
     }
-    expected = {"includeme", "andme", "nooverride"}
+    expected = {"nooverride"}
     merged = ensure_config(config)
     metadata = merged["metadata"]
     assert metadata.keys() == expected
TESTPATCH
    echo "Test patch applied successfully"
else
    echo "Test patch already applied or not needed"
fi

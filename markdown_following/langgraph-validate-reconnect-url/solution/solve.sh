#!/bin/bash
set -e

cd /workspace/langgraph

# Check if already applied (idempotency)
if grep -q "_validate_reconnect_location" libs/sdk-py/langgraph_sdk/_shared/utilities.py; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/libs/sdk-py/langgraph_sdk/__init__.py b/libs/sdk-py/langgraph_sdk/__init__.py
index 67aa624ff19..25ef2935fab 100644
--- a/libs/sdk-py/langgraph_sdk/__init__.py
+++ b/libs/sdk-py/langgraph_sdk/__init__.py
@@ -3,6 +3,6 @@
 from langgraph_sdk.encryption import Encryption
 from langgraph_sdk.encryption.types import EncryptionContext

-__version__ = "0.3.12"
+__version__ = "0.3.13"

 __all__ = ["Auth", "Encryption", "EncryptionContext", "get_client", "get_sync_client"]
diff --git a/libs/sdk-py/langgraph_sdk/_async/http.py b/libs/sdk-py/langgraph_sdk/_async/http.py
index 48e224be044..47c0f043fd0 100644
--- a/libs/sdk-py/langgraph_sdk/_async/http.py
+++ b/libs/sdk-py/langgraph_sdk/_async/http.py
@@ -12,7 +12,10 @@
 import httpx
 import orjson

-from langgraph_sdk._shared.utilities import _orjson_default
+from langgraph_sdk._shared.utilities import (
+    _orjson_default,
+    _validate_reconnect_location,
+)
 from langgraph_sdk.errors import _araise_for_status_typed
 from langgraph_sdk.schema import QueryParamTypes, StreamPart
 from langgraph_sdk.sse import SSEDecoder, aiter_lines_raw
@@ -164,6 +167,7 @@ async def request_reconnect(
             loc = r.headers.get("location")
             if reconnect_limit <= 0 or not loc:
                 return await _adecode_json(r)
+            _validate_reconnect_location(self.client.base_url, loc)
             try:
                 return await _adecode_json(r)
             except httpx.HTTPError:
@@ -242,6 +246,9 @@ async def stream(

                 reconnect_location = res.headers.get("location")
                 if reconnect_location:
+                    _validate_reconnect_location(
+                        self.client.base_url, reconnect_location
+                    )
                     reconnect_path = reconnect_location

                 # parse SSE
diff --git a/libs/sdk-py/langgraph_sdk/_shared/utilities.py b/libs/sdk-py/langgraph_sdk/_shared/utilities.py
index 4441bd255ed..c7b2583e2c7 100644
--- a/libs/sdk-py/langgraph_sdk/_shared/utilities.py
+++ b/libs/sdk-py/langgraph_sdk/_shared/utilities.py
@@ -8,6 +8,7 @@
 from collections.abc import Mapping
 from datetime import tzinfo
 from typing import TYPE_CHECKING, Any, cast
+from urllib.parse import urlparse

 import httpx

@@ -158,6 +159,40 @@ def _resolve_timezone(tz: str | tzinfo | ZoneInfo | None) -> str | None:
     )


+def _default_port(scheme: str) -> int:
+    return 443 if scheme == "https" else 80
+
+
+def _validate_reconnect_location(base_url: httpx.URL, location: str) -> str:
+    """Validate that a reconnect Location URL is same-origin as the base URL.
+
+    Raises ValueError if the Location header points to a different origin
+    (scheme + host + port), which would leak credentials to an external server.
+    """
+    parsed = urlparse(location)
+    # Relative URLs are safe — they resolve against the base
+    if not parsed.scheme and not parsed.netloc:
+        return location
+    # Compare origin components (normalize default ports to avoid mismatches)
+    base_scheme = str(base_url.scheme)
+    base_origin = (
+        base_scheme,
+        str(base_url.host),
+        base_url.port or _default_port(base_scheme),
+    )
+    loc_origin = (
+        parsed.scheme,
+        parsed.hostname or "",
+        parsed.port or _default_port(parsed.scheme),
+    )
+    if base_origin != loc_origin:
+        raise ValueError(
+            f"Refusing to follow cross-origin reconnect Location: {location!r} "
+            f"(origin {loc_origin}) does not match base URL origin {base_origin}"
+        )
+    return location
+
+
 def _provided_vals(d: Mapping[str, Any]) -> dict[str, Any]:
     return {k: v for k, v in d.items() if v is not None}

diff --git a/libs/sdk-py/langgraph_sdk/_sync/http.py b/libs/sdk-py/langgraph_sdk/_sync/http.py
index dccba518f04..ba56543be0c 100644
--- a/libs/sdk-py/langgraph_sdk/_sync/http.py
+++ b/libs/sdk-py/langgraph_sdk/_sync/http.py
@@ -11,7 +11,10 @@
 import httpx
 import orjson

-from langgraph_sdk._shared.utilities import _orjson_default
+from langgraph_sdk._shared.utilities import (
+    _orjson_default,
+    _validate_reconnect_location,
+)
 from langgraph_sdk.errors import _raise_for_status_typed
 from langgraph_sdk.schema import QueryParamTypes, StreamPart
 from langgraph_sdk.sse import SSEDecoder, iter_lines_raw
@@ -164,6 +167,7 @@ def request_reconnect(
             loc = r.headers.get("location")
             if reconnect_limit <= 0 or not loc:
                 return _decode_json(r)
+            _validate_reconnect_location(self.client.base_url, loc)
             try:
                 return _decode_json(r)
             except httpx.HTTPError:
@@ -244,6 +248,9 @@ def stream(

                 reconnect_location = res.headers.get("location")
                 if reconnect_location:
+                    _validate_reconnect_location(
+                        self.client.base_url, reconnect_location
+                    )
                     reconnect_path = reconnect_location

                 decoder = SSEDecoder()
PATCH

echo "Patch applied successfully"

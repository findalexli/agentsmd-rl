#!/bin/bash
# Gold solution for apache/airflow#64773
# Fix structlog positional formatting for single-dict arguments

set -e

cd /workspace/airflow

# Idempotency check - skip if already patched
if grep -q "def positional_arguments_formatter" shared/logging/src/airflow_shared/logging/structlog.py 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/shared/logging/src/airflow_shared/logging/structlog.py b/shared/logging/src/airflow_shared/logging/structlog.py
index 670f05ac8ad30..d5b0b9a8bfe43 100644
--- a/shared/logging/src/airflow_shared/logging/structlog.py
+++ b/shared/logging/src/airflow_shared/logging/structlog.py
@@ -95,10 +95,15 @@ def meth(self: Any, event: str, *args: Any, **kw: Any) -> Any:
             if not args:
                 return self._proxy_to_logger(name, event, **kw)

-            # See https://github.com/python/cpython/blob/3.13/Lib/logging/__init__.py#L307-L326 for reason
-            if args and len(args) == 1 and isinstance(args[0], Mapping) and args[0]:
-                return self._proxy_to_logger(name, event % args[0], **kw)
-            return self._proxy_to_logger(name, event % args, **kw)
+            # Match CPython's stdlib logging behavior: try positional formatting first,
+            # fall back to named substitution only if that fails.
+            # See https://github.com/python/cpython/blob/3.13/Lib/logging/__init__.py#L307-L326
+            try:
+                return self._proxy_to_logger(name, event % args, **kw)
+            except (TypeError, KeyError):
+                if len(args) == 1 and isinstance(args[0], Mapping) and args[0]:
+                    return self._proxy_to_logger(name, event % args[0], **kw)
+                raise

         meth.__name__ = name
         return meth
@@ -216,6 +221,30 @@ def drop_positional_args(logger: Any, method_name: Any, event_dict: EventDict) -
     return event_dict


+def positional_arguments_formatter(logger: Any, method_name: Any, event_dict: EventDict) -> EventDict:
+    """
+    Format positional arguments matching CPython's stdlib logging behavior.
+
+    Replaces structlog's built-in PositionalArgumentsFormatter to correctly handle the case
+    where a single dict is passed as a positional argument (e.g. ``log.warning('%s', {'a': 1})``).
+
+    CPython tries positional formatting first (``msg % args``), and only falls back to named
+    substitution (``msg % args[0]``) if that raises TypeError or KeyError. structlog's built-in
+    formatter does it the other way around, causing TypeError for ``%s`` format specifiers.
+    """
+    args = event_dict.get("positional_args")
+    if args:
+        try:
+            event_dict["event"] = event_dict["event"] % args
+        except (TypeError, KeyError):
+            if len(args) == 1 and isinstance(args[0], Mapping) and args[0]:
+                event_dict["event"] = event_dict["event"] % args[0]
+            else:
+                raise
+        del event_dict["positional_args"]
+    return event_dict
+
+
 # This is a placeholder fn, that is "edited" in place via the `suppress_logs_and_warning` decorator
 # The reason we need to do it this way is that structlog caches loggers on first use, and those include the
 # configured processors, so we can't get away with changing the config as it won't have any effect once the
@@ -268,7 +297,7 @@ def structlog_processors(
         timestamper,
         structlog.contextvars.merge_contextvars,
         structlog.processors.add_log_level,
-        structlog.stdlib.PositionalArgumentsFormatter(),
+        positional_arguments_formatter,
         logger_name,
         redact_jwt,
         structlog.processors.StackInfoRenderer(),
PATCH

echo "Patch applied successfully."

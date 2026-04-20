#!/bin/bash
set -e

cd /workspace/mlflow

# Apply the fix patch
git apply -v <<'ENDPATCH'
diff --git a/mlflow/tracing/utils/__init__.py b/mlflow/tracing/utils/__init__.py
index 622a0938b4fbc..6908b89e196e1 100644
--- a/mlflow/tracing/utils/__init__.py
+++ b/mlflow/tracing/utils/__init__.py
@@ -325,18 +325,10 @@ def calculate_cost_by_model_and_token_usage(
             # MLflow's logger is set to DEBUG level.
             litellm.suppress_debug_info = not _logger.isEnabledFor(logging.DEBUG)

-        result = cost_per_token(
-            model=model_name,
-            prompt_tokens=prompt_tokens,
-            completion_tokens=completion_tokens,
-            **cache_kwargs,
-        )
-    except Exception:
+        # When provider is known, try it first — this is a fast single-provider lookup
+        # and avoids the slower all-provider scan.
         result = None
         if model_provider:
-            # pass model_provider only in exception case to avoid invalid model_provider
-            # being used when model_name itself is enough to calculate cost, since model_provider
-            # field can be with any value and litellm may not support it.
             try:
                 result = cost_per_token(
                     model=model_name,
@@ -347,21 +339,23 @@ def calculate_cost_by_model_and_token_usage(
                 )
             except Exception:
                 pass
+
+        # Fallback: try without provider (for litellm this may match by model name alone,
+        # for builtin this scans bundled providers).
+        if result is None:
+            try:
+                result = cost_per_token(
+                    model=model_name,
+                    prompt_tokens=prompt_tokens,
+                    completion_tokens=completion_tokens,
+                    **cache_kwargs,
+                )
+            except Exception:
+                pass
     finally:
         if litellm is not None:
             litellm.suppress_debug_info = original_suppress

-    if result is None:
-        # Try with provider as a last resort (builtin path only, litellm already tried above)
-        if litellm is None and model_provider:
-            result = cost_per_token(
-                model=model_name,
-                prompt_tokens=prompt_tokens,
-                completion_tokens=completion_tokens,
-                custom_llm_provider=model_provider.lower(),
-                **cache_kwargs,
-            )
-
     if result is None:
         _logger.debug(f"Failed to calculate cost for model {model_name}")
         return None
diff --git a/mlflow/utils/providers.py b/mlflow/utils/providers.py
index 121e7f3ebac52..550cbe08af8fe 100644
--- a/mlflow/utils/providers.py
+++ b/mlflow/utils/providers.py
@@ -301,19 +301,17 @@ def _load_provider(provider: str) -> dict[str, ModelInfo]:


 def _lookup_model_info(model: str, custom_llm_provider: str | None = None) -> ModelInfo | None:
-    """Look up model cost info, loading only the relevant provider file when possible."""
+    """Look up model cost info, loading only the relevant provider file."""
     bare_model = model.split("/", 1)[-1]

     if custom_llm_provider:
-        # Fast path: load only the one provider file we need
-        if info := _load_provider(custom_llm_provider).get(bare_model):
-            return info
+        return _load_provider(custom_llm_provider).get(bare_model)

-    # Fallback: scan all providers for bare model name.
-    # Prefer entries that have pricing data over empty/stub entries.
+    # No provider given — scan bundled providers only (no remote fetch)
+    # to avoid O(N) network requests across all providers.
     fallback = None
     for provider in _list_provider_names():
-        if info := _load_provider(provider).get(bare_model):
+        if info := _load_bundled_provider(provider).get(bare_model):
             if info.get("input_cost_per_token"):
                 return info
             if fallback is None:
diff --git a/tests/utils/test_providers.py b/tests/utils/test_providers.py
index 6ececd91bd412..9764ccf8069ca 100644
--- a/tests/utils/test_providers.py
+++ b/tests/utils/test_providers.py
@@ -232,6 +232,9 @@ def mock_model_cost():
         mock.patch(
             "mlflow.utils.providers._load_provider", side_effect=_mock_load_provider
         ) as m_load,
+        mock.patch(
+            "mlflow.utils.providers._load_bundled_provider", side_effect=_mock_load_provider
+        ),
         mock.patch(
             "mlflow.utils.providers._list_provider_names",
             return_value=list(_MOCK_PROVIDER_DATA.keys()),
@@ -333,6 +336,10 @@ def test_cost_per_token_no_cache_cost_falls_back_to_input_rate():
             "mlflow.utils.providers._load_provider",
             side_effect=lambda p: no_cache_data.get(p, {}),
         ),
+        mock.patch(
+            "mlflow.utils.providers._load_bundled_provider",
+            side_effect=lambda p: no_cache_data.get(p, {}),
+        ),
         mock.patch(
             "mlflow.utils.providers._list_provider_names",
             return_value=list(no_cache_data.keys()),
ENDPATCH

# Verify the patch was applied by checking for the distinctive line
grep -q "_load_bundled_provider" mlflow/utils/providers.py
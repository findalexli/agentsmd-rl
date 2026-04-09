#!/usr/bin/env bash
set -euo pipefail

cd /workspace/beam

# Idempotent: skip if already applied
if grep -q '_invoke_route' sdks/python/apache_beam/ml/inference/vertex_ai_inference.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/sdks/python/apache_beam/ml/inference/vertex_ai_inference.py b/sdks/python/apache_beam/ml/inference/vertex_ai_inference.py
index 9858b59039c7..cd3d0beb593c 100644
--- a/sdks/python/apache_beam/ml/inference/vertex_ai_inference.py
+++ b/sdks/python/apache_beam/ml/inference/vertex_ai_inference.py
@@ -15,6 +15,7 @@
 # limitations under the License.
 #

+import json
 import logging
 from collections.abc import Iterable
 from collections.abc import Mapping
@@ -63,6 +64,7 @@ def __init__(
       experiment: Optional[str] = None,
       network: Optional[str] = None,
       private: bool = False,
+      invoke_route: Optional[str] = None,
       *,
       min_batch_size: Optional[int] = None,
       max_batch_size: Optional[int] = None,
@@ -95,6 +97,12 @@ def __init__(
       private: optional. if the deployed Vertex AI endpoint is
         private, set to true. Requires a network to be provided
         as well.
+      invoke_route: optional. the custom route path to use when invoking
+        endpoints with arbitrary prediction routes. When specified, uses
+        `Endpoint.invoke()` instead of `Endpoint.predict()`. The route
+        should start with a forward slash, e.g., "/predict/v1".
+        See https://cloud.google.com/vertex-ai/docs/predictions/use-arbitrary-custom-routes
+        for more information.
       min_batch_size: optional. the minimum batch size to use when batching
         inputs.
       max_batch_size: optional. the maximum batch size to use when batching
@@ -104,6 +112,7 @@ def __init__(
     """
     self._batching_kwargs = {}
     self._env_vars = kwargs.get('env_vars', {})
+    self._invoke_route = invoke_route
     if min_batch_size is not None:
       self._batching_kwargs["min_batch_size"] = min_batch_size
     if max_batch_size is not None:
@@ -203,9 +212,66 @@ def request(
     Returns:
       An iterable of Predictions.
     """
-    prediction = model.predict(instances=list(batch), parameters=inference_args)
-    return utils._convert_to_result(
-        batch, prediction.predictions, prediction.deployed_model_id)
+    if self._invoke_route:
+      # Use invoke() for endpoints with custom prediction routes
+      request_body: dict[str, Any] = {"instances": list(batch)}
+      if inference_args:
+        request_body["parameters"] = inference_args
+      response = model.invoke(
+          request_path=self._invoke_route,
+          body=json.dumps(request_body).encode("utf-8"),
+          headers={"Content-Type": "application/json"})
+      if hasattr(response, "content"):
+        return self._parse_invoke_response(batch, response.content)
+      return self._parse_invoke_response(batch, bytes(response))
+    else:
+      prediction = model.predict(
+          instances=list(batch), parameters=inference_args)
+      return utils._convert_to_result(
+          batch, prediction.predictions, prediction.deployed_model_id)
+
+  def _parse_invoke_response(self, batch: Sequence[Any],
+                             response: bytes) -> Iterable[PredictionResult]:
+    """Parses the response from Endpoint.invoke() into PredictionResults.
+
+    Args:
+      batch: the original batch of inputs.
+      response: the raw bytes response from invoke().
+
+    Returns:
+      An iterable of PredictionResults.
+    """
+    try:
+      response_json = json.loads(response.decode("utf-8"))
+    except (json.JSONDecodeError, UnicodeDecodeError) as e:
+      LOGGER.warning(
+          "Failed to decode invoke response as JSON, returning raw bytes: %s",
+          e)
+      # Return raw response for each batch item
+      return [
+          PredictionResult(example=example, inference=response)
+          for example in batch
+      ]
+
+    # Handle standard Vertex AI response format with "predictions" key
+    if isinstance(response_json, dict) and "predictions" in response_json:
+      predictions = response_json["predictions"]
+      model_id = response_json.get("deployedModelId")
+      return utils._convert_to_result(batch, predictions, model_id)
+
+    # Handle response as a list of predictions (one per input)
+    if isinstance(response_json, list) and len(response_json) == len(batch):
+      return utils._convert_to_result(batch, response_json, None)
+
+    # Handle single prediction response
+    if len(batch) == 1:
+      return [PredictionResult(example=batch[0], inference=response_json)]
+
+    # Fallback: return the full response for each batch item
+    return [
+        PredictionResult(example=example, inference=response_json)
+        for example in batch
+    ]

   def batch_elements_kwargs(self) -> Mapping[str, Any]:
     return self._batching_kwargs
diff --git a/sdks/python/apache_beam/yaml/yaml_ml.py b/sdks/python/apache_beam/yaml/yaml_ml.py
index e5a88f54eba7..4e750b79ce30 100644
--- a/sdks/python/apache_beam/yaml/yaml_ml.py
+++ b/sdks/python/apache_beam/yaml/yaml_ml.py
@@ -168,6 +168,7 @@ def __init__(
       experiment: Optional[str] = None,
       network: Optional[str] = None,
       private: bool = False,
+      invoke_route: Optional[str] = None,
       min_batch_size: Optional[int] = None,
       max_batch_size: Optional[int] = None,
       max_batch_duration_secs: Optional[int] = None):
@@ -236,6 +237,13 @@ def __init__(
       private: If the deployed Vertex AI endpoint is
         private, set to true. Requires a network to be provided
         as well.
+      invoke_route: The custom route path to use when invoking
+        endpoints with arbitrary prediction routes. When specified, uses
+        `Endpoint.invoke()` instead of `Endpoint.predict()`. The route
+        should start with a forward slash, e.g., "/predict/v1".
+        See
+        https://cloud.google.com/vertex-ai/docs/predictions/use-arbitrary-custom-routes
+        for more information.
       min_batch_size: The minimum batch size to use when batching
         inputs.
       max_batch_size: The maximum batch size to use when batching
@@ -258,6 +266,7 @@ def __init__(
         experiment=experiment,
         network=network,
         private=private,
+        invoke_route=invoke_route,
         min_batch_size=min_batch_size,
         max_batch_size=max_batch_size,
         max_batch_duration_secs=max_batch_duration_secs)

PATCH

echo "Patch applied successfully."

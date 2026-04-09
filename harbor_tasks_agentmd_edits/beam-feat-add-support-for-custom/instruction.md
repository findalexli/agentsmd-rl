# Add Support for Custom Prediction Routes in Vertex AI Inference

## Problem

The `VertexAIModelHandlerJSON` handler in Apache Beam's ML inference module only supports the standard `Endpoint.predict()` method for sending prediction requests. Users who have deployed Vertex AI endpoints with custom prediction routes (using `Endpoint.invoke()`) cannot use this handler. There is no way to specify an arbitrary prediction route path like `/predict/v1`.

## Expected Behavior

The handler should accept an optional `invoke_route` parameter. When provided:
1. The `request()` method should use `Endpoint.invoke()` instead of `Endpoint.predict()`, sending the batch as a JSON payload to the specified route
2. The invoke response (raw bytes) should be parsed correctly, handling various formats: standard predictions dict with `"predictions"` key, plain list, single prediction, and non-JSON responses
3. The same `invoke_route` parameter should be available through the YAML ML wrapper (`VertexAIRunInference` in `yaml_ml.py`)

## Files to Look At

- `sdks/python/apache_beam/ml/inference/vertex_ai_inference.py` — main model handler class (`VertexAIModelHandlerJSON`)
- `sdks/python/apache_beam/yaml/yaml_ml.py` — YAML ML wrapper (`VertexAIRunInference`) that exposes the handler for YAML pipelines

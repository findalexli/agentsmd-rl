"""
Task: beam-feat-add-support-for-custom
Repo: apache/beam @ be8dfed0530d9192454e410b7d5842651f35ffd6
PR:   37155

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
from pathlib import Path
import unittest.mock as mock

REPO = "/workspace/beam"

INFERENCE_FILE = f"{REPO}/sdks/python/apache_beam/ml/inference/vertex_ai_inference.py"
YAML_ML_FILE = f"{REPO}/sdks/python/apache_beam/yaml/yaml_ml.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified Python files must parse without errors."""
    for filepath in [INFERENCE_FILE, YAML_ML_FILE]:
        r = subprocess.run(
            [sys.executable, "-m", "py_compile", filepath],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"Syntax error in {filepath}: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_invoke_route_parameter_stored():
    """VertexAIModelHandlerJSON accepts and stores invoke_route parameter."""
    # Import from the repo
    sys.path.insert(0, f"{REPO}/sdks/python")
    try:
        from apache_beam.ml.inference.vertex_ai_inference import VertexAIModelHandlerJSON

        with mock.patch.object(VertexAIModelHandlerJSON, '_retrieve_endpoint', return_value=None):
            with mock.patch('google.cloud.aiplatform.init'):
                handler = VertexAIModelHandlerJSON(
                    endpoint_id="test-endpoint",
                    project="test-project",
                    location="us-central1",
                    invoke_route="/predict/v1"
                )

        assert hasattr(handler, '_invoke_route'), "Handler should have _invoke_route attribute"
        assert handler._invoke_route == "/predict/v1", f"Expected '/predict/v1', got {handler._invoke_route}"
    finally:
        sys.path.pop(0)


def test_parse_invoke_response_predictions_key():
    """_parse_invoke_response correctly parses standard Vertex AI response with 'predictions' key."""
    sys.path.insert(0, f"{REPO}/sdks/python")
    try:
        from apache_beam.ml.inference.vertex_ai_inference import VertexAIModelHandlerJSON

        with mock.patch.object(VertexAIModelHandlerJSON, '_retrieve_endpoint', return_value=None):
            with mock.patch('google.cloud.aiplatform.init'):
                handler = VertexAIModelHandlerJSON(
                    endpoint_id="test-endpoint",
                    project="test-project",
                    location="us-central1",
                    invoke_route="/predict"
                )

        batch = [{"input": "test1"}, {"input": "test2"}]
        response = b'{"predictions": ["result1", "result2"], "deployedModelId": "model123"}'

        results = list(handler._parse_invoke_response(batch, response))

        assert len(results) == 2, f"Expected 2 results, got {len(results)}"
        assert results[0].example == {"input": "test1"}
        assert results[0].inference == "result1"
        assert results[1].example == {"input": "test2"}
        assert results[1].inference == "result2"
    finally:
        sys.path.pop(0)


def test_parse_invoke_response_list_format():
    """_parse_invoke_response correctly parses response as a list of predictions."""
    sys.path.insert(0, f"{REPO}/sdks/python")
    try:
        from apache_beam.ml.inference.vertex_ai_inference import VertexAIModelHandlerJSON

        with mock.patch.object(VertexAIModelHandlerJSON, '_retrieve_endpoint', return_value=None):
            with mock.patch('google.cloud.aiplatform.init'):
                handler = VertexAIModelHandlerJSON(
                    endpoint_id="test-endpoint",
                    project="test-project",
                    location="us-central1",
                    invoke_route="/predict"
                )

        batch = [{"input": "a"}, {"input": "b"}]
        response = b'["output_a", "output_b"]'

        results = list(handler._parse_invoke_response(batch, response))

        assert len(results) == 2, f"Expected 2 results, got {len(results)}"
        assert results[0].inference == "output_a"
        assert results[1].inference == "output_b"
    finally:
        sys.path.pop(0)


def test_parse_invoke_response_single_prediction():
    """_parse_invoke_response correctly handles single prediction response."""
    sys.path.insert(0, f"{REPO}/sdks/python")
    try:
        from apache_beam.ml.inference.vertex_ai_inference import VertexAIModelHandlerJSON

        with mock.patch.object(VertexAIModelHandlerJSON, '_retrieve_endpoint', return_value=None):
            with mock.patch('google.cloud.aiplatform.init'):
                handler = VertexAIModelHandlerJSON(
                    endpoint_id="test-endpoint",
                    project="test-project",
                    location="us-central1",
                    invoke_route="/predict"
                )

        batch = [{"input": "single"}]
        response = b'{"output": "single_result"}'

        results = list(handler._parse_invoke_response(batch, response))

        assert len(results) == 1, f"Expected 1 result, got {len(results)}"
        assert results[0].example == {"input": "single"}
        assert results[0].inference == {"output": "single_result"}
    finally:
        sys.path.pop(0)


def test_parse_invoke_response_non_json():
    """_parse_invoke_response correctly handles non-JSON response by returning raw bytes."""
    sys.path.insert(0, f"{REPO}/sdks/python")
    try:
        from apache_beam.ml.inference.vertex_ai_inference import VertexAIModelHandlerJSON

        with mock.patch.object(VertexAIModelHandlerJSON, '_retrieve_endpoint', return_value=None):
            with mock.patch('google.cloud.aiplatform.init'):
                handler = VertexAIModelHandlerJSON(
                    endpoint_id="test-endpoint",
                    project="test-project",
                    location="us-central1",
                    invoke_route="/predict"
                )

        batch = [{"input": "test"}]
        response = b'not valid json data'

        results = list(handler._parse_invoke_response(batch, response))

        assert len(results) == 1, f"Expected 1 result, got {len(results)}"
        assert results[0].example == {"input": "test"}
        assert results[0].inference == response, "Should return raw bytes for non-JSON response"
    finally:
        sys.path.pop(0)


def test_yaml_wrapper_accepts_invoke_route():
    """VertexAIRunInference YAML wrapper accepts and passes invoke_route parameter."""
    sys.path.insert(0, f"{REPO}/sdks/python")
    try:
        from apache_beam.yaml.yaml_ml import VertexAIRunInference
        import inspect

        # Check that invoke_route is in the __init__ signature
        sig = inspect.signature(VertexAIRunInference.__init__)
        assert "invoke_route" in sig.parameters, "VertexAIRunInference should accept invoke_route parameter"
    finally:
        sys.path.pop(0)


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

def test_existing_unit_tests_pass():
    """Upstream unit tests for vertex_ai_inference still pass."""
    r = subprocess.run(
        [sys.executable, "-m", "pytest",
         f"{REPO}/sdks/python/apache_beam/ml/inference/vertex_ai_inference_test.py",
         "-v", "--timeout=60"],
        cwd=f"{REPO}/sdks/python",
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Upstream unit tests failed:\n{r.stdout}\n{r.stderr}"


def test_handler_not_stub():
    """VertexAIModelHandlerJSON has real logic, not just pass/return."""
    import ast

    src = Path(INFERENCE_FILE).read_text()
    tree = ast.parse(src)

    found_init = False
    found_parse_invoke = False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            if node.name == "__init__":
                # Check for meaningful statements (not just Pass or docstring Expr)
                stmts = [s for s in node.body if not isinstance(s, (ast.Pass, ast.Expr))]
                if len(stmts) > 1:
                    found_init = True
            if node.name == "_parse_invoke_response":
                # This is the new method, it should exist and have real logic
                stmts = [s for s in node.body if not isinstance(s, (ast.Pass, ast.Expr))]
                if len(stmts) > 5:  # The parse method has substantial logic
                    found_parse_invoke = True

    assert found_init, "VertexAIModelHandlerJSON.__init__ should have meaningful body"
    assert found_parse_invoke, "VertexAIModelHandlerJSON._parse_invoke_response should exist with real logic"

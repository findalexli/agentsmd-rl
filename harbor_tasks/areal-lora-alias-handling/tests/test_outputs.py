"""
Task: areal-lora-alias-handling
Repo: inclusionAI/AReaL @ 02a25454bc8ff348b05ae2a62040d5ec48237e16
PR:   1039

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import textwrap
from pathlib import Path
from unittest.mock import MagicMock

REPO = "/workspace/AReaL"
TARGET = f"{REPO}/areal/engine/vllm_ext/areal_vllm_server.py"


def _read_source():
    return Path(TARGET).read_text()


def _extract_function_source(source, func_name):
    """Extract a function's source code by exact name."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
            lines = source.splitlines(keepends=True)
            return "".join(lines[node.lineno - 1 : node.end_lineno])
    return None


def _find_lora_helper(source, keywords):
    """Find a helper function whose name contains 'lora' and any of the keywords."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name_lower = node.name.lower()
            if "lora" in name_lower and any(kw in name_lower for kw in keywords):
                lines = source.splitlines(keepends=True)
                return node.name, "".join(lines[node.lineno - 1 : node.end_lineno])
    return None, None


def _make_lora_request(lora_name, lora_int_id, lora_path="", base_model_name=None):
    """Create a mock LoRARequest with the expected attributes."""
    req = MagicMock()
    req.lora_name = lora_name
    req.lora_int_id = lora_int_id
    req.lora_path = lora_path
    req.base_model_name = base_model_name
    return req


def _build_exec_namespace():
    """Build a namespace with mocked dependencies for executing extracted functions."""

    class FakeLoRARequest:
        def __init__(self, lora_name, lora_int_id, lora_path="", **kwargs):
            self.lora_name = lora_name
            self.lora_int_id = lora_int_id
            self.lora_path = lora_path
            self.base_model_name = kwargs.get("base_model_name")

    logger = MagicMock()
    ns = {"LoRARequest": FakeLoRARequest, "logger": logger, "getattr": getattr}
    return ns, FakeLoRARequest


def _load_register_helper(ns, source):
    """Find and exec the LoRA registration helper + its path-inference dependency."""
    # Try exact names first, then fuzzy match
    reg_src = _extract_function_source(source, "_register_runtime_lora_name")
    if reg_src is None:
        _, reg_src = _find_lora_helper(source, ["register", "alias", "update_name"])
    assert reg_src is not None, (
        "No LoRA registration helper found. Expected a function with 'lora' and "
        "'register'/'alias' in its name that creates new LoRARequest entries."
    )

    infer_src = _extract_function_source(source, "_infer_runtime_lora_path")
    if infer_src is None:
        _, infer_src = _find_lora_helper(source, ["infer", "path", "resolve"])

    # The register helper may call the path helper — exec both if found
    if infer_src is not None:
        exec(textwrap.dedent(infer_src), ns)
    exec(textwrap.dedent(reg_src), ns)

    # Return the callable register function
    for key, val in ns.items():
        if callable(val) and "lora" in key.lower() and any(
            kw in key.lower() for kw in ["register", "alias", "update_name"]
        ):
            return val
    return None


def _load_infer_helper(ns, source):
    """Find and exec the LoRA path inference helper."""
    infer_src = _extract_function_source(source, "_infer_runtime_lora_path")
    if infer_src is None:
        _, infer_src = _find_lora_helper(source, ["infer", "path", "resolve"])
    assert infer_src is not None, (
        "No LoRA path inference helper found. Expected a function with 'lora' and "
        "'infer'/'path'/'resolve' in its name."
    )
    exec(textwrap.dedent(infer_src), ns)
    for key, val in ns.items():
        if callable(val) and "lora" in key.lower() and any(
            kw in key.lower() for kw in ["infer", "path", "resolve"]
        ):
            return val
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """Target file must parse without syntax errors."""
    import py_compile

    py_compile.compile(TARGET, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_register_helper_creates_lora_request():
    """A dedicated helper creates a new LoRARequest in the registry."""
    source = _read_source()
    ns, FakeLoRARequest = _build_exec_namespace()
    register_fn = _load_register_helper(ns, source)
    assert register_fn is not None

    test_cases = [
        ("adapter-v1", 42, None),
        ("my-lora-adapter", 1, None),
        ("xccl-runtime-3", 999, "base-model-7b"),
    ]
    for name, int_id, base_model in test_cases:
        app = MagicMock()
        app.state.openai_serving_models.lora_requests = {}

        register_fn(app, lora_name=name, lora_int_id=int_id, base_model_name=base_model)

        registry = app.state.openai_serving_models.lora_requests
        assert name in registry, f"{name} not registered"
        req = registry[name]
        assert isinstance(req, FakeLoRARequest), f"Registry entry for {name} is not a new LoRARequest"
        assert req.lora_int_id == int_id, f"Expected int_id {int_id}, got {req.lora_int_id}"
        assert req.lora_name == name, f"Expected name {name}, got {req.lora_name}"


# [pr_diff] fail_to_pass
def test_stale_aliases_removed():
    """Registering a new name for the same adapter id removes old aliases."""
    source = _read_source()
    ns, _ = _build_exec_namespace()
    register_fn = _load_register_helper(ns, source)
    assert register_fn is not None

    # Scenario 1: two stale entries for adapter id 7
    app = MagicMock()
    app.state.openai_serving_models.lora_requests = {
        "old-name-a": _make_lora_request("old-name-a", 7, "/path/a"),
        "old-name-b": _make_lora_request("old-name-b", 7, "/path/b"),
        "unrelated": _make_lora_request("unrelated", 99, "/path/other"),
    }

    register_fn(app, lora_name="new-name", lora_int_id=7, base_model_name=None)

    registry = app.state.openai_serving_models.lora_requests
    assert "old-name-a" not in registry, "Stale alias old-name-a should be removed"
    assert "old-name-b" not in registry, "Stale alias old-name-b should be removed"
    assert "new-name" in registry, "New name should be registered"
    assert "unrelated" in registry, "Unrelated adapter should not be affected"

    # Scenario 2: single stale entry for adapter id 50
    app2 = MagicMock()
    app2.state.openai_serving_models.lora_requests = {
        "stale-50": _make_lora_request("stale-50", 50, "/p"),
        "keep-me": _make_lora_request("keep-me", 11, "/q"),
    }

    register_fn(app2, lora_name="fresh-50", lora_int_id=50, base_model_name=None)

    registry2 = app2.state.openai_serving_models.lora_requests
    assert "stale-50" not in registry2
    assert "fresh-50" in registry2
    assert "keep-me" in registry2


# [pr_diff] fail_to_pass
def test_infer_path_synthetic_fallback():
    """Path inference returns xccl:// synthetic path when no existing path."""
    source = _read_source()
    ns, _ = _build_exec_namespace()
    infer_fn = _load_infer_helper(ns, source)
    assert infer_fn is not None

    serving_models = MagicMock()
    serving_models.lora_requests = {}  # empty registry

    for name, int_id in [("adapter-v1", 99), ("my-lora", 1), ("test_adapter", 500)]:
        result = infer_fn(serving_models, name, int_id)
        assert "xccl://" in result, f"Expected xccl:// fallback path, got: {result}"
        assert name in result, f"Expected adapter name '{name}' in path, got: {result}"


# [pr_diff] fail_to_pass
def test_infer_path_preserves_existing():
    """Path inference returns existing path from registry when available."""
    source = _read_source()
    ns, _ = _build_exec_namespace()
    infer_fn = _load_infer_helper(ns, source)
    assert infer_fn is not None

    # Case 1: exact name match has path
    existing = _make_lora_request("adapter-v1", 42, "/models/lora/adapter-v1")
    serving = MagicMock()
    serving.lora_requests = {"adapter-v1": existing}

    result = infer_fn(serving, "adapter-v1", 42)
    assert result == "/models/lora/adapter-v1", f"Expected existing path, got: {result}"

    # Case 2: same adapter id under different name has path
    old_entry = _make_lora_request("old-name", 42, "/models/lora/old")
    serving2 = MagicMock()
    serving2.lora_requests = {"old-name": old_entry}

    result2 = infer_fn(serving2, "new-name", 42)
    assert result2 == "/models/lora/old", f"Expected path from same adapter id, got: {result2}"

    # Case 3: entry exists but lora_path is empty -> should fall back to xccl://
    empty_path = _make_lora_request("no-path", 88, "")
    serving3 = MagicMock()
    serving3.lora_requests = {"no-path": empty_path}

    result3 = infer_fn(serving3, "no-path", 88)
    assert "xccl://" in result3, f"Expected xccl:// fallback for empty path, got: {result3}"


# [pr_diff] fail_to_pass
def test_success_gating():
    """Registry update in update_weight_lora_xccl is gated on all XCCL operations succeeding."""
    # AST-only because: update_weight_lora_xccl is an async FastAPI endpoint requiring
    # a running vLLM engine, CUDA, and distributed runtime — cannot be called in test
    source = _read_source()
    tree = ast.parse(source)

    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == "update_weight_lora_xccl":
                func_node = node
                break

    assert func_node is not None, "update_weight_lora_xccl function not found"

    func_lines = source.splitlines()[func_node.lineno - 1 : func_node.end_lineno]
    func_src = "\n".join(func_lines)

    # The fix must NOT do inline mutation (old pattern: req.lora_name = new_name)
    assert "req.lora_name = " not in func_src and ".lora_name = new_name" not in func_src, (
        "Old mutation pattern (req.lora_name = ...) still present — should use dedicated helper"
    )

    # Must create new LoRARequest or delegate to a helper (not mutate inline)
    has_new_request = "LoRARequest(" in func_src
    # Check for any call to a helper with lora/register in name
    has_helper_call = bool(re.search(r"_?\w*(?:register|lora_name)\w*\(", func_src))

    assert has_helper_call or has_new_request, (
        "update_weight_lora_xccl should use a registration helper or create new LoRARequest"
    )

    # Registry update must be conditional on success
    has_success_gate = "all(" in func_src or bool(
        re.search(r"if\s+.*(?:success|ret_list|result)", func_src)
    )
    assert has_success_gate, (
        "Registry update should be gated on XCCL success (expected 'all(...)' or success check)"
    )


# [pr_diff] fail_to_pass
def test_base_model_name_propagated():
    """Registration helper propagates base_model_name to the LoRARequest."""
    source = _read_source()
    ns, FakeLoRARequest = _build_exec_namespace()
    register_fn = _load_register_helper(ns, source)
    assert register_fn is not None

    for base_name in ["llama-7b", "qwen-14b", None]:
        app = MagicMock()
        app.state.openai_serving_models.lora_requests = {}

        register_fn(app, lora_name="adapter-x", lora_int_id=10, base_model_name=base_name)

        req = app.state.openai_serving_models.lora_requests["adapter-x"]
        assert req.base_model_name == base_name, (
            f"Expected base_model_name={base_name}, got {req.base_model_name}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_not_stub():
    """File retains original logic and expected symbols."""
    source = _read_source()
    required = [
        "update_weight_lora_xccl",
        "build_response",
        "router",
        "UpdateWeightsFromXcclRequestLora",
        "engine_core",
        "call_utility_async",
        "lora_name",
        "lora_int_id",
    ]
    missing = [r for r in required if r not in source]
    assert not missing, f"File is missing expected symbols: {missing}"

    line_count = len(source.splitlines())
    assert line_count >= 200, f"File has only {line_count} lines — looks like a stub"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — AGENTS.md:30 @ 02a25454bc8ff348b05ae2a62040d5ec48237e16
def test_no_wildcard_imports():
    """No wildcard imports (from x import *)."""
    source = _read_source()
    wildcard_lines = [
        (i + 1, line)
        for i, line in enumerate(source.splitlines())
        if re.match(r"\s*from\s+\S+\s+import\s+\*", line)
    ]
    assert not wildcard_lines, f"Wildcard imports found: {wildcard_lines}"


# [agent_config] pass_to_pass — AGENTS.md:89-91 @ 02a25454bc8ff348b05ae2a62040d5ec48237e16
def test_no_bare_print():
    """No bare print() calls in production code (use logger instead)."""
    source = _read_source()
    bare_prints = [
        (i + 1, line.strip())
        for i, line in enumerate(source.splitlines())
        if re.match(r"\s*print\(", line)
    ]
    assert not bare_prints, f"Bare print() calls found: {bare_prints}"

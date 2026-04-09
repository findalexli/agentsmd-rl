"""Tests for sgl-project/sglang#22174 — UX: clean loggings

Verifies:
1. SGLangORJSONResponse extends Response (not deprecated ORJSONResponse)
2. orjson_response() returns SGLangORJSONResponse instances with correct status codes
3. flash_attn.cute.cache_utils is in suppressed loggers
4. Correct kwarg name 'inputs_embeds' in mistral_3.py and qwen2_5vl.py
"""

import importlib.util
import os
import subprocess
import shutil

REPO = "/workspace/sglang"

# Modified files in this PR (for pass_to_pass repo tests)
MODIFIED_FILES = [
    "python/sglang/srt/utils/json_response.py",
    "python/sglang/multimodal_gen/runtime/utils/logging_utils.py",
    "python/sglang/multimodal_gen/runtime/models/encoders/mistral_3.py",
    "python/sglang/multimodal_gen/runtime/models/encoders/qwen2_5vl.py",
]


def _ensure_tool(tool, package=None):
    """Ensure a CLI tool is available, installing if necessary."""
    if package is None:
        package = tool
    if shutil.which(tool) is None:
        subprocess.run(
            ["pip", "install", "--no-cache-dir", "-q", package],
            check=True,
            capture_output=True,
        )


def _import_json_response():
    """Import json_response.py directly to avoid heavy package __init__ chains."""
    spec = importlib.util.spec_from_file_location(
        "json_response",
        os.path.join(REPO, "python/sglang/srt/utils/json_response.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── json_response: fail-to-pass ──────────────────────────────────────────────


def test_sglang_response_extends_response():
    """SGLangORJSONResponse must extend Response, not deprecated ORJSONResponse."""
    mod = _import_json_response()
    from fastapi.responses import ORJSONResponse, Response

    assert issubclass(mod.SGLangORJSONResponse, Response), (
        "SGLangORJSONResponse must be a subclass of Response"
    )
    assert not issubclass(mod.SGLangORJSONResponse, ORJSONResponse), (
        "SGLangORJSONResponse must NOT extend the deprecated ORJSONResponse"
    )


def test_orjson_response_returns_sglang_class():
    """orjson_response() must return SGLangORJSONResponse, not plain Response."""
    mod = _import_json_response()

    for data in [{"key": "value"}, [1, 2, 3], "hello", 42, True]:
        result = mod.orjson_response(data)
        assert isinstance(result, mod.SGLangORJSONResponse), (
            f"Expected SGLangORJSONResponse for input {data!r}, got {type(result).__name__}"
        )


def test_orjson_response_status_code_varied():
    """orjson_response() must set the correct status code for various codes."""
    mod = _import_json_response()

    for code in [200, 201, 400, 404, 500]:
        result = mod.orjson_response({"data": code}, status_code=code)
        assert isinstance(result, mod.SGLangORJSONResponse)
        assert result.status_code == code, (
            f"Expected status_code={code}, got {result.status_code}"
        )


# ── logging_utils: fail-to-pass ──────────────────────────────────────────────


def test_flash_attn_logger_suppressed():
    """flash_attn.cute.cache_utils must be in globally suppressed loggers."""
    path = os.path.join(
        REPO, "python/sglang/multimodal_gen/runtime/utils/logging_utils.py"
    )
    with open(path) as f:
        content = f.read()

    assert '"flash_attn.cute.cache_utils"' in content, (
        "flash_attn.cute.cache_utils must be added to the suppressed loggers list"
    )


# ── encoder kwarg fixes: fail-to-pass ────────────────────────────────────────


def test_mistral3_correct_kwarg_name():
    """mistral_3.py must use 'inputs_embeds' kwarg (not 'input_embeds')."""
    path = os.path.join(
        REPO, "python/sglang/multimodal_gen/runtime/models/encoders/mistral_3.py"
    )
    with open(path) as f:
        content = f.read()

    assert "inputs_embeds=inputs_embeds" in content, (
        "mistral_3.py must pass 'inputs_embeds' (not 'input_embeds') to create_causal_mask"
    )
    assert "input_embeds=inputs_embeds" not in content, (
        "mistral_3.py must not use the wrong kwarg name 'input_embeds'"
    )


def test_qwen2_correct_kwarg_name():
    """qwen2_5vl.py mask_kwargs must use 'inputs_embeds' key (not 'input_embeds')."""
    path = os.path.join(
        REPO, "python/sglang/multimodal_gen/runtime/models/encoders/qwen2_5vl.py"
    )
    with open(path) as f:
        content = f.read()

    assert '"inputs_embeds": inputs_embeds' in content, (
        "qwen2_5vl.py mask_kwargs must contain 'inputs_embeds' key"
    )
    assert '"input_embeds": inputs_embeds' not in content, (
        "qwen2_5vl.py mask_kwargs must not contain the wrong 'input_embeds' key"
    )


# ── pass-to-pass: json_response behavior preserved ───────────────────────────


def test_sglang_response_render_json():
    """SGLangORJSONResponse.render() must produce valid orjson-serialized bytes."""
    import orjson

    mod = _import_json_response()

    for data in [{"a": 1, "b": 2}, [10, 20], "test"]:
        resp = mod.SGLangORJSONResponse(content=data)
        body = resp.render(data)
        assert orjson.loads(body) == data, (
            f"render() output mismatch: expected {data}, got {orjson.loads(body)}"
        )


def test_dumps_json_roundtrip():
    """dumps_json must produce bytes that roundtrip through orjson."""
    import orjson

    mod = _import_json_response()

    for data in [{"x": 1}, [1, 2, 3], "hello", 42, True, None]:
        encoded = mod.dumps_json(data)
        assert isinstance(encoded, bytes)
        assert orjson.loads(encoded) == data


# ── pass-to-pass: repo CI/CD checks ──────────────────────────────────────────


def test_repo_ruff_linting():
    """Repo's ruff linting passes on modified files (pass_to_pass)."""
    _ensure_tool("ruff")
    files = [os.path.join(REPO, f) for f in MODIFIED_FILES]
    r = subprocess.run(
        ["ruff", "check", "--select=F401,F821"] + files,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff linting failed:\n{r.stdout}\n{r.stderr}"


def test_repo_black_formatting():
    """Repo's black formatting check passes on modified files (pass_to_pass)."""
    _ensure_tool("black")
    files = [os.path.join(REPO, f) for f in MODIFIED_FILES]
    r = subprocess.run(
        ["black", "--check"] + files,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Black formatting check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_isort_check():
    """Repo's isort import ordering check passes on modified files (pass_to_pass)."""
    _ensure_tool("isort")
    files = [os.path.join(REPO, f) for f in MODIFIED_FILES]
    r = subprocess.run(
        ["isort", "--check-only"] + files,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Isort check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_codespell():
    """Repo's codespell check passes on modified files (pass_to_pass)."""
    _ensure_tool("codespell")
    files = [os.path.join(REPO, f) for f in MODIFIED_FILES]
    r = subprocess.run(
        ["codespell", "--config", ".codespellrc"] + files,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Codespell check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_python_syntax():
    """Modified Python files have valid syntax (pass_to_pass)."""
    files = [os.path.join(REPO, f) for f in MODIFIED_FILES]
    for f in files:
        r = subprocess.run(
            ["python3", "-m", "py_compile", f],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Python syntax error in {f}:\n{r.stderr}"

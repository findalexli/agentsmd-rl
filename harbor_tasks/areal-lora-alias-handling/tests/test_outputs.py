"""
Task: areal-lora-alias-handling
Repo: inclusionAI/AReaL @ 02a25454bc8ff348b05ae2a62040d5ec48237e16
PR:   1039

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import subprocess
import textwrap
from pathlib import Path
from unittest.mock import MagicMock

REPO = "/workspace/AReaL"
TARGET = f"{REPO}/areal/engine/vllm_ext/areal_vllm_server.py"


def _read_source():
    return Path(TARGET).read_text()


# ---------------------------------------------------------------------------
# Subprocess helpers for behavioral tests
# ---------------------------------------------------------------------------

_PREAMBLE = '''
import ast, textwrap
from pathlib import Path
from unittest.mock import MagicMock

SOURCE = Path("%s").read_text()

class FakeLoRARequest:
    def __init__(self, lora_name, lora_int_id, lora_path="", **kwargs):
        self.lora_name = lora_name
        self.lora_int_id = lora_int_id
        self.lora_path = lora_path
        self.base_model_name = kwargs.get("base_model_name")

logger = MagicMock()
NS = {"LoRARequest": FakeLoRARequest, "logger": logger, "getattr": getattr}

def _extract_func(name):
    tree = ast.parse(SOURCE)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            lines = SOURCE.splitlines(keepends=True)
            return "".join(lines[node.lineno - 1 : node.end_lineno])
    return None

infer_src = _extract_func("_infer_runtime_lora_path")
reg_src = _extract_func("_register_runtime_lora_name")
if infer_src:
    exec(textwrap.dedent(infer_src), NS)
if reg_src:
    exec(textwrap.dedent(reg_src), NS)

register_fn = None
infer_fn = None
for k, v in NS.items():
    if callable(v):
        kl = k.lower()
        if "register" in kl and "lora" in kl:
            register_fn = v
        if ("infer" in kl or "path" in kl) and "lora" in kl:
            infer_fn = v

def _make_req(lora_name, lora_int_id, lora_path="", base_model_name=None):
    req = MagicMock()
    req.lora_name = lora_name
    req.lora_int_id = lora_int_id
    req.lora_path = lora_path
    req.base_model_name = base_model_name
    return req

''' % TARGET


def _run_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code via subprocess with mocked vLLM deps."""
    script = Path(REPO) / "_eval_tmp.py"
    try:
        script.write_text(_PREAMBLE + code)
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """Target file must parse without syntax errors."""
    import py_compile

    py_compile.compile(TARGET, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests using subprocess
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_register_helper_creates_lora_request():
    """A dedicated helper creates a new LoRARequest in the registry."""
    r = _run_python("""
assert register_fn is not None, "No LoRA registration helper found"

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
    assert isinstance(req, FakeLoRARequest), f"Not a new LoRARequest: {type(req)}"
    assert req.lora_int_id == int_id
    assert req.lora_name == name

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_stale_aliases_removed():
    """Registering a new name for the same adapter id removes old aliases."""
    r = _run_python("""
assert register_fn is not None

# Scenario 1: two stale entries for adapter id 7
app = MagicMock()
app.state.openai_serving_models.lora_requests = {
    "old-name-a": _make_req("old-name-a", 7, "/path/a"),
    "old-name-b": _make_req("old-name-b", 7, "/path/b"),
    "unrelated": _make_req("unrelated", 99, "/path/other"),
}

register_fn(app, lora_name="new-name", lora_int_id=7, base_model_name=None)

registry = app.state.openai_serving_models.lora_requests
assert "old-name-a" not in registry, "Stale alias old-name-a should be removed"
assert "old-name-b" not in registry, "Stale alias old-name-b should be removed"
assert "new-name" in registry
assert "unrelated" in registry, "Unrelated adapter should not be affected"

# Scenario 2: single stale entry for adapter id 50
app2 = MagicMock()
app2.state.openai_serving_models.lora_requests = {
    "stale-50": _make_req("stale-50", 50, "/p"),
    "keep-me": _make_req("keep-me", 11, "/q"),
}

register_fn(app2, lora_name="fresh-50", lora_int_id=50, base_model_name=None)

registry2 = app2.state.openai_serving_models.lora_requests
assert "stale-50" not in registry2
assert "fresh-50" in registry2
assert "keep-me" in registry2

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_infer_path_synthetic_fallback():
    """Path inference returns xccl:// synthetic path when no existing path."""
    r = _run_python("""
assert infer_fn is not None, "No LoRA path inference helper found"

serving_models = MagicMock()
serving_models.lora_requests = {}

for name, int_id in [("adapter-v1", 99), ("my-lora", 1), ("test_adapter", 500)]:
    result = infer_fn(serving_models, name, int_id)
    assert "xccl://" in result, f"Expected xccl:// fallback, got: {result}"
    assert name in result, f"Expected name '{name}' in path, got: {result}"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_infer_path_preserves_existing():
    """Path inference returns existing path from registry when available."""
    r = _run_python("""
assert infer_fn is not None

# Case 1: exact name match has path
existing = _make_req("adapter-v1", 42, "/models/lora/adapter-v1")
serving = MagicMock()
serving.lora_requests = {"adapter-v1": existing}

result = infer_fn(serving, "adapter-v1", 42)
assert result == "/models/lora/adapter-v1", f"Expected existing path, got: {result}"

# Case 2: same adapter id under different name has path
old_entry = _make_req("old-name", 42, "/models/lora/old")
serving2 = MagicMock()
serving2.lora_requests = {"old-name": old_entry}

result2 = infer_fn(serving2, "new-name", 42)
assert result2 == "/models/lora/old", f"Expected path from same id, got: {result2}"

# Case 3: entry exists but lora_path is empty -> falls back to xccl://
empty_path = _make_req("no-path", 88, "")
serving3 = MagicMock()
serving3.lora_requests = {"no-path": empty_path}

result3 = infer_fn(serving3, "no-path", 88)
assert "xccl://" in result3, f"Expected xccl:// fallback, got: {result3}"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_success_gating():
    """Registry update in update_weight_lora_xccl is gated on XCCL success."""
    # AST-only: update_weight_lora_xccl is async FastAPI requiring vLLM engine + CUDA
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

    # Must NOT do inline mutation (old pattern: req.lora_name = new_name)
    assert "req.lora_name = " not in func_src and ".lora_name = new_name" not in func_src, (
        "Old mutation pattern still present — should use dedicated helper"
    )

    # Must delegate to a helper or create new LoRARequest
    has_new_request = "LoRARequest(" in func_src
    has_helper_call = bool(re.search(r"_?\w*(?:register|lora_name)\w*\(", func_src))
    assert has_helper_call or has_new_request, (
        "Should use a registration helper or create new LoRARequest"
    )

    # Registry update must be conditional on success
    has_success_gate = "all(" in func_src or bool(
        re.search(r"if\s+.*(?:success|ret_list|result)", func_src)
    )
    assert has_success_gate, (
        "Registry update should be gated on XCCL success"
    )


# [pr_diff] fail_to_pass
def test_base_model_name_propagated():
    """Registration helper propagates base_model_name to the LoRARequest."""
    r = _run_python("""
assert register_fn is not None

for base_name in ["llama-7b", "qwen-14b", None]:
    app = MagicMock()
    app.state.openai_serving_models.lora_requests = {}

    register_fn(app, lora_name="adapter-x", lora_int_id=10, base_model_name=base_name)

    req = app.state.openai_serving_models.lora_requests["adapter-x"]
    assert req.base_model_name == base_name, (
        f"Expected base_model_name={base_name}, got {req.base_model_name}"
    )

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


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


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates
# ---------------------------------------------------------------------------


def test_repo_ruff_check():
    """Repo's Ruff linting passes on target file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["ruff", "check", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format():
    """Repo's Ruff formatting check passes on target file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["ruff", "format", "--check", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_precommit_yaml():
    """Repo's YAML files pass pre-commit check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["pre-commit", "run", "check-yaml", "--all-files"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit YAML check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_precommit_eof():
    """Repo's files pass end-of-file-fixer pre-commit check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["pre-commit", "run", "end-of-file-fixer", "--all-files"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit EOF check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_precommit_whitespace():
    """Repo's files pass trailing-whitespace pre-commit check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["pre-commit", "run", "trailing-whitespace", "--all-files"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Pre-commit whitespace check failed:\n{r.stdout}\n{r.stderr}"

"""
Task: prime-rl-qwen35-vlm-text-dispatch
Repo: PrimeIntellect-ai/prime-rl @ ecd080928014e20d1927a4f8b0b01d399151fdba
PR:   2098

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import functools
import importlib.util
import subprocess
from pathlib import Path

REPO = "/repo"
MODEL_PY = f"{REPO}/src/prime_rl/trainer/model.py"
VLM_PY = f"{REPO}/src/prime_rl/utils/vlm.py"


@functools.lru_cache(maxsize=1)
def _load_vlm_module():
    spec = importlib.util.spec_from_file_location("vlm", VLM_PY)
    vlm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vlm)
    return vlm


class _MockConfig:
    def __init__(self, model_type):
        self.model_type = model_type


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    for path in [VLM_PY, MODEL_PY]:
        source = Path(path).read_text()
        compile(source, path, "exec")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_is_vlm_architecture_classifies_configs():
    """is_vlm_architecture returns True for VLM types, False for text-only types."""
    r = subprocess.run(
        ["python3", "-c", """
from prime_rl.utils.vlm import is_vlm_architecture

class MockConfig:
    def __init__(self, model_type):
        self.model_type = model_type

# VLM architectures in registry must return True
for mt in ["qwen3_5_moe", "qwen3_5", "qwen3_vl"]:
    assert is_vlm_architecture(MockConfig(mt)) is True, f"{mt} should be VLM"

# Non-VLM model types must return False
for mt in ["llama", "gpt2", "mistral", "gemma", "phi"]:
    assert is_vlm_architecture(MockConfig(mt)) is False, f"{mt} should not be VLM"

# Edge cases
assert is_vlm_architecture(MockConfig(None)) is False, "None model_type"
assert is_vlm_architecture(MockConfig("")) is False, "empty model_type"
assert is_vlm_architecture(MockConfig("nonexistent_model_999")) is False

print("PASS")
"""],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_get_model_uses_architecture_detection():
    """get_model() must call is_vlm_architecture() for model class dispatch.

    # AST-only because: get_model requires GPU, model weights, FSDP, and the
    # full prime_rl training stack — cannot be invoked on CPU.
    """
    source = Path(MODEL_PY).read_text()
    tree = ast.parse(source)

    get_model = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_model":
            get_model = node
            break
    assert get_model is not None, "get_model function not found"

    calls_fn = False
    for node in ast.walk(get_model):
        if isinstance(node, ast.Call):
            func = node.func
            name = getattr(func, "id", None) or getattr(func, "attr", None)
            if name == "is_vlm_architecture":
                calls_fn = True
                break
    assert calls_fn, "get_model does not call is_vlm_architecture"


# [pr_diff] fail_to_pass
def test_model_class_dispatch_uses_arch_detection():
    """Model class selection (AutoModelForImageTextToText vs CausalLM) must use
    architecture detection, not training config flag.

    # AST-only because: get_model requires GPU to call.
    """
    source = Path(MODEL_PY).read_text()
    lines = source.splitlines()

    # Find where AutoModelForImageTextToText is referenced — this is the VLM
    # model class path. It should be guarded by architecture detection, not
    # the old is_vlm (training config) flag.
    for i, line in enumerate(lines):
        if "AutoModelForImageTextToText" in line:
            # Check surrounding context (10 lines before)
            ctx_start = max(0, i - 10)
            context = "\n".join(lines[ctx_start:i + 1])
            # Should NOT be guarded by the old single boolean is_vlm
            # The variable name should reflect architecture, not training
            assert "is_vlm_arch" in context or "is_vlm_architecture" in context or "vlm_arch" in context, \
                f"AutoModelForImageTextToText dispatch should use architecture detection variable"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_get_model_info_registry_lookup():
    """_get_model_info_from_config returns ModelInfo for VLM types, None otherwise."""
    vlm = _load_vlm_module()
    fn = vlm._get_model_info_from_config

    for mt in ["qwen3_5_moe", "qwen3_5", "qwen3_vl"]:
        info = fn(_MockConfig(mt))
        assert info is not None, f"{mt} should have model info"
        assert hasattr(info, "vision_encoder_attr")
        assert hasattr(info, "language_model_attr")

    for mt in ["llama", "gpt2", "mistral"]:
        assert fn(_MockConfig(mt)) is None, f"{mt} should return None"


# [pr_diff] pass_to_pass
def test_vlm_registry_entries():
    """VLM_REGISTRY has expected entries with valid attributes."""
    vlm = _load_vlm_module()
    reg = vlm.VLM_REGISTRY

    for key in ["qwen3_vl", "qwen3_5", "qwen3_5_moe"]:
        assert key in reg, f"{key} missing from VLM_REGISTRY"
        info = reg[key]
        assert isinstance(info.vision_encoder_attr, str) and info.vision_encoder_attr
        assert isinstance(info.language_model_attr, str) and info.language_model_attr


# [static] fail_to_pass
def test_is_vlm_architecture_not_stub():
    """is_vlm_architecture uses registry lookup, not hardcoded values."""
    source = Path(VLM_PY).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "is_vlm_architecture":
            stmts = [n for n in node.body
                     if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]
            assert len(stmts) >= 1, "is_vlm_architecture is a stub"
            func_src = "\n".join(source.splitlines()[node.lineno - 1:node.end_lineno])
            assert "_get_model_info_from_config" in func_src or "VLM_REGISTRY" in func_src, \
                "should use registry lookup"
            return
    raise AssertionError("is_vlm_architecture function not found")


# [pr_diff] pass_to_pass
def test_freeze_guarded_by_training_config():
    """freeze_vision_encoder must be guarded by training config, not architecture detection.

    # AST-only because: get_model requires GPU to call.
    """
    source = Path(MODEL_PY).read_text()
    lines = source.splitlines()

    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name == "freeze_vision_encoder":
                ctx_start = max(0, node.lineno - 6)
                context = "\n".join(lines[ctx_start:node.lineno])
                assert "is_vlm_architecture" not in context, \
                    "freeze_vision_encoder should be guarded by training config, not architecture"


# [pr_diff] pass_to_pass
def test_setup_fsdp_vision_guarded_by_training():
    """setup_fsdp vision encoder sharding must be guarded by training config.

    # AST-only because: setup_fsdp requires GPU and FSDP to call.
    """
    source = Path(MODEL_PY).read_text()
    lines = source.splitlines()
    tree = ast.parse(source)

    setup_fsdp = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "setup_fsdp":
            setup_fsdp = node
            break
    assert setup_fsdp is not None, "setup_fsdp function not found"

    func_source = "\n".join(lines[setup_fsdp.lineno - 1:setup_fsdp.end_lineno])
    # Vision encoder FSDP should NOT use is_vlm_architecture
    assert "is_vlm_architecture" not in func_source, \
        "setup_fsdp should use training config for vision encoder sharding, not architecture detection"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:5 @ ecd080928014e20d1927a4f8b0b01d399151fdba
def test_no_bare_except():
    """No bare except blocks in modified files (AGENTS.md:5)."""
    for filepath in [VLM_PY, MODEL_PY]:
        source = Path(filepath).read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                for handler in node.handlers:
                    assert handler.type is not None, \
                        f"{filepath}: bare except at line {node.lineno}"


# [agent_config] pass_to_pass — AGENTS.md:5,23 @ ecd080928014e20d1927a4f8b0b01d399151fdba
def test_errors_not_silenced():
    """No except-pass patterns that silently swallow errors (AGENTS.md:5, Zen:23)."""
    for filepath in [VLM_PY, MODEL_PY]:
        source = Path(filepath).read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                for handler in node.handlers:
                    body = handler.body
                    if len(body) == 1 and isinstance(body[0], ast.Pass):
                        assert False, \
                            f"{filepath}: except-pass silently swallows errors at line {handler.lineno}"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates
# ---------------------------------------------------------------------------

# [repo_ci] pass_to_pass
def test_repo_ruff_check():
    """Repo's ruff lint check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    # ruff check on modified files
    r = subprocess.run(
        ["ruff", "check", "--config=/repo/pyproject.toml", VLM_PY, MODEL_PY],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_ci] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff format check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    # ruff format check on modified files
    r = subprocess.run(
        ["ruff", "format", "--check", "--config=/repo/pyproject.toml", VLM_PY, MODEL_PY],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_ci] pass_to_pass
def test_repo_imports():
    """Modified files can be imported without errors (pass_to_pass)."""
    import sys
    python_exe = sys.executable  # Use the same python running this test

    # Test vlm.py imports
    r = subprocess.run(
        [python_exe, "-c", "from prime_rl.utils.vlm import get_language_model, get_vision_encoder, VLM_REGISTRY, VLMModelInfo"],
        capture_output=True, text=True, timeout=30, cwd=REPO, env={"PYTHONPATH": f"{REPO}/src"},
    )
    assert r.returncode == 0, f"vlm.py import failed:\n{r.stderr[-500:]}"

    # Test model.py can be parsed (AST check)
    r = subprocess.run(
        [python_exe, "-c", f"import ast; ast.parse(open('{MODEL_PY}').read())"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"model.py parse failed:\n{r.stderr[-500:]}"


# [repo_ci] pass_to_pass
def test_repo_configs_parse():
    """All repo config files are valid TOML (pass_to_pass)."""
    import sys
    python_exe = sys.executable

    configs_dir = Path(f"{REPO}/configs")
    examples_dir = Path(f"{REPO}/examples")

    toml_files = list(configs_dir.rglob("*.toml")) + list(examples_dir.rglob("*.toml"))
    assert len(toml_files) > 0, "No config files found"

    for toml_file in toml_files:
        r = subprocess.run(
            [python_exe, "-c", f"import tomllib; tomllib.load(open('{toml_file}', 'rb'))"],
            capture_output=True, text=True, timeout=10, cwd=REPO,
        )
        assert r.returncode == 0, f"Failed to parse {toml_file}:\n{r.stderr[-500:]}"


# [repo_ci] pass_to_pass
def test_repo_readme_exists():
    """Repo README exists and is readable (pass_to_pass)."""
    readme = Path(f"{REPO}/README.md")
    assert readme.exists(), "README.md must exist"
    content = readme.read_text()
    assert len(content) > 100, "README.md should have substantial content"




# [repo_ci] pass_to_pass
def test_repo_git_valid():
    """Repo has valid git structure and commit history (pass_to_pass)."""
    r = subprocess.run(
        ["git", "-C", REPO, "log", "--oneline", "-1"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Git log failed:\n{r.stderr}"
    assert "ecd0809" in r.stdout, "Expected base commit not found"


# [repo_ci] pass_to_pass
def test_repo_vlm_registry_import():
    """VLM module imports correctly with all registry entries (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
sys.path.insert(0, "/repo/src")
from prime_rl.utils.vlm import VLM_REGISTRY, VLMModelInfo

# Verify registry has expected entries
expected = ["qwen3_vl", "qwen3_5", "qwen3_5_moe"]
for key in expected:
    assert key in VLM_REGISTRY, f"{key} missing from registry"
    info = VLM_REGISTRY[key]
    assert isinstance(info, VLMModelInfo)
    assert info.vision_encoder_attr == "model.visual"
    assert info.language_model_attr == "model.language_model"

print("VLM registry OK")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"VLM import test failed:\n{r.stderr}"
    assert "VLM registry OK" in r.stdout


# [repo_ci] pass_to_pass
def test_repo_model_py_parses():
    """model.py parses as valid Python AST (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", f"import ast; ast.parse(open('{MODEL_PY}').read())"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"model.py AST parse failed:\n{r.stderr}"


# [repo_ci] pass_to_pass
def test_repo_vlm_py_parses():
    """vlm.py parses as valid Python AST (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", f"import ast; ast.parse(open('{VLM_PY}').read())"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"vlm.py AST parse failed:\n{r.stderr}"

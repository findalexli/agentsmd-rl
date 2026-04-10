"""
Task: vllm-gptq-compile-correctness
Repo: vllm-project/vllm @ 37a83007fef9925609a8d9b7c7b86bb41dab4e5d
PR:   #38161

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import dataclasses
import types
from enum import Enum
from pathlib import Path

import torch

REPO = "/workspace/vllm"
WEIGHT_UTILS = f"{REPO}/vllm/model_executor/model_loader/weight_utils.py"
TEST_FILE = f"{REPO}/tests/compile/fullgraph/test_basic_correctness.py"


def _load_initialize_single_dummy_weight(is_tpu=False, is_rocm=False):
    """Extract and compile initialize_single_dummy_weight with mocked platform.
    # AST-only because: function depends on vllm.platforms.current_platform (GPU)
    """
    src = Path(WEIGHT_UTILS).read_text()
    tree = ast.parse(src)
    func_src = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "initialize_single_dummy_weight":
            func_src = ast.get_source_segment(src, node)
            break
    assert func_src is not None, "initialize_single_dummy_weight not found in weight_utils.py"
    platform = types.SimpleNamespace(is_tpu=lambda: is_tpu, is_rocm=lambda: is_rocm)
    ns = {"torch": torch, "current_platform": platform}
    exec(compile(ast.parse(func_src), "<test>", "exec"), ns)
    return ns["initialize_single_dummy_weight"]


def _load_test_compile_correctness():
    """Extract test_compile_correctness, mock compare_all_settings to capture calls.
    # AST-only because: function requires GPU cluster, vllm imports, pytest fixtures
    """
    src = Path(TEST_FILE).read_text()
    tree = ast.parse(src)
    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "test_compile_correctness":
            func_node = node
            break
    assert func_node is not None, "test_compile_correctness not found"
    lines = src.splitlines(keepends=True)
    func_src = "".join(lines[func_node.lineno - 1 : func_node.end_lineno])

    class CompilationMode(Enum):
        NONE = 0
        STOCK_TORCH_COMPILE = 1
        DYNAMO_TRACE_ONCE = 2
        VLLM_COMPILE = 3

    calls = []

    def mock_compare_all_settings(model, all_args, all_envs, method="generate"):
        calls.append({"args": list(all_args), "envs": list(all_envs), "method": method})

    @dataclasses.dataclass
    class TestSetting:
        model: str
        model_args: list
        pp_size: int
        tp_size: int
        attn_backend: str
        method: str

    class MockPytest:
        @staticmethod
        def skip(reason=""):
            pass

    test_setting = TestSetting(
        model="mock-model",
        model_args=["--max-model-len", "2048"],
        pp_size=1,
        tp_size=1,
        attn_backend="FLASH_ATTN",
        method="generate",
    )

    ns = {
        "CompilationMode": CompilationMode,
        "compare_all_settings": mock_compare_all_settings,
        "cuda_device_count_stateless": lambda: 8,
        "pytest": MockPytest(),
        "TestSetting": TestSetting,
        "__builtins__": __builtins__,
    }
    exec(compile(ast.parse(func_src), "<test>", "exec"), ns)
    fn = ns["test_compile_correctness"]
    fn(test_setting)
    return calls


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    for path in [WEIGHT_UTILS, TEST_FILE]:
        src = Path(path).read_text()
        ast.parse(src)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_int_params_zeroed_on_rocm():
    """Integer params (int32/int64 like GPTQ qweight/qzeros) are zeroed on ROCm."""
    fn = _load_initialize_single_dummy_weight(is_rocm=True)

    # int32 — simulates GPTQ qweight (various shapes and values)
    p32 = torch.ones(4, 8, dtype=torch.int32) * 42
    fn(p32)
    assert torch.all(p32 == 0), f"int32 param not zeroed on ROCm: {p32}"

    p32_neg = torch.full((2, 3), -17, dtype=torch.int32)
    fn(p32_neg)
    assert torch.all(p32_neg == 0), f"int32 negative param not zeroed on ROCm: {p32_neg}"

    # int64 — simulates GPTQ qzeros
    p64 = torch.ones(8, dtype=torch.int64) * 99
    fn(p64)
    assert torch.all(p64 == 0), f"int64 param not zeroed on ROCm: {p64}"

    # int16 — another integer dtype
    p16 = torch.full((5,), 255, dtype=torch.int16)
    fn(p16)
    assert torch.all(p16 == 0), f"int16 param not zeroed on ROCm: {p16}"


# [pr_diff] fail_to_pass
def test_list_construction_matching_lengths():
    """all_args and all_envs have matching lengths in compare_all_settings calls."""
    calls = _load_test_compile_correctness()
    assert len(calls) >= 1, "Expected >=1 compare_all_settings calls, got 0"
    for i, call in enumerate(calls):
        assert len(call["args"]) == len(call["envs"]), (
            f"Call {i}: len(all_args)={len(call['args'])} != len(all_envs)={len(call['envs'])}"
        )
        assert len(call["args"]) > 0, f"Call {i}: empty configuration lists"
    # Anti-stub: verify args reference real compilation modes
    all_arg_strs = []
    for call in calls:
        for arg_list in call["args"]:
            if isinstance(arg_list, list):
                all_arg_strs.extend(str(a) for a in arg_list)
            else:
                all_arg_strs.append(str(arg_list))
    mode_args = [a for a in all_arg_strs if "-cc.mode=" in a]
    assert len(mode_args) >= 2, (
        f"Expected >=2 mode flags (-cc.mode=...), found {len(mode_args)} — possible stub"
    )
    mode_names = {a.split("-cc.mode=")[-1].split(",")[0].split(" ")[0] for a in mode_args}
    assert len(mode_names) >= 2, f"Expected >=2 distinct modes, got {mode_names}"


# [pr_diff] fail_to_pass
def test_inductor_comparison_not_dead_code():
    """Inductor comparison section produces non-empty pairs with inductor backend args."""
    calls = _load_test_compile_correctness()
    assert len(calls) >= 2, (
        f"Expected >=2 compare_all_settings calls (inductor+eager), got {len(calls)} "
        "— inductor section may be dead code"
    )
    # Find calls with inductor-backend args
    inductor_calls = []
    for i, call in enumerate(calls):
        for arg_list in call["args"]:
            if isinstance(arg_list, list) and any("inductor" in str(a) for a in arg_list):
                inductor_calls.append(i)
                break
    assert len(inductor_calls) >= 1, "No compare_all_settings call with inductor backend found"
    for idx in inductor_calls:
        ic = calls[idx]
        assert len(ic["args"]) == len(ic["envs"]), (
            f"Inductor call {idx}: len(args)={len(ic['args'])} != len(envs)={len(ic['envs'])}"
        )
        assert len(ic["args"]) > 0, f"Inductor call {idx} has 0 configurations"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_float_params_initialized_correctly():
    """Float params still get initialized in [low, high] with reproducible seeds."""
    fn = _load_initialize_single_dummy_weight(is_rocm=False)

    # Test with default-ish range
    p1 = torch.zeros(16, 16, dtype=torch.float32)
    fn(p1, low=-1e-3, high=1e-3, seed=1234)
    assert not torch.all(p1 == 0), "Float param should not remain all zeros"
    assert p1.min().item() >= -1e-3 - 1e-6, f"Below range: {p1.min().item()}"
    assert p1.max().item() <= 1e-3 + 1e-6, f"Above range: {p1.max().item()}"

    # Reproducibility with same seed
    p2 = torch.zeros(16, 16, dtype=torch.float32)
    fn(p2, low=-1e-3, high=1e-3, seed=1234)
    assert torch.allclose(p1, p2), "Same seed should produce identical values"

    # Different seed → different values
    p3 = torch.zeros(16, 16, dtype=torch.float32)
    fn(p3, low=-1e-3, high=1e-3, seed=9999)
    assert not torch.allclose(p1, p3), "Different seeds should produce different values"

    # Different range
    p4 = torch.zeros(8, 8, dtype=torch.float32)
    fn(p4, low=-0.5, high=0.5, seed=42)
    assert p4.min().item() >= -0.5 - 1e-6, f"Below range: {p4.min().item()}"
    assert p4.max().item() <= 0.5 + 1e-6, f"Above range: {p4.max().item()}"
    assert not torch.all(p4 == 0), "Float param should be initialized"


# [pr_diff] pass_to_pass
def test_non_rocm_int_params_unchanged():
    """On non-ROCm, integer params are returned untouched (early return path)."""
    fn = _load_initialize_single_dummy_weight(is_rocm=False)

    # int32
    p32 = torch.ones(4, 4, dtype=torch.int32) * 42
    p32_orig = p32.clone()
    fn(p32)
    assert torch.equal(p32, p32_orig), f"int32 param modified on non-ROCm: {p32}"

    # int64
    p64 = torch.arange(8, dtype=torch.int64)
    p64_orig = p64.clone()
    fn(p64)
    assert torch.equal(p64, p64_orig), f"int64 param modified on non-ROCm: {p64}"

    # int16
    p16 = torch.full((3, 3), 7, dtype=torch.int16)
    p16_orig = p16.clone()
    fn(p16)
    assert torch.equal(p16, p16_orig), f"int16 param modified on non-ROCm: {p16}"


# ---------------------------------------------------------------------------
# Anti-stub (static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
# AST-only because: safety net alongside behavioral tests — ensures agent doesn't
# replace functions with trivial stubs that happen to satisfy mocked behavioral checks
def test_not_stub():
    """Both modified functions have non-trivial bodies."""
    # Check initialize_single_dummy_weight
    src = Path(WEIGHT_UTILS).read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "initialize_single_dummy_weight":
            meaningful = sum(
                1 for child in ast.walk(node)
                if isinstance(child, (ast.If, ast.For, ast.While, ast.Assign, ast.AugAssign, ast.Return))
                or (isinstance(child, ast.Expr) and not isinstance(getattr(child, "value", None), ast.Constant))
            )
            assert meaningful >= 5, f"initialize_single_dummy_weight: {meaningful} stmts — likely stub"
            break
    else:
        raise AssertionError("initialize_single_dummy_weight not found")

    # Check test_compile_correctness
    src2 = Path(TEST_FILE).read_text()
    tree2 = ast.parse(src2)
    for node in ast.walk(tree2):
        if isinstance(node, ast.FunctionDef) and node.name == "test_compile_correctness":
            meaningful = sum(
                1 for child in ast.walk(node)
                if isinstance(child, (ast.If, ast.For, ast.While, ast.Assign, ast.AugAssign, ast.Return))
                or (isinstance(child, ast.Expr) and not isinstance(getattr(child, "value", None), ast.Constant))
            )
            assert meaningful >= 8, f"test_compile_correctness: {meaningful} stmts — likely stub"
            break
    else:
        raise AssertionError("test_compile_correctness not found")


# ---------------------------------------------------------------------------
# Repo CI tests (repo_tests) — pass_to_pass gates from actual CI commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — CI: ruff check
def test_repo_ruff_lint():
    """Repo's ruff linter passes on modified files (pass_to_pass)."""
    import subprocess

    r = subprocess.run(
        ["ruff", "check", WEIGHT_UTILS, TEST_FILE, "--select", "E,F", "--quiet"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI: py_compile
def test_repo_py_compile():
    """Modified files compile without syntax errors (pass_to_pass)."""
    import subprocess

    r = subprocess.run(
        ["python", "-m", "py_compile", WEIGHT_UTILS, TEST_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI: python -c ast.parse
def test_repo_ast_parse():
    """Modified files parse as valid Python AST (pass_to_pass)."""
    import subprocess

    cmd = (
        "import ast; "
        "[ast.parse(open(f).read()) for f in [\"vllm/model_executor/model_loader/weight_utils.py\", "
        "\"tests/compile/fullgraph/test_basic_correctness.py\"]]"
    )
    r = subprocess.run(
        ["python", "-c", cmd],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"AST parse failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md lint rule
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:86-98 @ 37a83007fef9925609a8d9b7c7b86bb41dab4e5d
def test_ruff_lint_clean():
    """ruff lint passes on modified files (AGENTS.md requires pre-commit ruff-check)."""
    import subprocess

    r = subprocess.run(
        ["ruff", "check", WEIGHT_UTILS, TEST_FILE, "--select", "E,F,W", "--quiet"],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"ruff lint errors:\n{r.stderr.decode()}\n{r.stdout.decode()}"

"""
Task: prime-rl-vllm-sampling-args-token-ids
Repo: PrimeIntellect-ai/prime-rl @ b92c2128ddeb679c23954c2bf6825e4d6659d501
PR:   2100

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import inspect
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

REPO = "/workspace/prime-rl"
TARGET = f"{REPO}/src/prime_rl/orchestrator/utils.py"


# ---------------------------------------------------------------------------
# Helpers — mock SamplingConfig and function extraction
# ---------------------------------------------------------------------------

@dataclass
class FakeExtraBody:
    def __iter__(self):
        return iter({}.items())

    def items(self):
        return {}.items()


@dataclass
class FakeSamplingConfig:
    temperature: float = 1.0
    temp_scheduler: object = None
    min_tokens: int = 0
    repetition_penalty: float = 1.0
    extra_body: object = None
    max_tokens: int = 100

    def __post_init__(self):
        if self.extra_body is None:
            self.extra_body = FakeExtraBody()

    def __iter__(self):
        return iter({
            "temperature": self.temperature,
            "temp_scheduler": self.temp_scheduler,
            "min_tokens": self.min_tokens,
            "repetition_penalty": self.repetition_penalty,
            "extra_body": self.extra_body,
            "max_tokens": self.max_tokens,
        }.items())


def _extract_function(filepath, func_name):
    """Extract and compile a function from source using AST."""
    source = Path(filepath).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
            lines = source.splitlines(keepends=True)
            func_src = "".join(lines[node.lineno - 1 : node.end_lineno])
            # Remove SamplingConfig type annotation so our mock works
            func_src = re.sub(r":\s*SamplingConfig", "", func_src)
            ns = {"__builtins__": __builtins__}
            exec(compile(func_src, "<extracted>", "exec"), ns)
            return ns[func_name]
    return None


def _discover_vllm_param(func):
    """Find the parameter that controls vLLM-specific behavior.

    The buggy code uses 'use_token_client' — excluded because the fix
    requires introducing a proper vLLM-specific flag.
    """
    sig = inspect.signature(func)
    known = {"sampling_config", "temperature", "use_token_client"}
    for name in sig.parameters:
        if name in known:
            continue
        if "vllm" in name.lower():
            return name
    for name, p in sig.parameters.items():
        if name in known:
            continue
        if isinstance(p.default, bool):
            return name
    return None


def _call_f2p(cfg, temperature, vllm_value):
    """Call get_sampling_args requiring the new vLLM param (fails on base)."""
    func = _extract_function(TARGET, "get_sampling_args")
    assert func is not None, "get_sampling_args not found"
    vllm_param = _discover_vllm_param(func)
    assert vllm_param is not None, "No vLLM-controlling parameter found"
    return func(cfg, temperature=temperature, **{vllm_param: vllm_value})


def _call_flexible(cfg, temperature, vllm_value=True):
    """Call get_sampling_args, working on both base and fixed code."""
    func = _extract_function(TARGET, "get_sampling_args")
    assert func is not None, "get_sampling_args not found"
    vllm_param = _discover_vllm_param(func)
    if vllm_param:
        return func(cfg, temperature=temperature, **{vllm_param: vllm_value})
    sig = inspect.signature(func)
    if "use_token_client" in sig.parameters:
        return func(cfg, temperature=temperature, use_token_client=vllm_value)
    return func(cfg, temperature=temperature)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import py_compile

    for path in [
        f"{REPO}/src/prime_rl/orchestrator/utils.py",
        f"{REPO}/src/prime_rl/orchestrator/orchestrator.py",
        f"{REPO}/src/prime_rl/orchestrator/scheduler.py",
    ]:
        py_compile.compile(path, doraise=True)


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's ruff linting passes on modified files (pass_to_pass)."""
    # Ensure ruff is installed
    subprocess.run(
        ["python", "-m", "pip", "install", "ruff", "-q"],
        capture_output=True,
        timeout=60,
    )
    files = [
        f"{REPO}/src/prime_rl/orchestrator/utils.py",
        f"{REPO}/src/prime_rl/orchestrator/orchestrator.py",
        f"{REPO}/src/prime_rl/orchestrator/scheduler.py",
    ]
    r = subprocess.run(
        ["python", "-m", "ruff", "check", "--config", f"{REPO}/pyproject.toml"] + files,
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff format check passes on modified files (pass_to_pass)."""
    # Ensure ruff is installed
    subprocess.run(
        ["python", "-m", "pip", "install", "ruff", "-q"],
        capture_output=True,
        timeout=60,
    )
    files = [
        f"{REPO}/src/prime_rl/orchestrator/utils.py",
        f"{REPO}/src/prime_rl/orchestrator/orchestrator.py",
        f"{REPO}/src/prime_rl/orchestrator/scheduler.py",
    ]
    r = subprocess.run(
        ["python", "-m", "ruff", "format", "--check", "--config", f"{REPO}/pyproject.toml"] + files,
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_vllm_backend_gets_return_token_ids():
    """vLLM backend must receive return_token_ids=True in extra_body."""
    for temp in [0.7, 1.0, 0.0]:
        cfg = FakeSamplingConfig()
        result = _call_f2p(cfg, temperature=temp, vllm_value=True)
        assert isinstance(result, dict)
        eb = result.get("extra_body", {})
        assert isinstance(eb, dict)
        assert eb.get("return_token_ids") is True, (
            f"return_token_ids missing at temp={temp}"
        )


# [pr_diff] fail_to_pass
def test_non_vllm_backend_omits_vllm_keys():
    """Non-vLLM backend must NOT get return_token_ids/top_k/min_p."""
    for temp in [0.7, 1.0]:
        cfg = FakeSamplingConfig()
        result = _call_f2p(cfg, temperature=temp, vllm_value=False)
        assert isinstance(result, dict)
        assert "logprobs" in result, "Result missing logprobs key"
        eb = result.get("extra_body", {})
        if not isinstance(eb, dict):
            eb = {}
        for key in ["return_token_ids", "top_k", "min_p"]:
            assert key not in eb, f"vLLM key '{key}' in non-vLLM extra_body"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_logprobs_always_true():
    """logprobs must be True regardless of backend type."""
    cfg = FakeSamplingConfig()
    for vllm_val in [True, False]:
        result = _call_flexible(cfg, temperature=0.7, vllm_value=vllm_val)
        assert isinstance(result, dict)
        assert result.get("logprobs") is True, f"logprobs not True when vllm={vllm_val}"


# [pr_diff] pass_to_pass
def test_min_tokens_and_repetition_penalty_preserved():
    """min_tokens and repetition_penalty must appear in extra_body when set."""
    for min_tok, rep_pen in [(10, 1.5), (5, 2.0)]:
        cfg = FakeSamplingConfig(min_tokens=min_tok, repetition_penalty=rep_pen)
        result = _call_flexible(cfg, temperature=0.7, vllm_value=True)
        eb = result.get("extra_body", {})
        assert isinstance(eb, dict)
        assert eb.get("min_tokens") == min_tok, f"min_tokens expected {min_tok}"
        assert eb.get("repetition_penalty") == rep_pen, f"repetition_penalty expected {rep_pen}"


# [pr_diff] pass_to_pass
def test_max_tokens_in_result():
    """max_tokens must still be passed through in the result."""
    for max_tok in [200, 50]:
        cfg = FakeSamplingConfig(max_tokens=max_tok)
        result = _call_flexible(cfg, temperature=0.7, vllm_value=True)
        assert result.get("max_tokens") == max_tok, f"max_tokens expected {max_tok}"


# ---------------------------------------------------------------------------
# Structural (pr_diff) — caller correctness
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_orchestrator_callers_updated():
    """orchestrator.py must not pass use_token_client to get_sampling_args."""
    src = Path(f"{REPO}/src/prime_rl/orchestrator/orchestrator.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = ""
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name == "get_sampling_args":
                for kw in node.keywords:
                    assert kw.arg != "use_token_client", (
                        "orchestrator.py still passes use_token_client"
                    )


# [pr_diff] fail_to_pass
def test_scheduler_callers_updated():
    """scheduler.py must not pass use_token_client to get_sampling_args."""
    # AST-only because: scheduler.py imports heavy deps (torch, distributed) that aren't installed
    src = Path(f"{REPO}/src/prime_rl/orchestrator/scheduler.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = ""
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name == "get_sampling_args":
                for kw in node.keywords:
                    assert kw.arg != "use_token_client", (
                        "scheduler.py still passes use_token_client"
                    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:15 @ b92c2128
def test_explicit_vllm_parameter():
    """get_sampling_args must use an explicit vLLM flag, not use_token_client."""
    src = Path(TARGET).read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_sampling_args":
            for arg in node.args.args + node.args.kwonlyargs:
                assert arg.arg != "use_token_client", (
                    "Parameter still named use_token_client"
                )
            return
    raise AssertionError("get_sampling_args not found")

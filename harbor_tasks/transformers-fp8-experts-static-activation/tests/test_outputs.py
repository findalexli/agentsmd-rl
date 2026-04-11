"""
Task: transformers-fp8-experts-static-activation
Repo: huggingface/transformers @ f6195948b47f06444a7bdf5f169197ed64b64de2
PR:   44895

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/repo"
TARGET = f"{REPO}/src/transformers/integrations/finegrained_fp8.py"

# Shared setup: triton mock + FakeConfig, written once to a temp file
_SETUP = """\
import torch, sys, types

# Mock triton (GPU-only) so the module can be imported on CPU
triton_mock = types.ModuleType('triton')
triton_mock.cdiv = lambda a, b: (a + b - 1) // b
triton_mock.jit = lambda **kw: (lambda fn: fn)
sys.modules.setdefault('triton', triton_mock)

class FakeConfig:
    hidden_size = 64
    num_local_experts = 4
    moe_intermediate_size = 128
    hidden_act = 'silu'
"""


def _run(script: str, timeout: int = 30) -> None:
    """Run a Python script in a subprocess; assert exit code 0."""
    full = _SETUP + "\n" + script
    r = subprocess.run(
        ["python3", "-c", full],
        capture_output=True,
        timeout=timeout,
        cwd=REPO,
    )
    assert r.returncode == 0, (
        f"Script failed (rc={r.returncode}):\n"
        f"STDOUT: {r.stdout.decode()}\nSTDERR: {r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without errors."""
    src = Path(TARGET).read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_static_scheme_accepted():
    """FP8Experts can be constructed with activation_scheme='static'."""
    _run("""
with torch.device('meta'):
    from transformers.integrations.finegrained_fp8 import FP8Experts
    module = FP8Experts(FakeConfig(), activation_scheme='static')
print('OK')
""")


# [pr_diff] fail_to_pass
def test_static_activation_scale_params():
    """Static mode registers gate_up and down activation scale params with correct shape/dtype."""
    _run("""
with torch.device('meta'):
    from transformers.integrations.finegrained_fp8 import FP8Experts

    for num_experts in [4, 8]:
        cfg = FakeConfig()
        cfg.num_local_experts = num_experts
        module = FP8Experts(cfg, activation_scheme='static')
        param_names = [n for n, _ in module.named_parameters()]

        assert 'gate_up_proj_activation_scale' in param_names, \
            f'Missing gate_up_proj_activation_scale, got: {param_names}'
        assert 'down_proj_activation_scale' in param_names, \
            f'Missing down_proj_activation_scale, got: {param_names}'

        gu = module.gate_up_proj_activation_scale
        dp = module.down_proj_activation_scale
        assert gu.shape == (num_experts,), f'gate_up scale shape {gu.shape} != ({num_experts},)'
        assert dp.shape == (num_experts,), f'down scale shape {dp.shape} != ({num_experts},)'
        assert gu.dtype == torch.float32, f'gate_up scale dtype {gu.dtype}'
        assert dp.dtype == torch.float32, f'down scale dtype {dp.dtype}'
print('OK')
""")


# [pr_diff] fail_to_pass
def test_static_quantizes_to_fp8():
    """linear() with static scheme + activation_scale quantizes input to FP8 dtype."""
    _run("""
from unittest.mock import patch

with torch.device('meta'):
    from transformers.integrations.finegrained_fp8 import FP8Experts
    module = FP8Experts(FakeConfig(), activation_scheme='static')

captured = {}
def mock_matmul(*args, **kwargs):
    captured['qinput'] = args[0]
    captured['input_scale'] = args[2]
    return torch.zeros(args[0].shape[0], args[1].shape[0], dtype=torch.float32)

with patch('transformers.integrations.finegrained_fp8.w8a8_fp8_matmul', mock_matmul):
    for inp_val in [1.0, 5.0, 10.0]:
        inp = torch.full((4, 64), inp_val)
        weight = torch.zeros(128, 64, dtype=torch.float8_e4m3fn)
        weight_scale = torch.ones(128)
        act_scale = torch.tensor(2.0)

        result = module.linear(inp, weight, weight_scale, activation_scale=act_scale)

        fp8_types = (torch.float8_e4m3fn, torch.float8_e5m2)
        if hasattr(torch, 'float8_e4m3fnuz'):
            fp8_types += (torch.float8_e4m3fnuz,)
        assert captured['qinput'].dtype in fp8_types, \
            f'Expected FP8 dtype, got {captured["qinput"].dtype} for inp_val={inp_val}'
        assert captured['input_scale'] is not None, 'Activation scale not passed to matmul'
print('OK')
""")


# [pr_diff] fail_to_pass
def test_static_scale_affects_output():
    """Different activation scales produce different quantized values (scale is actually used)."""
    _run("""
from unittest.mock import patch

with torch.device('meta'):
    from transformers.integrations.finegrained_fp8 import FP8Experts
    module = FP8Experts(FakeConfig(), activation_scheme='static')

results = []
for scale_val in [1.0, 4.0]:
    captured = {}
    def mock_matmul(*args, **kwargs):
        captured['qinput'] = args[0]
        return torch.zeros(args[0].shape[0], args[1].shape[0], dtype=torch.float32)

    with patch('transformers.integrations.finegrained_fp8.w8a8_fp8_matmul', mock_matmul):
        inp = torch.full((2, 64), 8.0)
        weight = torch.zeros(128, 64, dtype=torch.float8_e4m3fn)
        weight_scale = torch.ones(128)
        act_scale = torch.tensor(scale_val)
        module.linear(inp, weight, weight_scale, activation_scale=act_scale)
        results.append(captured['qinput'].float().clone())

# Different scales must produce different quantized values
# scale=1 -> qinput ~ 8.0, scale=4 -> qinput ~ 2.0
assert not torch.equal(results[0], results[1]), \
    'Changing activation_scale did not change quantized input'
assert results[1].abs().mean() < results[0].abs().mean(), \
    f'Larger scale should produce smaller quantized values: ' \
    f'scale=1 mean={results[0].abs().mean():.2f}, scale=4 mean={results[1].abs().mean():.2f}'
print('OK')
""")


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_dynamic_mode_no_static_params():
    """Dynamic mode still works and does NOT register activation_scale params."""
    _run("""
with torch.device('meta'):
    from transformers.integrations.finegrained_fp8 import FP8Experts
    module = FP8Experts(FakeConfig(), activation_scheme='dynamic')
    param_names = [n for n, _ in module.named_parameters()]
    assert 'gate_up_proj' in param_names, 'Missing gate_up_proj'
    assert 'down_proj' in param_names, 'Missing down_proj'
    assert 'gate_up_proj_activation_scale' not in param_names, \
        'Dynamic mode should not have gate_up_proj_activation_scale'
    assert 'down_proj_activation_scale' not in param_names, \
        'Dynamic mode should not have down_proj_activation_scale'
print('OK')
""")


# ---------------------------------------------------------------------------
# Structural (pr_diff) — multi-GPU set_device (cannot test behaviorally on CPU)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_set_device_calls():
    """Multi-GPU code paths call torch.cuda.set_device (AST-verified; needs GPU to test behaviorally)."""
    src = Path(TARGET).read_text()
    tree = ast.parse(src)

    set_device_count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == 'set_device':
                set_device_count += 1

    assert set_device_count >= 2, (
        f"Expected >=2 set_device() calls in multi-GPU code paths, found {set_device_count}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — actual CI commands from the repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — From Makefile and CI
def test_ruff_format_check():
    """Repo CI: Modified file passes ruff format check (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check", TARGET],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"ruff format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
    )


# [repo_tests] pass_to_pass — From utils/check_inits.py
def test_check_inits():
    """Repo CI: utils/check_inits.py passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_inits.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, (
        f"check_inits failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
    )


# [repo_tests] pass_to_pass — From utils/check_dummies.py
def test_check_dummies():
    """Repo CI: utils/check_dummies.py passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_dummies.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, (
        f"check_dummies failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
    )


# [repo_tests] pass_to_pass — From utils/check_copies.py
def test_check_copies():
    """Repo CI: utils/check_copies.py passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_copies.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, (
        f"check_copies failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .ai/AGENTS.md:2 @ f6195948b47f06444a7bdf5f169197ed64b64de2
def test_ruff_check():
    """Modified file passes ruff linting (AGENTS.md: 'make style: runs formatters and linters (ruff)')."""
    r = subprocess.run(
        ["ruff", "check", TARGET, "--quiet"],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"ruff check failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )

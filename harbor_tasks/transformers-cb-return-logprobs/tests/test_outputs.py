"""
Task: transformers-cb-return-logprobs
Repo: huggingface/transformers @ a9532bcf887b364bfedcc33a13be2b1d1acbef85
PR:   #44835

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys

REPO = "/repo"
sys.path.insert(0, f"{REPO}/src")

CONFIG_FILE = f"{REPO}/src/transformers/generation/configuration_utils.py"
REQUESTS_FILE = f"{REPO}/src/transformers/generation/continuous_batching/requests.py"
API_FILE = f"{REPO}/src/transformers/generation/continuous_batching/continuous_api.py"
IO_FILE = f"{REPO}/src/transformers/generation/continuous_batching/input_outputs.py"

CHANGED_FILES = [CONFIG_FILE, REQUESTS_FILE, API_FILE, IO_FILE]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All four modified files must parse without syntax errors."""
    import py_compile

    for f in CHANGED_FILES:
        py_compile.compile(f, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_config_return_logprobs():
    """ContinuousBatchingConfig must expose return_logprobs defaulting to False."""
    from transformers.generation.configuration_utils import ContinuousBatchingConfig

    cfg = ContinuousBatchingConfig()
    assert hasattr(cfg, "return_logprobs"), "return_logprobs attribute missing"
    assert cfg.return_logprobs is False, f"default should be False, got {cfg.return_logprobs}"

    cfg_on = ContinuousBatchingConfig(return_logprobs=True)
    assert cfg_on.return_logprobs is True, "setting return_logprobs=True failed"


# [pr_diff] fail_to_pass
def test_update_accepts_logprob():
    """update_and_check_completion must accept (token_id, logprob) two-arg signature."""
    from transformers.generation.continuous_batching.requests import RequestState, RequestStatus

    state = RequestState(
        request_id="sig-1",
        initial_tokens=[1, 2, 3],
        max_new_tokens=5,
        eos_token_id=0,
    )
    state._status = RequestStatus.DECODING

    result = state.update_and_check_completion(42, -0.5)
    assert isinstance(result, bool), f"Expected bool, got {type(result)}"

    # Also verify with a different token and logprob value
    result2 = state.update_and_check_completion(99, -2.3)
    assert isinstance(result2, bool)


# [pr_diff] fail_to_pass
def test_logprobs_stored_in_output():
    """Logprobs must flow from update_and_check_completion to GenerationOutput."""
    from transformers.generation.continuous_batching.requests import RequestState, RequestStatus

    state = RequestState(
        request_id="store-1",
        initial_tokens=[10, 20],
        max_new_tokens=5,
        eos_token_id=0,
    )
    state._status = RequestStatus.DECODING

    logprob_vals = [-1.5, -0.3, -2.7]
    for i, lp in enumerate(logprob_vals):
        state.update_and_check_completion(100 + i, lp)

    output = state.to_generation_output()
    assert len(output.logprobs) >= len(logprob_vals), (
        f"Expected at least {len(logprob_vals)} logprobs, got {len(output.logprobs)}"
    )
    for i, expected in enumerate(logprob_vals):
        assert abs(output.logprobs[i] - expected) < 1e-6, (
            f"logprob[{i}] expected {expected}, got {output.logprobs[i]}"
        )


# [pr_diff] fail_to_pass
def test_fork_preserves_logprobs():
    """fork() must copy accumulated logprobs to the new state, independently."""
    from transformers.generation.continuous_batching.requests import RequestState, RequestStatus

    state = RequestState(
        request_id="fork-1",
        initial_tokens=[1],
        max_new_tokens=10,
        eos_token_id=0,
    )
    state._status = RequestStatus.DECODING
    state.update_and_check_completion(5, -2.0)
    state.update_and_check_completion(6, -0.4)

    forked = state.fork("fork-1-copy")
    assert hasattr(forked, "logprobs"), "forked state missing logprobs attr"
    assert len(forked.logprobs) == 2, f"Expected 2 logprobs in fork, got {len(forked.logprobs)}"
    assert abs(forked.logprobs[0] - (-2.0)) < 1e-6
    assert abs(forked.logprobs[1] - (-0.4)) < 1e-6

    # Mutation independence
    forked.logprobs.append(-0.1)
    assert len(state.logprobs) == 2, "Fork logprobs not independent from original"


# [pr_diff] fail_to_pass
def test_equivalent_initial_request_preserves_logprobs():
    """create_equivalent_initial_request must keep accumulated logprobs."""
    from transformers.generation.continuous_batching.requests import RequestState, RequestStatus

    state = RequestState(
        request_id="equiv-1",
        initial_tokens=[1, 2],
        max_new_tokens=10,
        eos_token_id=0,
    )
    state._status = RequestStatus.DECODING
    state.update_and_check_completion(50, -1.0)
    state.update_and_check_completion(60, -0.7)

    equiv = state.create_equivalent_initial_request()
    assert hasattr(equiv, "logprobs"), "equivalent request missing logprobs"
    assert len(equiv.logprobs) == 2, f"Expected 2 logprobs, got {len(equiv.logprobs)}"
    assert abs(equiv.logprobs[0] - (-1.0)) < 1e-6
    assert abs(equiv.logprobs[1] - (-0.7)) < 1e-6

    # Mutation independence
    equiv.logprobs.append(-0.5)
    assert len(state.logprobs) == 2, "Equivalent request logprobs not independent"


# [pr_diff] fail_to_pass
def test_eos_detection_with_logprob():
    """EOS detection must still work when logprob is passed."""
    from transformers.generation.continuous_batching.requests import RequestState, RequestStatus

    state = RequestState(
        request_id="eos-1",
        initial_tokens=[1],
        max_new_tokens=10,
        eos_token_id=99,
    )
    state._status = RequestStatus.DECODING

    done = state.update_and_check_completion(42, -0.8)
    assert done is False, f"Non-EOS token should not complete, got {done}"

    done = state.update_and_check_completion(99, -3.2)
    assert done is True, f"EOS token should complete, got {done}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — backward compatibility (base has 1-arg signature)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_none_logprob_backward_compat():
    """update_and_check_completion with logprob=None must not break token generation."""
    from transformers.generation.continuous_batching.requests import RequestState, RequestStatus

    state = RequestState(
        request_id="p2p-none",
        initial_tokens=[1, 2, 3],
        max_new_tokens=3,
        eos_token_id=99,
    )
    state._status = RequestStatus.DECODING

    state.update_and_check_completion(10, None)
    state.update_and_check_completion(20, None)

    output = state.to_generation_output()
    assert output.generated_tokens == [10, 20], f"Wrong tokens: {output.generated_tokens}"
    # logprobs should be empty or contain only None when None is passed
    assert all(lp is None for lp in output.logprobs) or len(output.logprobs) == 0, (
        f"Expected no real logprobs with None input, got {output.logprobs}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:2 @ a9532bcf887b
def test_ruff_check():
    """ruff check passes on all changed files (CLAUDE.md: 'make style: runs formatters and linters (ruff)')."""
    r = subprocess.run(
        ["ruff", "check", "--quiet"] + CHANGED_FILES,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout.decode()}"


# [repo_tests] pass_to_pass — repo CI: ruff format check
def test_ruff_format_check():
    """ruff format --check passes on all changed files (repo CI via Makefile 'check-repo' target)."""
    r = subprocess.run(
        ["ruff", "format", "--check"] + CHANGED_FILES,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ruff format check failed:\n{r.stderr.decode()[-500:]}"


# [repo_tests] pass_to_pass — repo CI: module import test
def test_continuous_batching_modules_import():
    """All modified continuous batching modules import without errors (repo CI)."""
    import importlib

    modules = [
        "transformers.generation.configuration_utils",
        "transformers.generation.continuous_batching.requests",
        "transformers.generation.continuous_batching.continuous_api",
        "transformers.generation.continuous_batching.input_outputs",
    ]
    for mod in modules:
        importlib.import_module(mod)


# [repo_tests] pass_to_pass — repo CI: attention mask tests
def test_repo_attention_mask():
    """Continuous batching attention mask tests pass (repo CI pass_to_pass)."""
    # Install required packages
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pytest-xdist", "parameterized"], check=False)
    r = subprocess.run(
        [
            "python", "-m", "pytest",
            "tests/generation/test_continuous_batching.py::ContinuousBatchingNoAcceleratorTest::test_attention_mask_0",
            "tests/generation/test_continuous_batching.py::ContinuousBatchingNoAcceleratorTest::test_attention_mask_1",
            "tests/generation/test_continuous_batching.py::ContinuousBatchingNoAcceleratorTest::test_attention_mask_2",
            "-v", "--no-header",
        ],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Attention mask tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — repo CI: layer grouping tests
def test_repo_group_layers():
    """Continuous batching layer grouping tests pass (repo CI pass_to_pass)."""
    # Install required packages
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pytest-xdist", "parameterized"], check=False)
    r = subprocess.run(
        [
            "python", "-m", "pytest",
            "tests/generation/test_continuous_batching.py::ContinuousBatchingNoAcceleratorTest::test_group_layers_0",
            "tests/generation/test_continuous_batching.py::ContinuousBatchingNoAcceleratorTest::test_group_layers_1",
            "tests/generation/test_continuous_batching.py::ContinuousBatchingNoAcceleratorTest::test_group_layers_2_f",
            "-v", "--no-header",
        ],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Group layers tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — repo CI: cache allocator tests
def test_repo_cache_allocator():
    """Continuous batching cache allocator read/write indices tests pass (repo CI pass_to_pass)."""
    # Install required packages
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pytest-xdist", "parameterized"], check=False)
    r = subprocess.run(
        [
            "python", "-m", "pytest",
            "tests/generation/test_continuous_batching.py::ContinuousBatchingNoAcceleratorTest::test_full_attention_get_read_indices_0",
            "tests/generation/test_continuous_batching.py::ContinuousBatchingNoAcceleratorTest::test_full_attention_get_write_indices_00",
            "tests/generation/test_continuous_batching.py::ContinuousBatchingNoAcceleratorTest::test_full_attention_get_read_indices_1",
            "tests/generation/test_continuous_batching.py::ContinuousBatchingNoAcceleratorTest::test_full_attention_get_write_indices_01",
            "-v", "--no-header",
        ],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Cache allocator tests failed:\n{r.stderr[-500:]}"

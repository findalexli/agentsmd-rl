"""
Task: slime-datasource-prompt-none-crash
Repo: THUDM/slime @ 10f21d86514bcd26ca813590a7d22072325d36df
PR:   1751

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import py_compile
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

REPO = "/workspace/slime"

# ---------------------------------------------------------------------------
# Shared mock setup — patches heavy deps so we can exec data_source.py
# ---------------------------------------------------------------------------

def _build_namespace():
    """Exec the class definitions from data_source.py with mocked deps."""
    import abc, copy, logging

    class _FakeDataset:
        """Mimics real Dataset: crashes if path is None (like the real one)."""
        def __init__(self, path, **kwargs):
            if path is None:
                raise ValueError("prompt_data is None — Dataset cannot load from None")
            self._count = hash(path) % 20 + 1  # vary length by path
            self.samples = [MagicMock() for _ in range(self._count)]
            self.shuffle_calls = []

        def __len__(self):
            return len(self.samples)

        def shuffle(self, epoch):
            self.shuffle_calls.append(epoch)

    ns = {
        "abc": abc,
        "copy": copy,
        "logging": logging,
        "os": os,
        "Path": Path,
        "torch": SimpleNamespace(
            load=lambda path, **kw: {},
            save=lambda obj, path: None,
        ),
        "Dataset": _FakeDataset,
        "load_function": MagicMock(),
        "load_processor": MagicMock(return_value=None),
        "load_tokenizer": MagicMock(return_value=MagicMock()),
        "Sample": MagicMock,
        "logger": logging.getLogger("test"),
    }

    source = Path(f"{REPO}/slime/rollout/data_source.py").read_text()
    idx = source.find("class DataSource")
    exec(source[idx:], ns)
    return ns


def _make_args(**overrides):
    """Build a minimal args namespace for RolloutDataSource."""
    defaults = dict(
        rollout_global_dataset=True,
        prompt_data=None,
        hf_checkpoint="test",
        dump_details=None,
        rollout_max_prompt_len=100,
        input_key="prompt",
        multimodal_keys=None,
        label_key="answer",
        metadata_key=None,
        tool_key=None,
        apply_chat_template=False,
        apply_chat_template_kwargs=None,
        rollout_seed=42,
        rollout_shuffle=False,
        n_samples_per_prompt=1,
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import py_compile
    py_compile.compile(f"{REPO}/slime/rollout/data_source.py", doraise=True)
    py_compile.compile(f"{REPO}/slime/ray/rollout.py", doraise=True)


# [repo_ci] pass_to_pass — ruff lint check
def test_repo_ruff():
    """Repo's ruff lint check passes on modified files (pass_to_pass)."""
    subprocess.run(["pip", "install", "ruff", "-q"], check=True, capture_output=True)

    r = subprocess.run(
        ["ruff", "check", f"{REPO}/slime/rollout/data_source.py", f"{REPO}/slime/ray/rollout.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}{r.stderr}"


# [repo_ci] pass_to_pass — black format check
def test_repo_black():
    """Repo's black format check passes on modified files (pass_to_pass)."""
    subprocess.run(["pip", "install", "black", "-q"], check=True, capture_output=True)

    r = subprocess.run(
        ["black", "--check", f"{REPO}/slime/rollout/data_source.py", f"{REPO}/slime/ray/rollout.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Black format check failed:\n{r.stderr}"


# [repo_ci] pass_to_pass — isort import order check
def test_repo_isort():
    """Repo's isort import order check passes on modified files (pass_to_pass)."""
    subprocess.run(["pip", "install", "isort", "-q"], check=True, capture_output=True)

    r = subprocess.run(
        ["isort", "--check", "--profile=black",
         f"{REPO}/slime/rollout/data_source.py", f"{REPO}/slime/ray/rollout.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Isort check failed:\n{r.stderr}"


# [repo_ci] pass_to_pass — chunked GAE unit tests
def test_repo_chunked_gae():
    """Repo's chunked GAE unit tests pass (pass_to_pass)."""
    # Install dependencies
    subprocess.run(
        ["pip", "install", "torch", "--index-url", "https://download.pytorch.org/whl/cpu", "-q"],
        check=True, capture_output=True
    )
    subprocess.run(["pip", "install", "pytest", "numpy", "-q"], check=True, capture_output=True)
    subprocess.run(["pip", "install", "-e", REPO, "--no-deps", "-q"], check=True, capture_output=True)

    r = subprocess.run(
        ["python", "-m", "pytest", "tests/test_chunked_gae.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Chunked GAE tests failed:\n{r.stderr[-1000:]}"


# [repo_ci] pass_to_pass — autoflake unused import check
def test_repo_autoflake():
    """Repo's autoflake unused import check passes on modified files (pass_to_pass)."""
    subprocess.run(["pip", "install", "autoflake", "-q"], check=True, capture_output=True)

    r = subprocess.run(
        ["autoflake", "--remove-all-unused-imports", "--check",
         f"{REPO}/slime/rollout/data_source.py", f"{REPO}/slime/ray/rollout.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Autoflake check failed:\n{r.stderr}"


# [repo_ci] pass_to_pass — plugin contract tests
def test_repo_plugin_contracts():
    """Repo's plugin contract tests pass (pass_to_pass)."""
    # Install dependencies
    subprocess.run(["pip", "install", "pillow", "packaging", "pyyaml", "omegaconf", "tqdm",
                     "httpx", "pybase64", "pylatexenc", "sympy", "aiohttp", "-q"],
                   check=True, capture_output=True)
    subprocess.run(
        ["pip", "install", "torch", "--index-url", "https://download.pytorch.org/whl/cpu", "-q"],
        check=True, capture_output=True
    )
    subprocess.run(["pip", "install", "pytest", "numpy", "-q"], check=True, capture_output=True)
    subprocess.run(["pip", "install", "-e", REPO, "--no-deps", "-q"], check=True, capture_output=True)

    r = subprocess.run(
        ["python", "-m", "pytest", "tests/plugin_contracts/", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Plugin contract tests failed:\n{r.stderr[-1000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_constructor_none_prompt_data():
    """Constructor doesn't crash when prompt_data is None with global_dataset=True."""
    ns = _build_namespace()
    RolloutDataSource = ns["RolloutDataSource"]

    # Test with global_dataset=True and prompt_data=None — the exact crash scenario
    ds = RolloutDataSource(_make_args(prompt_data=None, rollout_global_dataset=True))
    assert ds.dataset is None, "dataset should be None when prompt_data is None"

    # Also works when global_dataset=False (should always skip dataset loading)
    ds2 = RolloutDataSource(_make_args(prompt_data=None, rollout_global_dataset=False))
    assert ds2.dataset is None, "dataset should be None when global_dataset is False"


# [pr_diff] fail_to_pass
def test_len_returns_zero_when_dataset_none():
    """__len__ returns 0 when dataset is None instead of crashing."""
    ns = _build_namespace()
    RolloutDataSource = ns["RolloutDataSource"]

    ds = object.__new__(RolloutDataSource)
    ds.dataset = None
    result = len(ds)
    assert result == 0, f"Expected 0 for None dataset, got {result}"
    assert isinstance(result, int), f"Expected int, got {type(result)}"


# [pr_diff] fail_to_pass
def test_load_no_crash_when_dataset_none_shuffle_true():
    """load() doesn't crash when dataset is None and shuffle is True."""
    ns = _build_namespace()
    RolloutDataSource = ns["RolloutDataSource"]

    tmpdir = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmpdir, "rollout"), exist_ok=True)
    cp_path = os.path.join(tmpdir, "rollout", "global_dataset_state_dict_0.pt")
    with open(cp_path, "w") as f:
        f.write("fake")

    ds = object.__new__(RolloutDataSource)
    ds.dataset = None
    ds.args = SimpleNamespace(
        rollout_global_dataset=True,
        rollout_shuffle=True,
        load=tmpdir,
    )
    ds.epoch_id = 0
    ds.sample_offset = 0
    ds.sample_group_index = 0
    ds.sample_index = 0
    ds.metadata = {}

    # Should not raise AttributeError from trying to call shuffle on None
    ds.load(rollout_id=0)


# [pr_diff] fail_to_pass
def test_router_disables_health_check():
    """_start_router sets router_args.disable_health_check = True."""
    # AST-only because: slime/ray/rollout.py imports ray, multiprocessing,
    # and sglang internals that are not installed in the test container
    import ast

    source = Path(f"{REPO}/slime/ray/rollout.py").read_text()
    tree = ast.parse(source)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_start_router":
            for child in ast.walk(node):
                if isinstance(child, ast.Assign):
                    for target in child.targets:
                        if (isinstance(target, ast.Attribute)
                                and target.attr == "disable_health_check"
                                and isinstance(child.value, ast.Constant)
                                and child.value.value is True):
                            found = True
            break

    assert found, "disable_health_check = True not found in _start_router"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_len_returns_correct_count_with_dataset():
    """__len__ returns actual dataset length when dataset exists (not hardcoded 0)."""
    ns = _build_namespace()
    RolloutDataSource = ns["RolloutDataSource"]
    _FakeDataset = ns["Dataset"]

    # Test with multiple different dataset sizes to prevent hardcoded return values
    for path in ["/data/a.jsonl", "/data/b.jsonl", "/data/cc.jsonl"]:
        ds = object.__new__(RolloutDataSource)
        ds.dataset = _FakeDataset(path)
        expected = len(ds.dataset)
        result = len(ds)
        assert result == expected, f"Expected {expected} for dataset from '{path}', got {result}"
        assert result > 0, f"Dataset length should be positive, got {result}"


# [pr_diff] pass_to_pass
def test_constructor_with_prompt_data_creates_dataset():
    """Constructor with valid prompt_data still creates the dataset normally."""
    ns = _build_namespace()
    RolloutDataSource = ns["RolloutDataSource"]

    for path in ["/fake/path.jsonl", "/data/train.json", "/other/set.jsonl"]:
        ds = RolloutDataSource(_make_args(prompt_data=path, rollout_global_dataset=True))
        assert ds.dataset is not None, f"dataset should exist when prompt_data={path}"
        assert len(ds) > 0, f"dataset length should be positive for prompt_data={path}"


# [pr_diff] pass_to_pass
def test_load_calls_shuffle_when_dataset_exists():
    """load() still calls dataset.shuffle when dataset IS present and shuffle is on."""
    ns = _build_namespace()
    RolloutDataSource = ns["RolloutDataSource"]
    _FakeDataset = ns["Dataset"]

    tmpdir = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmpdir, "rollout"), exist_ok=True)
    cp_path = os.path.join(tmpdir, "rollout", "global_dataset_state_dict_0.pt")
    with open(cp_path, "w") as f:
        f.write("fake")

    ds = object.__new__(RolloutDataSource)
    ds.dataset = _FakeDataset("/fake/data.jsonl")
    ds.args = SimpleNamespace(
        rollout_global_dataset=True,
        rollout_shuffle=True,
        load=tmpdir,
    )
    ds.epoch_id = 0
    ds.sample_offset = 0
    ds.sample_group_index = 0
    ds.sample_index = 0
    ds.metadata = {}

    ds.load(rollout_id=0)
    assert len(ds.dataset.shuffle_calls) == 1, (
        f"Expected shuffle to be called once, got {len(ds.dataset.shuffle_calls)} calls"
    )


# [pr_diff] pass_to_pass
def test_get_samples_when_dataset_none():
    """get_samples returns empty Sample objects when dataset is None."""
    ns = _build_namespace()
    RolloutDataSource = ns["RolloutDataSource"]

    for batch_size, n_samples in [(3, 2), (1, 1), (5, 3)]:
        ds = RolloutDataSource(_make_args(
            prompt_data=None, rollout_global_dataset=True,
            n_samples_per_prompt=n_samples,
        ))
        samples = ds.get_samples(batch_size)
        assert len(samples) == batch_size, (
            f"Expected {batch_size} sample groups, got {len(samples)}"
        )
        assert all(len(g) == n_samples for g in samples), (
            f"Each group should have n_samples_per_prompt={n_samples} items"
        )

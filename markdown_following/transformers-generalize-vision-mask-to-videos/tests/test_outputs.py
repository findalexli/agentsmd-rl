"""Behavior tests for huggingface/transformers#45185.

The PR refactors `token_type_ids_mask_function` (gemma3, git, paligemma) so
that the mask is produced from a single `group_ids` tensor instead of the
old `(token_type_ids, image_group_ids)` pair, generalizing the helper to
any non-negative vision group id (images today, videos in the future).

The tests exercise:
  - the new public signature (1 positional argument),
  - the inner-mask behavior the PR specifies,
  - cross-module consistency required by the repo's `# Copied from`
    convention,
  - that modular_gemma3.py was edited so `make fix-repo` regeneration is
    consistent.
"""

from __future__ import annotations

import importlib
import inspect
import subprocess
import sys
from pathlib import Path

import pytest
import torch

REPO = Path("/workspace/transformers")

GEMMA3_MOD = "transformers.models.gemma3.modeling_gemma3"
GIT_MOD = "transformers.models.git.modeling_git"
PALIGEMMA_MOD = "transformers.models.paligemma.modeling_paligemma"
ALL_MODS = [GEMMA3_MOD, GIT_MOD, PALIGEMMA_MOD]


def _import_fn(module_name: str):
    """Import (or re-import) the helper from `module_name` and return it.

    The fresh-import dance avoids stale module objects when solve.sh has
    edited files after the test process started.
    """
    if module_name in sys.modules:
        del sys.modules[module_name]
    module = importlib.import_module(module_name)
    return module.token_type_ids_mask_function


def _call_inner(inner, batch: int, head: int, q: int, kv: int) -> bool:
    """Invoke `inner_mask` with tensor indices (mirrors how vmap calls it)."""
    return bool(
        inner(
            torch.tensor(batch),
            torch.tensor(head),
            torch.tensor(q),
            torch.tensor(kv),
        )
    )


# ---------------------------------------------------------------------------
# Signature / public API
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("module_name", ALL_MODS)
def test_signature_takes_single_arg(module_name: str) -> None:
    fn = _import_fn(module_name)
    sig = inspect.signature(fn)
    assert len(sig.parameters) == 1, (
        f"{module_name}.token_type_ids_mask_function should accept exactly "
        f"one parameter (group_ids); got {list(sig.parameters)}"
    )


@pytest.mark.parametrize("module_name", ALL_MODS)
def test_callable_with_one_positional_arg(module_name: str) -> None:
    fn = _import_fn(module_name)
    group_ids = torch.tensor([[-1, -1, 0, 0, -1]])
    inner = fn(group_ids)
    assert callable(inner)


# ---------------------------------------------------------------------------
# Inner-mask behavior
# ---------------------------------------------------------------------------


_GROUPS_A = [-1, -1, 0, 0, 0, -1, 1, 1, -1]
_GROUPS_B = [0, 0, -1, 1, 1, 2, 2, -1]


@pytest.mark.parametrize(
    "group_ids,q,kv,expected",
    [
        (_GROUPS_A, 2, 3, True),  # same image group 0
        (_GROUPS_A, 3, 2, True),  # bidirectional within group 0
        (_GROUPS_A, 4, 4, True),  # self-attention within a group
        (_GROUPS_A, 6, 7, True),  # same image group 1
        (_GROUPS_A, 2, 6, False),  # different groups
        (_GROUPS_A, 7, 3, False),  # different groups (reversed)
        (_GROUPS_A, 0, 1, False),  # text-text
        (_GROUPS_A, 0, 3, False),  # text -> image
        (_GROUPS_A, 3, 5, False),  # image -> text
        (_GROUPS_B, 0, 1, True),  # vary shape, group 0
        (_GROUPS_B, 3, 4, True),  # group 1
        (_GROUPS_B, 5, 6, True),  # group 2 (would be a "video"-style group)
        (_GROUPS_B, 0, 3, False),  # group 0 vs 1
        (_GROUPS_B, 1, 5, False),  # group 0 vs 2
        (_GROUPS_B, 4, 7, False),  # image -> trailing text
    ],
)
@pytest.mark.parametrize("module_name", ALL_MODS)
def test_inner_mask_behavior(
    module_name: str, group_ids: list[int], q: int, kv: int, expected: bool
) -> None:
    fn = _import_fn(module_name)
    gids = torch.tensor([group_ids])
    inner = fn(gids)
    assert _call_inner(inner, 0, 0, q, kv) is expected


@pytest.mark.parametrize("module_name", ALL_MODS)
def test_inner_mask_handles_out_of_bounds_indices(module_name: str) -> None:
    """Static cache produces q_idx/kv_idx values that go past seq_length.
    The helper must return False for those without raising an indexing error.
    """
    fn = _import_fn(module_name)
    group_ids = torch.tensor([[-1, 0, 0, -1]])
    seq_len = 4
    inner = fn(group_ids)

    # q_idx beyond bounds — no attention regardless of kv
    assert _call_inner(inner, 0, 0, seq_len + 5, 1) is False
    # kv_idx beyond bounds — no attention regardless of q
    assert _call_inner(inner, 0, 0, 1, seq_len + 5) is False
    # Both beyond bounds
    assert _call_inner(inner, 0, 0, seq_len + 5, seq_len + 7) is False


@pytest.mark.parametrize("module_name", ALL_MODS)
def test_inner_mask_supports_batched_inputs(module_name: str) -> None:
    """Each row of group_ids is independent — masks must respect batch_idx."""
    fn = _import_fn(module_name)
    group_ids = torch.tensor(
        [
            [-1, 0, 0, -1, 1, 1, -1],
            [-1, -1, 0, 0, 0, -1, -1],
        ]
    )
    inner = fn(group_ids)

    # Batch 0: positions 1,2 are group 0; positions 4,5 are group 1
    assert _call_inner(inner, 0, 0, 1, 2) is True  # same group
    assert _call_inner(inner, 0, 0, 1, 4) is False  # different groups
    assert _call_inner(inner, 0, 0, 4, 5) is True  # same group 1
    # Batch 1: positions 2,3,4 are group 0
    assert _call_inner(inner, 1, 0, 2, 4) is True  # same group
    assert _call_inner(inner, 1, 0, 2, 1) is False  # group 0 vs text
    # Indexing into row 1 must not see row 0's groups: position 4,5 in row 1
    # is image vs text (False), while in row 0 it is group 1 vs group 1 (True).
    assert _call_inner(inner, 0, 0, 4, 5) != _call_inner(inner, 1, 0, 4, 5)


# ---------------------------------------------------------------------------
# Cross-module consistency
# ---------------------------------------------------------------------------


def test_git_signature_matches_gemma3() -> None:
    """git's helper is `# Copied from gemma3` — same signature is required."""
    g = inspect.signature(_import_fn(GEMMA3_MOD))
    git = inspect.signature(_import_fn(GIT_MOD))
    assert list(g.parameters) == list(git.parameters)


def test_paligemma_signature_matches_gemma3() -> None:
    g = inspect.signature(_import_fn(GEMMA3_MOD))
    pg = inspect.signature(_import_fn(PALIGEMMA_MOD))
    assert list(g.parameters) == list(pg.parameters)


def test_modular_gemma3_call_site_updated() -> None:
    """`modular_gemma3.py` is the source of truth for `modeling_gemma3.py`.

    `make fix-repo` regenerates the modeling file from the modular one,
    so the modular file must be updated to call the helper with one arg.
    """
    src = (REPO / "src/transformers/models/gemma3/modular_gemma3.py").read_text()
    assert "token_type_ids_mask_function(group_ids)" in src, (
        "modular_gemma3.py should call token_type_ids_mask_function with a "
        "single argument named group_ids; otherwise running the modular "
        "converter regenerates a stale modeling_gemma3.py."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass: repository CI checks
# ---------------------------------------------------------------------------


def test_repo_check_copies() -> None:
    """transformers' own check-copies utility — guards `# Copied from` blocks
    in git/modeling_git.py and other downstream copies.
    """
    r = subprocess.run(
        ["python3", "utils/checkers.py", "copies"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=str(REPO),
    )
    assert r.returncode == 0, (
        f"check-copies failed (rc={r.returncode}):\n"
        f"stdout:\n{r.stdout[-1500:]}\nstderr:\n{r.stderr[-500:]}"
    )


def _touched_files() -> list[str]:
    return [
        "src/transformers/models/gemma3/modeling_gemma3.py",
        "src/transformers/models/gemma3/modular_gemma3.py",
        "src/transformers/models/git/modeling_git.py",
        "src/transformers/models/paligemma/modeling_paligemma.py",
    ]


def test_repo_ruff_format() -> None:
    r = subprocess.run(
        ["ruff", "format", "--check", *_touched_files()],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
    )
    assert r.returncode == 0, (
        f"ruff format --check failed:\n{r.stdout}\n{r.stderr}"
    )


def test_repo_ruff_check() -> None:
    r = subprocess.run(
        ["ruff", "check", *_touched_files()],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout}\n{r.stderr}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_check_timestamps_verify_merge_commit_timestamp_is_older_t():
    """pass_to_pass | CI job 'Check timestamps' → step 'Verify `merge_commit` timestamp is older than the issue comment timestamp'"""
    r = subprocess.run(
        ["bash", "-lc", 'COMMENT_TIMESTAMP=$(date -d "${COMMENT_DATE}" +"%s")\necho "COMMENT_DATE: $COMMENT_DATE"\necho "COMMENT_TIMESTAMP: $COMMENT_TIMESTAMP"\nif [ $COMMENT_TIMESTAMP -le $PR_MERGE_COMMIT_TIMESTAMP ]; then\n  echo "Last commit on the pull request is newer than the issue comment triggering this run! Abort!";\n  exit -1;\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify `merge_commit` timestamp is older than the issue comment timestamp' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_get_tests_verify_merge_commit_sha():
    """pass_to_pass | CI job 'get-tests' → step 'Verify merge commit SHA'"""
    r = subprocess.run(
        ["bash", "-lc", 'PR_MERGE_SHA=$(git log -1 --format=%H)\nif [ $PR_MERGE_SHA != $VERIFIED_PR_MERGE_SHA ]; then\n  echo "The merged commit SHA is not the same as the verified one! Security issue detected, abort the workflow!";\n  exit -1;\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify merge commit SHA' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_get_tests_get_models_to_test():
    """pass_to_pass | CI job 'get-tests' → step 'Get models to test'"""
    r = subprocess.run(
        ["bash", "-lc", 'python -m pip install GitPython'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Get models to test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_get_tests_show_models_to_test():
    """pass_to_pass | CI job 'get-tests' → step 'Show models to test'"""
    r = subprocess.run(
        ["bash", "-lc", 'echo "$models"\necho "models=$models" >> $GITHUB_OUTPUT\necho "$quantizations"\necho "quantizations=$quantizations" >> $GITHUB_OUTPUT'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Show models to test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check___report_process_and_filter_reports():
    """pass_to_pass | CI job 'Check & Report' → step 'Process and filter reports'"""
    r = subprocess.run(
        ["bash", "-lc", "python3 << 'PYTHON_SCRIPT'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Process and filter reports' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
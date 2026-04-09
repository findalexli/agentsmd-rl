"""
Task: vllm-workspace-manager-size
Repo: vllm @ 062f1a2d706cfb631521461f6a7ad533cf69a4a8
PR:   38853

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/vllm"

# Helper: run a Python script that imports WorkspaceManager with CUDA mocks.
# workspace.py imports vllm.v1.worker.ubatching which needs torch.cuda,
# so we pre-populate sys.modules with a stub before the import.
_PREAMBLE = textwrap.dedent("""\
    import sys, types
    sys.path.insert(0, '/workspace/vllm')

    # Stub out CUDA-dependent modules before workspace import
    _ub = types.ModuleType('vllm.v1.worker.ubatching')
    _ub.dbo_current_ubatch_id = lambda: 0
    sys.modules['vllm.v1.worker.ubatching'] = _ub

    import torch
    from vllm.v1.worker.workspace import WorkspaceManager
""")


def _run_script(body: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Python test script with mocked CUDA deps."""
    full = _PREAMBLE + textwrap.dedent(body)
    return subprocess.run(
        ["python3", "-c", full],
        capture_output=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without errors."""
    import py_compile
    py_compile.compile(f"{REPO}/vllm/v1/worker/workspace.py", doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_workspace_default_size():
    """Default WorkspaceManager (num_ubatches=None) must have exactly 1 slot."""
    r = _run_script("""\
        wm = WorkspaceManager(torch.device('cpu'), num_ubatches=None)
        n = len(wm._current_workspaces)
        assert n == 1, f"Default num_ubatches=None: expected 1 slot, got {n}"
    """)
    assert r.returncode == 0, f"Failed:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_workspace_custom_size():
    """WorkspaceManager with num_ubatches=3 must have exactly 3 slots."""
    r = _run_script("""\
        wm = WorkspaceManager(torch.device('cpu'), num_ubatches=3)
        n = len(wm._current_workspaces)
        assert n == 3, f"num_ubatches=3: expected 3 slots, got {n}"
    """)
    assert r.returncode == 0, f"Failed:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_workspace_all_slots_accessible():
    """All slots in _current_workspaces must be indexable without IndexError."""
    r = _run_script("""\
        for num in [1, 4, 5]:
            wm = WorkspaceManager(torch.device('cpu'), num_ubatches=num)
            # Access every slot — must not raise IndexError
            for i in range(num):
                _ = wm._current_workspaces[i]
            assert len(wm._current_workspaces) == num, \\
                f"num_ubatches={num}: expected {num} slots, got {len(wm._current_workspaces)}"
    """)
    assert r.returncode == 0, f"Failed:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_workspace_manager_has_methods():
    """WorkspaceManager must have real lock/unlock/get_simultaneous methods."""
    r = _run_script("""\
        wm = WorkspaceManager(torch.device('cpu'), num_ubatches=2)
        # Verify key methods exist and are callable
        assert callable(getattr(wm, 'lock', None)), "Missing lock method"
        assert callable(getattr(wm, 'unlock', None)), "Missing unlock method"
        assert callable(getattr(wm, 'get_simultaneous', None)), "Missing get_simultaneous method"
        assert callable(getattr(wm, '_ensure_workspace_size', None)), "Missing _ensure_workspace_size method"
        # Verify lock/unlock work
        wm.lock()
        assert wm.is_locked()
        wm.unlock()
        assert not wm.is_locked()
    """)
    assert r.returncode == 0, f"Failed:\n{r.stderr.decode()}"

"""Behavioral checks for mfc-add-claudemd-and-clauderules-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mfc")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/common-pitfalls.md')
    assert '- Tests are generated **programmatically** in `toolchain/mfc/test/cases.py`, not standalone files' in text, "expected to find: " + '- Tests are generated **programmatically** in `toolchain/mfc/test/cases.py`, not standalone files'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/common-pitfalls.md')
    assert '- Index ranges depend on `model_eqns` and enabled features (set in `m_global_parameters.fpp`):' in text, "expected to find: " + '- Index ranges depend on `model_eqns` and enabled features (set in `m_global_parameters.fpp`):'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/common-pitfalls.md')
    assert '- `src/common/` is shared by ALL three executables (pre_process, simulation, post_process)' in text, "expected to find: " + '- `src/common/` is shared by ALL three executables (pre_process, simulation, post_process)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/fortran-conventions.md')
    assert '- `dsqrt`, `dexp`, `dlog`, `dble`, `dabs`, `dcos`, `dsin`, `dtan`, etc. → use generic intrinsics' in text, "expected to find: " + '- `dsqrt`, `dexp`, `dlog`, `dble`, `dabs`, `dcos`, `dsin`, `dtan`, etc. → use generic intrinsics'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/fortran-conventions.md')
    assert '- Explicit `intent(in)`, `intent(out)`, or `intent(inout)` on ALL subroutine/function arguments' in text, "expected to find: " + '- Explicit `intent(in)`, `intent(out)`, or `intent(inout)` on ALL subroutine/function arguments'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/fortran-conventions.md')
    assert '- Fortran-side runtime validation also exists in `m_checker*.fpp` files using `@:PROHIBIT`' in text, "expected to find: " + '- Fortran-side runtime validation also exists in `m_checker*.fpp` files using `@:PROHIBIT`'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/gpu-and-mpi.md')
    assert '- `@:ACC_SETUP_VFs(...)` / `@:ACC_SETUP_SFs(...)` — GPU pointer setup for vector/scalar fields' in text, "expected to find: " + '- `@:ACC_SETUP_VFs(...)` / `@:ACC_SETUP_SFs(...)` — GPU pointer setup for vector/scalar fields'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/gpu-and-mpi.md')
    assert '- `omp_macros.fpp` — OpenMP target offload `OMP_*` implementations (do not call directly)' in text, "expected to find: " + '- `omp_macros.fpp` — OpenMP target offload `OMP_*` implementations (do not call directly)'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/gpu-and-mpi.md')
    assert '- `shared_parallel_macros.fpp` — Shared helpers (collapse, private, reduction generators)' in text, "expected to find: " + '- `shared_parallel_macros.fpp` — Shared helpers (collapse, private, reduction generators)'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/parameter-system.md')
    assert 'MFC has ~3,400 simulation parameters defined in Python and read by Fortran via namelist files.' in text, "expected to find: " + 'MFC has ~3,400 simulation parameters defined in Python and read by Fortran via namelist files.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/parameter-system.md')
    assert 'These are compiled into the binary, so syntax errors cause build failures, not runtime errors.' in text, "expected to find: " + 'These are compiled into the binary, so syntax errors cause build failures, not runtime errors.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/parameter-system.md')
    assert 'YOU MUST update the first 3 locations. Missing any causes silent failures or compile errors.' in text, "expected to find: " + 'YOU MUST update the first 3 locations. Missing any causes silent failures or compile errors.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '* Only `simulation` (plus its `common` dependencies) is GPU-accelerated via **OpenACC** or **OpenMP target offload** (`--gpu acc` or `--gpu mp`). GPU code uses backend-agnostic `GPU_*` Fypp macros (in' in text, "expected to find: " + '* Only `simulation` (plus its `common` dependencies) is GPU-accelerated via **OpenACC** or **OpenMP target offload** (`--gpu acc` or `--gpu mp`). GPU code uses backend-agnostic `GPU_*` Fypp macros (in'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert './mfc.sh build -j 8                        # Build all 3 targets (pre_process, simulation, post_process)' in text, "expected to find: " + './mfc.sh build -j 8                        # Build all 3 targets (pre_process, simulation, post_process)'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'NEVER use double-precision intrinsics: `dsqrt`, `dexp`, `dlog`, `dble`, `dabs`, `real(8)`, `real(4)`.' in text, "expected to find: " + 'NEVER use double-precision intrinsics: `dsqrt`, `dexp`, `dlog`, `dble`, `dabs`, `real(8)`, `real(4)`.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert './mfc.sh test --generate --only <feature>  # Regenerate golden files after intentional output change' in text, "expected to find: " + './mfc.sh test --generate --only <feature>  # Regenerate golden files after intentional output change'[:80]


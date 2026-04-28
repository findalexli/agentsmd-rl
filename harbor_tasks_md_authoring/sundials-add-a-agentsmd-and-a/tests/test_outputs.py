"""Behavioral checks for sundials-add-a-agentsmd-and-a (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sundials")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/building/SKILL.md')
    assert 'description: Build, install, and test SUNDIALS from source as an end user or as a SUNDIALS developer. Use when a request involves configuring CMake, selecting compilers/options (MPI, GPU backends, For' in text, "expected to find: " + 'description: Build, install, and test SUNDIALS from source as an end user or as a SUNDIALS developer. Use when a request involves configuring CMake, selecting compilers/options (MPI, GPU backends, For'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/building/SKILL.md')
    assert '- Set `SUNDIALS_DIR` to the SUNDIALS install tree (or to the installed CMake package dir) and use `find_package(SUNDIALS REQUIRED)`; link with exported targets like `SUNDIALS::cvode`. If you link via ' in text, "expected to find: " + '- Set `SUNDIALS_DIR` to the SUNDIALS install tree (or to the installed CMake package dir) and use `find_package(SUNDIALS REQUIRED)`; link with exported targets like `SUNDIALS::cvode`. If you link via '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/building/SKILL.md')
    assert '- If tests that compare against “answer files” fail due to platform differences, consider rerunning with a locally-generated answer directory using `SUNDIALS_TEST_ANSWER_DIR` (see `doc/superbuild/sour' in text, "expected to find: " + '- If tests that compare against “answer files” fail due to platform differences, consider rerunning with a locally-generated answer directory using `SUNDIALS_TEST_ANSWER_DIR` (see `doc/superbuild/sour'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/new-module/SKILL.md')
    assert 'description: Add a new SUNDIALS module (e.g., NVECTOR_*, SUNMATRIX_*, SUNLINSOL_*, SUNNONLINSOL_*, SUNMEMORY_*, or a new shared component) including source/header layout, CMake wiring, enable/disable ' in text, "expected to find: " + 'description: Add a new SUNDIALS module (e.g., NVECTOR_*, SUNMATRIX_*, SUNLINSOL_*, SUNNONLINSOL_*, SUNMEMORY_*, or a new shared component) including source/header layout, CMake wiring, enable/disable '[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/new-module/SKILL.md')
    assert 'If you implement a module as an `INTERFACE` library (no `sundials_add_library`), you must manually add it to `_SUNDIALS_INSTALLED_COMPONENTS` so that `find_package(SUNDIALS COMPONENTS ...)` can work.' in text, "expected to find: " + 'If you implement a module as an `INTERFACE` library (no `sundials_add_library`), you must manually add it to `_SUNDIALS_INSTALLED_COMPONENTS` so that `find_package(SUNDIALS COMPONENTS ...)` can work.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/new-module/SKILL.md')
    assert 'For categories that are listed in `src/CMakeLists.txt` (e.g., `nvector`, `sunmatrix`, `sunlinsol`, …), you usually only need to change the category-level `CMakeLists.txt`.' in text, "expected to find: " + 'For categories that are listed in `src/CMakeLists.txt` (e.g., `nvector`, `sunmatrix`, `sunlinsol`, …), you usually only need to change the category-level `CMakeLists.txt`.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `src/` and `include/`: core SUNDIALS C/C++ sources and public headers, organized by package (e.g., `cvode/`, `ida/`) or module (e.g., `nvector/`, `sunlinsol/`).' in text, "expected to find: " + '- `src/` and `include/`: core SUNDIALS C/C++ sources and public headers, organized by package (e.g., `cvode/`, `ida/`) or module (e.g., `nvector/`, `sunlinsol/`).'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- PRs should include: what/why, how it was tested, and updates to `CHANGELOG.md` and `doc/shared/RecentChanges.rst` when user-visible.' in text, "expected to find: " + '- PRs should include: what/why, how it was tested, and updates to `CHANGELOG.md` and `doc/shared/RecentChanges.rst` when user-visible.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Keep new features paired with targeted tests; update answer files under `test/answers/` only when output changes are intended.' in text, "expected to find: " + '- Keep new features paired with targeted tests; update answer files under `test/answers/` only when output changes are intended.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


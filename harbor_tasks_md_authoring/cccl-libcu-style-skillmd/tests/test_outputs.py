"""Behavioral checks for cccl-libcu-style-skillmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cccl")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/licudacxx-style/SKILL.md')
    assert '- All calls to free functions must be fully qualified starting from the global namespace, e.g. `::cuda::ceil_div`. This includes calls to functions defined in the same namespace, e.g. inside `cuda::`,' in text, "expected to find: " + '- All calls to free functions must be fully qualified starting from the global namespace, e.g. `::cuda::ceil_div`. This includes calls to functions defined in the same namespace, e.g. inside `cuda::`,'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/licudacxx-style/SKILL.md')
    assert '- This includes standard integer type aliases (`::cuda::std::size_t`, `::cuda::std::uintptr_t`, `::cuda::std::int32_t`, etc.) and any other `cuda::std` or standard library types. A local `using` decla' in text, "expected to find: " + '- This includes standard integer type aliases (`::cuda::std::size_t`, `::cuda::std::uintptr_t`, `::cuda::std::int32_t`, etc.) and any other `cuda::std` or standard library types. A local `using` decla'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/licudacxx-style/SKILL.md')
    assert '- All variables that are not modified must use `const`. This includes variables initialized by casts (`static_cast`, `reinterpret_cast`, `bit_cast`), function return values, and loop-invariant computa' in text, "expected to find: " + '- All variables that are not modified must use `const`. This includes variables initialized by casts (`static_cast`, `reinterpret_cast`, `bit_cast`), function return values, and loop-invariant computa'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/licudacxx-style/SKILL.md')
    assert 'description: Make the code in libcudacxx/include, cudax/include compliant with the coding style' in text, "expected to find: " + 'description: Make the code in libcudacxx/include, cudax/include compliant with the coding style'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/licudacxx-style/SKILL.md')
    assert 'The skill content is in .agent/skills/licudacxx-style/SKILL.md' in text, "expected to find: " + 'The skill content is in .agent/skills/licudacxx-style/SKILL.md'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/licudacxx-style/SKILL.md')
    assert 'name: libcudacxx-style' in text, "expected to find: " + 'name: libcudacxx-style'[:80]


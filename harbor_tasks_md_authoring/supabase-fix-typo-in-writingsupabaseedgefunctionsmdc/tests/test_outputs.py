"""Behavioral checks for supabase-fix-typo-in-writingsupabaseedgefunctionsmdc (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/supabase")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/ui-library/registry/default/ai-editor-rules/writing-supabase-edge-functions.mdc')
    assert "3. Do NOT use bare specifiers when importing dependencies. If you need to use an external dependency, make sure it's prefixed with either `npm:` or `jsr:`. For example, `@supabase/supabase-js` should " in text, "expected to find: " + "3. Do NOT use bare specifiers when importing dependencies. If you need to use an external dependency, make sure it's prefixed with either `npm:` or `jsr:`. For example, `@supabase/supabase-js` should "[:80]


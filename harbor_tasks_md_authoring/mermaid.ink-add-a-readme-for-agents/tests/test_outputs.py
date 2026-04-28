"""Behavioral checks for mermaid.ink-add-a-readme-for-agents (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mermaid.ink")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**[Render flow](https://mermaid.ink/img/pako:eNpNUttum0AQ_ZXRvtamJvEF89CK-J7YbpSklVrww4odG2RgybIbxwX_e9cLVEZCYuacmTOcmZKEnCFxyT7hpzCiQsLbNMhAP57_wpVEiGjGEhQ76Ha_wUM5oWGEoN_weKmJD1ekWsaygon_glKJDMIriwE' in text, "expected to find: " + '**[Render flow](https://mermaid.ink/img/pako:eNpNUttum0AQ_ZXRvtamJvEF89CK-J7YbpSklVrww4odG2RgybIbxwX_e9cLVEZCYuacmTOcmZKEnCFxyT7hpzCiQsLbNMhAP57_wpVEiGjGEhQ76Ha_wUM5oWGEoN_weKmJD1ekWsaygon_glKJDMIriwE'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Database** (optional, `ENABLE_DATABASE=true`): Pool max 1 for advisory locks, SHA256 cache keys, exports `connect/disconnect/readAsset/insertAsset/updateAsset/tryAcquireLock/releaseLock`' in text, "expected to find: " + '**Database** (optional, `ENABLE_DATABASE=true`): Pool max 1 for advisory locks, SHA256 cache keys, exports `connect/disconnect/readAsset/insertAsset/updateAsset/tryAcquireLock/releaseLock`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Route handlers** (`img.js`, `svg.js`, `pdf.js`): Export default wrapped in `renderImgOrSvg`, receive `(ctx, cacheKey, page, size)`, use Puppeteer API, update cache, set response.' in text, "expected to find: " + '**Route handlers** (`img.js`, `svg.js`, `pdf.js`): Export default wrapped in `renderImgOrSvg`, receive `(ctx, cacheKey, page, size)`, use Puppeteer API, update cache, set response.'[:80]


"""Behavioral checks for wordpress-playground-ai-improve-agentsmd-configuration (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/wordpress-playground")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '3. **Supporting packages**: `packages/nx-extensions/` (custom NX executors), `packages/docs/` (Docusaurus documentation site), `packages/meta/` (ESLint plugin, changelog tooling), `packages/bun-extens' in text, "expected to find: " + '3. **Supporting packages**: `packages/nx-extensions/` (custom NX executors), `packages/docs/` (Docusaurus documentation site), `packages/meta/` (ESLint plugin, changelog tooling), `packages/bun-extens'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Node.js version**: This project requires a specific Node.js version (defined in `.nvmrc` and the `engines` field in root `package.json`). Before running any commands, ensure the correct version is a' in text, "expected to find: " + '**Node.js version**: This project requires a specific Node.js version (defined in `.nvmrc` and the `engines` field in root `package.json`). Before running any commands, ensure the correct version is a'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'WordPress Playground is a monorepo that runs WordPress and PHP entirely in WebAssembly, enabling zero-setup WordPress environments in browsers, Node.js, and CLIs. The project consists of two major arc' in text, "expected to find: " + 'WordPress Playground is a monorepo that runs WordPress and PHP entirely in WebAssembly, enabling zero-setup WordPress environments in browsers, Node.js, and CLIs. The project consists of two major arc'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/php-wasm/compile/AGENTS.md')
    assert '- **Asyncify** — Older approach. Transforms synchronous C code to be pausable/resumable.' in text, "expected to find: " + '- **Asyncify** — Older approach. Transforms synchronous C code to be pausable/resumable.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/php-wasm/compile/AGENTS.md')
    assert 'build, extracts WASM output. Invoked by NX targets in `php-wasm-web`/`php-wasm-node`.' in text, "expected to find: " + 'build, extracts WASM output. Invoked by NX targets in `php-wasm-web`/`php-wasm-node`.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/php-wasm/compile/AGENTS.md')
    assert '- `php/Dockerfile` — The main PHP compilation. ~2400 lines. Accepts 20+ `--build-arg`' in text, "expected to find: " + '- `php/Dockerfile` — The main PHP compilation. ~2400 lines. Accepts 20+ `--build-arg`'[:80]


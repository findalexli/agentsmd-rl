"""Behavioral checks for ai-setup-fixskills-correct-writerspattern-syncexport-signatu (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai-setup")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/writers-pattern/SKILL.md')
    assert '- **"ENOENT: no such file or directory"** — Ensure `fs.mkdirSync(parentDir, { recursive: true })` is called BEFORE `fs.writeFileSync(filePath, ...)`. See `src/writers/claude/index.ts` for correct orde' in text, "expected to find: " + '- **"ENOENT: no such file or directory"** — Ensure `fs.mkdirSync(parentDir, { recursive: true })` is called BEFORE `fs.writeFileSync(filePath, ...)`. See `src/writers/claude/index.ts` for correct orde'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/writers-pattern/SKILL.md')
    assert '- **"Skill file has no frontmatter"** — Frontmatter format must be `---\\nname: ...\\ndescription: ...\\n---\\n<content>` (no extra blank lines). Compare with `src/writers/claude/index.ts` lines 40–48.' in text, "expected to find: " + '- **"Skill file has no frontmatter"** — Frontmatter format must be `---\\nname: ...\\ndescription: ...\\n---\\n<content>` (no extra blank lines). Compare with `src/writers/claude/index.ts` lines 40–48.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/writers-pattern/SKILL.md')
    assert '- **"TypeError: write{Platform}Config is not a function"** — Verify the function is exported: `export function write{Platform}Config(...)`. Missing `export` is a common mistake.' in text, "expected to find: " + '- **"TypeError: write{Platform}Config is not a function"** — Verify the function is exported: `export function write{Platform}Config(...)`. Missing `export` is a common mistake.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/writers-pattern/SKILL.md')
    assert '2. Implement `export function writeGithubCopilotConfig(config: GithubCopilotConfig): string[]` — synchronous, writes `.github/copilot-instructions.md` and `.github/instructions/` files' in text, "expected to find: " + '2. Implement `export function writeGithubCopilotConfig(config: GithubCopilotConfig): string[]` — synchronous, writes `.github/copilot-instructions.md` and `.github/instructions/` files'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/writers-pattern/SKILL.md')
    assert '- Each writer lives in `src/writers/{platform}/index.ts` with a named export `write{Platform}Config(config: {PlatformConfig}): string[]`' in text, "expected to find: " + '- Each writer lives in `src/writers/{platform}/index.ts` with a named export `write{Platform}Config(config: {PlatformConfig}): string[]`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/writers-pattern/SKILL.md')
    assert 'Verify: function is synchronous; every `fs.writeFileSync` is preceded by `fs.mkdirSync`; every written path is in the returned array.' in text, "expected to find: " + 'Verify: function is synchronous; every `fs.writeFileSync` is preceded by `fs.mkdirSync`; every written path is in the returned array.'[:80]


"""Behavioral checks for openhuman-choreclauderules-add-paths-frontmatter-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openhuman")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/03-platform-setup-windows.md')
    assert '- "app/src-tauri/**"' in text, "expected to find: " + '- "app/src-tauri/**"'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/03-platform-setup-windows.md')
    assert '- "src-tauri/**"' in text, "expected to find: " + '- "src-tauri/**"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/04-platform-setup-macos.md')
    assert '- "app/src-tauri/**"' in text, "expected to find: " + '- "app/src-tauri/**"'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/04-platform-setup-macos.md')
    assert '- "src-tauri/**"' in text, "expected to find: " + '- "src-tauri/**"'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/05-platform-setup-android.md')
    assert '- "app/src-tauri/gen/android/**"' in text, "expected to find: " + '- "app/src-tauri/gen/android/**"'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/05-platform-setup-android.md')
    assert '- "src-tauri/gen/android/**"' in text, "expected to find: " + '- "src-tauri/gen/android/**"'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/06-platform-setup-ios.md')
    assert '- "app/src-tauri/gen/apple/**"' in text, "expected to find: " + '- "app/src-tauri/gen/apple/**"'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/06-platform-setup-ios.md')
    assert '- "src-tauri/gen/apple/**"' in text, "expected to find: " + '- "src-tauri/gen/apple/**"'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/07-rust-backend-guide.md')
    assert '- "app/src-tauri/**"' in text, "expected to find: " + '- "app/src-tauri/**"'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/07-rust-backend-guide.md')
    assert '- "**/Cargo.toml"' in text, "expected to find: " + '- "**/Cargo.toml"'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/07-rust-backend-guide.md')
    assert '- "src-tauri/**"' in text, "expected to find: " + '- "src-tauri/**"'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/08-frontend-guide.md')
    assert '- "app/vite.config.*"' in text, "expected to find: " + '- "app/vite.config.*"'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/08-frontend-guide.md')
    assert '- "app/src/**"' in text, "expected to find: " + '- "app/src/**"'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/08-frontend-guide.md')
    assert '- "app/*.tsx"' in text, "expected to find: " + '- "app/*.tsx"'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/09-permissions-capabilities.md')
    assert '- "**/capabilities/**"' in text, "expected to find: " + '- "**/capabilities/**"'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/09-permissions-capabilities.md')
    assert '- "**/tauri.conf.json"' in text, "expected to find: " + '- "**/tauri.conf.json"'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/12-design-system.md')
    assert '- "**/tailwind.config.*"' in text, "expected to find: " + '- "**/tailwind.config.*"'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/12-design-system.md')
    assert '- "app/src/**/*.tsx"' in text, "expected to find: " + '- "app/src/**/*.tsx"'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/12-design-system.md')
    assert '- "app/src/**/*.css"' in text, "expected to find: " + '- "app/src/**/*.css"'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/13-backend-auth-implementation.md')
    assert '- "app/src-tauri/src/lib.rs"' in text, "expected to find: " + '- "app/src-tauri/src/lib.rs"'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/13-backend-auth-implementation.md')
    assert '- "**/*auth*.tsx"' in text, "expected to find: " + '- "**/*auth*.tsx"'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/13-backend-auth-implementation.md')
    assert '- "**/*auth*.ts"' in text, "expected to find: " + '- "**/*auth*.ts"'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/14-deep-link-platform-guide.md')
    assert '- "**/tauri.conf.json"' in text, "expected to find: " + '- "**/tauri.conf.json"'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/14-deep-link-platform-guide.md')
    assert '- "app/src-tauri/**"' in text, "expected to find: " + '- "app/src-tauri/**"'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/14-deep-link-platform-guide.md')
    assert '- "**/*deep*link*"' in text, "expected to find: " + '- "**/*deep*link*"'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/15-settings-modal-system.md')
    assert '- "app/src/components/settings/**"' in text, "expected to find: " + '- "app/src/components/settings/**"'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/16-macos-background-execution.md')
    assert '- "app/src-tauri/src/lib.rs"' in text, "expected to find: " + '- "app/src-tauri/src/lib.rs"'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/16-macos-background-execution.md')
    assert '- "**/tauri.conf.json"' in text, "expected to find: " + '- "**/tauri.conf.json"'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/16-macos-background-execution.md')
    assert '- "**/Info.plist"' in text, "expected to find: " + '- "**/Info.plist"'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/17-skills-memory-inference-flow.md')
    assert '- "app/src/providers/SkillProvider.tsx"' in text, "expected to find: " + '- "app/src/providers/SkillProvider.tsx"'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/17-skills-memory-inference-flow.md')
    assert '- "app/src/lib/ai/**"' in text, "expected to find: " + '- "app/src/lib/ai/**"'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/17-skills-memory-inference-flow.md')
    assert '- "src/openhuman/**"' in text, "expected to find: " + '- "src/openhuman/**"'[:80]


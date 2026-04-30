"""Behavioral checks for aionui-choreskills-enhance-prreview-dimensions-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/aionui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-fix/SKILL.md')
    assert 'The `electron-rebuild` step recompiles native modules (e.g., `better-sqlite3`) against the Electron version used by this project, ensuring ABI compatibility.' in text, "expected to find: " + 'The `electron-rebuild` step recompiles native modules (e.g., `better-sqlite3`) against the Electron version used by this project, ensuring ABI compatibility.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-fix/SKILL.md')
    assert '**All paths — symlink node_modules and rebuild native modules:**' in text, "expected to find: " + '**All paths — symlink node_modules and rebuild native modules:**'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-fix/SKILL.md')
    assert 'npx electron-rebuild -f -w better-sqlite3 2>/dev/null || true' in text, "expected to find: " + 'npx electron-rebuild -f -w better-sqlite3 2>/dev/null || true'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-review/SKILL.md')
    assert '- **Electron 安全配置** — 若 PR 涉及 `electron-builder.yml`、`entitlements.plist` 或 `electron.vite.config.ts` 中的 Electron 配置：(1) sandbox/nodeIntegration/contextIsolation 设置是否被弱化；(2) entitlements 是否授权过度；(3) 签名' in text, "expected to find: " + '- **Electron 安全配置** — 若 PR 涉及 `electron-builder.yml`、`entitlements.plist` 或 `electron.vite.config.ts` 中的 Electron 配置：(1) sandbox/nodeIntegration/contextIsolation 设置是否被弱化；(2) entitlements 是否授权过度；(3) 签名'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-review/SKILL.md')
    assert '- **IPC bridge / preload** — 若 PR 涉及 `src/preload.ts` 或 IPC channel 定义：(1) 是否暴露了不必要的 Node.js API 给 renderer；(2) 所有暴露的 API 是否有输入校验；(3) renderer 是否能在无授权情况下触发特权操作。暴露不安全 API 标记为 CRITICAL。' in text, "expected to find: " + '- **IPC bridge / preload** — 若 PR 涉及 `src/preload.ts` 或 IPC channel 定义：(1) 是否暴露了不必要的 Node.js API 给 renderer；(2) 所有暴露的 API 是否有输入校验；(3) renderer 是否能在无授权情况下触发特权操作。暴露不安全 API 标记为 CRITICAL。'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-review/SKILL.md')
    assert '- **数据库变更** — 若 PR 涉及 migration 文件或数据库 schema：(1) migration 是否正确（字段类型、约束、索引、默认值、可回滚性）；(2) 变更是否合理且与 PR 目标一致；(3) 对现有数据是否有丢失风险；(4) migration 顺序和依赖是否正确。不正确的 migration 标记为 CRITICAL。' in text, "expected to find: " + '- **数据库变更** — 若 PR 涉及 migration 文件或数据库 schema：(1) migration 是否正确（字段类型、约束、索引、默认值、可回滚性）；(2) 变更是否合理且与 PR 目标一致；(3) 对现有数据是否有丢失风险；(4) migration 顺序和依赖是否正确。不正确的 migration 标记为 CRITICAL。'[:80]


"""Behavioral checks for cli-featwhiteboard-pin-whiteboardcli-to-029 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/SKILL.md')
    assert 'npx -y @larksuite/whiteboard-cli@^0.2.9 -i <产物文件> --to openapi --format json \\' in text, "expected to find: " + 'npx -y @larksuite/whiteboard-cli@^0.2.9 -i <产物文件> --to openapi --format json \\'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/SKILL.md')
    assert '> - 运行 `npx -y @larksuite/whiteboard-cli@^0.2.9 -v`，确认可用，无需询问用户。' in text, "expected to find: " + '> - 运行 `npx -y @larksuite/whiteboard-cli@^0.2.9 -v`，确认可用，无需询问用户。'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/SKILL.md')
    assert '> - 运行 `lark-cli --version`，确认可用，无需询问用户。' in text, "expected to find: " + '> - 运行 `lark-cli --version`，确认可用，无需询问用户。'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/lark-whiteboard-update.md')
    assert 'npx -y @larksuite/whiteboard-cli@^0.2.9 -i <DSL 文件> --to openapi --format json -o ./temp.json' in text, "expected to find: " + 'npx -y @larksuite/whiteboard-cli@^0.2.9 -i <DSL 文件> --to openapi --format json -o ./temp.json'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/lark-whiteboard-update.md')
    assert 'npx -y @larksuite/whiteboard-cli@^0.2.9 -i <产物文件> --to openapi --format json \\' in text, "expected to find: " + 'npx -y @larksuite/whiteboard-cli@^0.2.9 -i <产物文件> --to openapi --format json \\'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/layout.md')
    assert 'npx -y @larksuite/whiteboard-cli@^0.2.9 -i skeleton.json -o step1.png -l coords.json' in text, "expected to find: " + 'npx -y @larksuite/whiteboard-cli@^0.2.9 -i skeleton.json -o step1.png -l coords.json'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/schema.md')
    assert 'name: string;                 // 图标名称，从 npx -y @larksuite/whiteboard-cli@^0.2.9 --icons 输出中选取' in text, "expected to find: " + 'name: string;                 // 图标名称，从 npx -y @larksuite/whiteboard-cli@^0.2.9 --icons 输出中选取'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/schema.md')
    assert 'npx -y @larksuite/whiteboard-cli@^0.2.9 --icons' in text, "expected to find: " + 'npx -y @larksuite/whiteboard-cli@^0.2.9 --icons'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/routes/dsl.md')
    assert '- 渲染 PNG（仅用于预览验证，不是最终产物）：npx -y @larksuite/whiteboard-cli@^0.2.9 -i diagram.json -o diagram.png' in text, "expected to find: " + '- 渲染 PNG（仅用于预览验证，不是最终产物）：npx -y @larksuite/whiteboard-cli@^0.2.9 -i diagram.json -o diagram.png'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/routes/dsl.md')
    assert 'npx -y @larksuite/whiteboard-cli@^0.2.9 -i diagram.json --to openapi --format json \\' in text, "expected to find: " + 'npx -y @larksuite/whiteboard-cli@^0.2.9 -i diagram.json --to openapi --format json \\'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/routes/dsl.md')
    assert '- 推荐使用图标让图表更直观，运行 `npx -y @larksuite/whiteboard-cli@^0.2.9 --icons` 查看可用图标' in text, "expected to find: " + '- 推荐使用图标让图表更直观，运行 `npx -y @larksuite/whiteboard-cli@^0.2.9 --icons` 查看可用图标'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/routes/mermaid.md')
    assert 'npx -y @larksuite/whiteboard-cli@^0.2.9 -i diagram.mmd --to openapi --format json \\' in text, "expected to find: " + 'npx -y @larksuite/whiteboard-cli@^0.2.9 -i diagram.mmd --to openapi --format json \\'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/routes/mermaid.md')
    assert 'npx -y @larksuite/whiteboard-cli@^0.2.9 -i diagram.mmd -o diagram.png' in text, "expected to find: " + 'npx -y @larksuite/whiteboard-cli@^0.2.9 -i diagram.mmd -o diagram.png'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/routes/svg.md')
    assert '导出     npx -y @larksuite/whiteboard-cli@^0.2.9 -i <dir>/diagram.svg -f svg --to openapi --format json > <dir>/diagram.json' in text, "expected to find: " + '导出     npx -y @larksuite/whiteboard-cli@^0.2.9 -i <dir>/diagram.svg -f svg --to openapi --format json > <dir>/diagram.json'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/routes/svg.md')
    assert '`npx -y @larksuite/whiteboard-cli@^0.2.9 --check` 检测 `text-overflow` 和 `node-overlap`, 并结合视觉效果(查看 PNG)进行调整' in text, "expected to find: " + '`npx -y @larksuite/whiteboard-cli@^0.2.9 --check` 检测 `text-overflow` 和 `node-overlap`, 并结合视觉效果(查看 PNG)进行调整'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/routes/svg.md')
    assert '渲染     npx -y @larksuite/whiteboard-cli@^0.2.9 -i <dir>/diagram.svg -o <dir>/diagram.png -f svg' in text, "expected to find: " + '渲染     npx -y @larksuite/whiteboard-cli@^0.2.9 -i <dir>/diagram.svg -o <dir>/diagram.png -f svg'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/scenes/bar-chart.md')
    assert '- **脚本生成坐标**（推荐）：用 .cjs 脚本计算柱体位置和高度，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.9` 渲染' in text, "expected to find: " + '- **脚本生成坐标**（推荐）：用 .cjs 脚本计算柱体位置和高度，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.9` 渲染'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/scenes/fishbone.md')
    assert '- **脚本生成坐标**（必须）：用 .cjs 脚本通过三角函数计算鱼骨坐标，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.9` 渲染' in text, "expected to find: " + '- **脚本生成坐标**（必须）：用 .cjs 脚本通过三角函数计算鱼骨坐标，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.9` 渲染'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/scenes/flywheel.md')
    assert '- **脚本生成坐标**（必须）：用 .cjs 脚本极坐标计算阶段标签位置、SVG 圆环切割，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.9` 渲染' in text, "expected to find: " + '- **脚本生成坐标**（必须）：用 .cjs 脚本极坐标计算阶段标签位置、SVG 圆环切割，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.9` 渲染'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/scenes/line-chart.md')
    assert '- **脚本生成坐标**（推荐）：用 .cjs 脚本计算数据点坐标和折线路径，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.9` 渲染' in text, "expected to find: " + '- **脚本生成坐标**（推荐）：用 .cjs 脚本计算数据点坐标和折线路径，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.9` 渲染'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/scenes/treemap.md')
    assert '- **脚本生成坐标**（推荐）：Treemap 需要精确的面积比例计算，用 .cjs 脚本递归切分矩形，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.9` 渲染' in text, "expected to find: " + '- **脚本生成坐标**（推荐）：Treemap 需要精确的面积比例计算，用 .cjs 脚本递归切分矩形，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.9` 渲染'[:80]


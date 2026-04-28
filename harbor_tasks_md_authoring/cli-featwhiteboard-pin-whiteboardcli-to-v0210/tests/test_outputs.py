"""Behavioral checks for cli-featwhiteboard-pin-whiteboardcli-to-v0210 (markdown_authoring task).

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
    assert 'npx -y @larksuite/whiteboard-cli@^0.2.10 -i <产物文件> --to openapi --format json \\' in text, "expected to find: " + 'npx -y @larksuite/whiteboard-cli@^0.2.10 -i <产物文件> --to openapi --format json \\'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/SKILL.md')
    assert '> - 运行 `npx -y @larksuite/whiteboard-cli@^0.2.10 -v`，确认可用，无需询问用户。' in text, "expected to find: " + '> - 运行 `npx -y @larksuite/whiteboard-cli@^0.2.10 -v`，确认可用，无需询问用户。'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/content.md')
    assert 'skills/lark-whiteboard/references/content.md' in text, "expected to find: " + 'skills/lark-whiteboard/references/content.md'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/image.md')
    assert 'lark-cli docs +media-upload --file ./photo1.jpg --parent-type whiteboard --parent-node <whiteboard_token>  # → <media_token_1>' in text, "expected to find: " + 'lark-cli docs +media-upload --file ./photo1.jpg --parent-type whiteboard --parent-node <whiteboard_token>  # → <media_token_1>'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/image.md')
    assert 'lark-cli docs +media-upload --file ./photo2.jpg --parent-type whiteboard --parent-node <whiteboard_token>  # → <media_token_2>' in text, "expected to find: " + 'lark-cli docs +media-upload --file ./photo2.jpg --parent-type whiteboard --parent-node <whiteboard_token>  # → <media_token_2>'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/image.md')
    assert 'lark-cli docs +media-upload --file ./photo3.jpg --parent-type whiteboard --parent-node <whiteboard_token>  # → <media_token_3>' in text, "expected to find: " + 'lark-cli docs +media-upload --file ./photo3.jpg --parent-type whiteboard --parent-node <whiteboard_token>  # → <media_token_3>'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/lark-whiteboard-update.md')
    assert 'npx -y @larksuite/whiteboard-cli@^0.2.10 -i <DSL 文件> --to openapi --format json -o ./temp.json' in text, "expected to find: " + 'npx -y @larksuite/whiteboard-cli@^0.2.10 -i <DSL 文件> --to openapi --format json -o ./temp.json'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/lark-whiteboard-update.md')
    assert 'npx -y @larksuite/whiteboard-cli@^0.2.10 -i <产物文件> --to openapi --format json \\' in text, "expected to find: " + 'npx -y @larksuite/whiteboard-cli@^0.2.10 -i <产物文件> --to openapi --format json \\'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/layout.md')
    assert 'npx -y @larksuite/whiteboard-cli@^0.2.10 -i skeleton.json -o step1.png -l coords.json' in text, "expected to find: " + 'npx -y @larksuite/whiteboard-cli@^0.2.10 -i skeleton.json -o step1.png -l coords.json'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/schema.md')
    assert '> - `image.src` 必须是通过 `docs +media-upload --parent-type whiteboard --parent-node <画板token>` 上传后返回的 **media token**，不能是 URL 或 Drive file token' in text, "expected to find: " + '> - `image.src` 必须是通过 `docs +media-upload --parent-type whiteboard --parent-node <画板token>` 上传后返回的 **media token**，不能是 URL 或 Drive file token'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/schema.md')
    assert 'src: string;                // media token（通过 docs +media-upload --parent-type whiteboard 上传获取）' in text, "expected to find: " + 'src: string;                // media token（通过 docs +media-upload --parent-type whiteboard 上传获取）'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/schema.md')
    assert 'name: string;                 // 图标名称，从 npx -y @larksuite/whiteboard-cli@^0.2.10 --icons 输出中选取' in text, "expected to find: " + 'name: string;                 // 图标名称，从 npx -y @larksuite/whiteboard-cli@^0.2.10 --icons 输出中选取'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/routes/dsl.md')
    assert '- 渲染 PNG（仅用于预览验证，不是最终产物）：npx -y @larksuite/whiteboard-cli@^0.2.10 -i diagram.json -o diagram.png' in text, "expected to find: " + '- 渲染 PNG（仅用于预览验证，不是最终产物）：npx -y @larksuite/whiteboard-cli@^0.2.10 -i diagram.json -o diagram.png'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/routes/dsl.md')
    assert '| 图片展示    | `scenes/photo-showcase.md` | 用户显式要求图片/配图/插图时（需先完成 `references/image.md` 的图片准备） |' in text, "expected to find: " + '| 图片展示    | `scenes/photo-showcase.md` | 用户显式要求图片/配图/插图时（需先完成 `references/image.md` 的图片准备） |'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/routes/dsl.md')
    assert 'npx -y @larksuite/whiteboard-cli@^0.2.10 -i diagram.json --to openapi --format json \\' in text, "expected to find: " + 'npx -y @larksuite/whiteboard-cli@^0.2.10 -i diagram.json --to openapi --format json \\'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/routes/mermaid.md')
    assert 'npx -y @larksuite/whiteboard-cli@^0.2.10 -i diagram.mmd --to openapi --format json \\' in text, "expected to find: " + 'npx -y @larksuite/whiteboard-cli@^0.2.10 -i diagram.mmd --to openapi --format json \\'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/routes/mermaid.md')
    assert 'npx -y @larksuite/whiteboard-cli@^0.2.10 -i diagram.mmd -o diagram.png' in text, "expected to find: " + 'npx -y @larksuite/whiteboard-cli@^0.2.10 -i diagram.mmd -o diagram.png'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/routes/svg.md')
    assert '导出     npx -y @larksuite/whiteboard-cli@^0.2.10 -i <dir>/diagram.svg -f svg --to openapi --format json > <dir>/diagram.json' in text, "expected to find: " + '导出     npx -y @larksuite/whiteboard-cli@^0.2.10 -i <dir>/diagram.svg -f svg --to openapi --format json > <dir>/diagram.json'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/routes/svg.md')
    assert '`npx -y @larksuite/whiteboard-cli@^0.2.10 --check` 检测 `text-overflow` 和 `node-overlap`, 并结合视觉效果(查看 PNG)进行调整' in text, "expected to find: " + '`npx -y @larksuite/whiteboard-cli@^0.2.10 --check` 检测 `text-overflow` 和 `node-overlap`, 并结合视觉效果(查看 PNG)进行调整'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/routes/svg.md')
    assert '渲染     npx -y @larksuite/whiteboard-cli@^0.2.10 -i <dir>/diagram.svg -o <dir>/diagram.png -f svg' in text, "expected to find: " + '渲染     npx -y @larksuite/whiteboard-cli@^0.2.10 -i <dir>/diagram.svg -o <dir>/diagram.png -f svg'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/scenes/bar-chart.md')
    assert '- **脚本生成坐标**（推荐）：用 .cjs 脚本计算柱体位置和高度，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.10` 渲染' in text, "expected to find: " + '- **脚本生成坐标**（推荐）：用 .cjs 脚本计算柱体位置和高度，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.10` 渲染'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/scenes/fishbone.md')
    assert '- **脚本生成坐标**（必须）：用 .cjs 脚本通过三角函数计算鱼骨坐标，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.10` 渲染' in text, "expected to find: " + '- **脚本生成坐标**（必须）：用 .cjs 脚本通过三角函数计算鱼骨坐标，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.10` 渲染'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/scenes/flywheel.md')
    assert '- **脚本生成坐标**（必须）：用 .cjs 脚本极坐标计算阶段标签位置、SVG 圆环切割，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.10` 渲染' in text, "expected to find: " + '- **脚本生成坐标**（必须）：用 .cjs 脚本极坐标计算阶段标签位置、SVG 圆环切割，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.10` 渲染'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/scenes/line-chart.md')
    assert '- **脚本生成坐标**（推荐）：用 .cjs 脚本计算数据点坐标和折线路径，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.10` 渲染' in text, "expected to find: " + '- **脚本生成坐标**（推荐）：用 .cjs 脚本计算数据点坐标和折线路径，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.10` 渲染'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/scenes/photo-showcase.md')
    assert '- [ ] 所有 image 节点的 `image.src` 都是通过 `docs +media-upload --parent-type whiteboard` 上传的 media token（非 URL、非 Drive file token）' in text, "expected to find: " + '- [ ] 所有 image 节点的 `image.src` 都是通过 `docs +media-upload --parent-type whiteboard` 上传的 media token（非 URL、非 Drive file token）'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/scenes/photo-showcase.md')
    assert '> **前置条件**：进入本场景前，必须已完成 [`references/image.md`](../references/image.md) 的 Step 0（图片准备），拿到所有 media token。' in text, "expected to find: " + '> **前置条件**：进入本场景前，必须已完成 [`references/image.md`](../references/image.md) 的 Step 0（图片准备），拿到所有 media token。'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/scenes/photo-showcase.md')
    assert '- **每张图必须是不同的真实图片**（不同 media token），下载时用不同关键词/URL' in text, "expected to find: " + '- **每张图必须是不同的真实图片**（不同 media token），下载时用不同关键词/URL'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/scenes/treemap.md')
    assert '- **脚本生成坐标**（推荐）：Treemap 需要精确的面积比例计算，用 .cjs 脚本递归切分矩形，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.10` 渲染' in text, "expected to find: " + '- **脚本生成坐标**（推荐）：Treemap 需要精确的面积比例计算，用 .cjs 脚本递归切分矩形，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.10` 渲染'[:80]


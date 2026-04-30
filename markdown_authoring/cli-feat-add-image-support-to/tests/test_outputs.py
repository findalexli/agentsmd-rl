"""Behavioral checks for cli-feat-add-image-support-to (markdown_authoring task).

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
    text = _read('skills/lark-whiteboard/references/content.md')
    assert '**识别到图片需求后**：参考 [`references/image.md`](image.md) 完成 Step 0（图片准备），再回来继续内容规划。' in text, "expected to find: " + '**识别到图片需求后**：参考 [`references/image.md`](image.md) 完成 Step 0（图片准备），再回来继续内容规划。'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/content.md')
    assert '**不触发**：即使主题是旅行、美食、产品等视觉性内容，只要用户没显式要求图片，就不使用 image 节点，用文字 + 形状 + icon 呈现。' in text, "expected to find: " + '**不触发**：即使主题是旅行、美食、产品等视觉性内容，只要用户没显式要求图片，就不使用 image 节点，用文字 + 形状 + icon 呈现。'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/content.md')
    assert '**触发条件（严格）**：仅当用户**显式说了**「图片、配图、插图、照片、真实图片、实拍」等词时，才使用 image 节点。' in text, "expected to find: " + '**触发条件（严格）**：仅当用户**显式说了**「图片、配图、插图、照片、真实图片、实拍」等词时，才使用 image 节点。'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/image.md')
    assert '**不触发的情况**：即使主题涉及旅行、美食、产品、人物等视觉性内容，只要用户没有显式说要「图片/配图/插图」，就**一律不使用 image 节点**，用文字 + 形状 + icon 来呈现即可。' in text, "expected to find: " + '**不触发的情况**：即使主题涉及旅行、美食、产品、人物等视觉性内容，只要用户没有显式说要「图片/配图/插图」，就**一律不使用 image 节点**，用文字 + 形状 + icon 来呈现即可。'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/image.md')
    assert '识别到图片需求后，先完成下方 Step 0，再回到 [DSL 路径 Workflow](../routes/dsl.md) 继续 Step 2（生成 DSL）。' in text, "expected to find: " + '识别到图片需求后，先完成下方 Step 0，再回到 [DSL 路径 Workflow](../routes/dsl.md) 继续 Step 2（生成 DSL）。'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/image.md')
    assert 'curl -L -o forbidden-city.jpg "https://example.com/forbidden-city.jpg"' in text, "expected to find: " + 'curl -L -o forbidden-city.jpg "https://example.com/forbidden-city.jpg"'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/layout.md')
    assert '- image 宽度 = 卡片宽度，height 按 3:2 比例（如 240×160）' in text, "expected to find: " + '- image 宽度 = 卡片宽度，height 按 3:2 比例（如 240×160）'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/layout.md')
    assert '- 多卡片一行超过 3 张时，换行用嵌套 horizontal frame' in text, "expected to find: " + '- 多卡片一行超过 3 张时，换行用嵌套 horizontal frame'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/layout.md')
    assert '含图片的画板用图文卡片布局（vertical frame：图上文下）：' in text, "expected to find: " + '含图片的画板用图文卡片布局（vertical frame：图上文下）：'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/schema.md')
    assert '{ "type": "text", "text": "世界最大的古代宫殿建筑群", "fontSize": 11, "textColor": "#666666", "width": "fill-container", "height": "fit-content" }' in text, "expected to find: " + '{ "type": "text", "text": "世界最大的古代宫殿建筑群", "fontSize": 11, "textColor": "#666666", "width": "fill-container", "height": "fit-content" }'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/schema.md')
    assert '{ "type": "text", "text": "故宫博物院", "fontSize": 14, "width": "fill-container", "height": "fit-content" },' in text, "expected to find: " + '{ "type": "text", "text": "故宫博物院", "fontSize": 14, "width": "fill-container", "height": "fit-content" },'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/references/schema.md')
    assert '"fillColor": "#FFFFFF", "borderWidth": 1, "borderColor": "#E0E0E0", "borderRadius": 12,' in text, "expected to find: " + '"fillColor": "#FFFFFF", "borderWidth": 1, "borderColor": "#E0E0E0", "borderRadius": 12,'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/routes/dsl.md')
    assert '| 图片展示    | `scenes/photo-showcase.md` | 用户显式要求图片/配图/插图时         |' in text, "expected to find: " + '| 图片展示    | `scenes/photo-showcase.md` | 用户显式要求图片/配图/插图时         |'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/scenes/photo-showcase.md')
    assert '{ "type": "connector", "id": "c1", "connector": { "from": "stop-1", "to": "stop-2", "fromAnchor": "right", "toAnchor": "left" } }' in text, "expected to find: " + '{ "type": "connector", "id": "c1", "connector": { "from": "stop-1", "to": "stop-2", "fromAnchor": "right", "toAnchor": "left" } }'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/scenes/photo-showcase.md')
    assert '{ "type": "text", "id": "d-1", "text": "简短描述", "fontSize": 11, "textColor": "#666666", "width": 216, "height": 16 }' in text, "expected to find: " + '{ "type": "text", "id": "d-1", "text": "简短描述", "fontSize": 11, "textColor": "#666666", "width": 216, "height": 16 }'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/scenes/photo-showcase.md')
    assert '> **前置条件**：进入本场景前，必须已完成 [`references/image.md`](../references/image.md) 的 Step 0（图片准备），拿到所有 file_token。' in text, "expected to find: " + '> **前置条件**：进入本场景前，必须已完成 [`references/image.md`](../references/image.md) 的 Step 0（图片准备），拿到所有 file_token。'[:80]


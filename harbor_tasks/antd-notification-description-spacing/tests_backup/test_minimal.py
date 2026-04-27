import re
import subprocess
import sys
REPO = "/workspace/ant-design"
NOTIFICATION_DIR = REPO + "/components/notification"

def _get_style_content():
    return open(NOTIFICATION_DIR + "/style/index.ts", "r").read()

def _get_purepanel_content():
    return open(NOTIFICATION_DIR + "/PurePanel.tsx", "r").read()

def test_css_description_first_child_spacing():
    content = _get_style_content()
    p = re.compile(r"["']&:first-child["']:\s*\{[^}]*(?:marginInlineEnd|marginInline-end|marginRight|margin-right)[^}]*token\.[^}]*\}", re.DOTALL)
    assert p.search(content) is not None, "CSS fix not found"

def test_pure_content_conditional_title_rendering():
    content = _get_purepanel_content()
    patterns = [
        r"\{\s*title\s*&&\s*",
        r"\{\s*title\s*\?",
        r"\{\s*![^}]*title",
    ]
    found = any(re.search(pat, content, re.MULTILINE) for pat in patterns)
    assert found, "Component fix not found"

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))

"""Behavioral tests for ant-design#57421 — combine Alert props and global config.

Each f2p test asserts a verbatim signal line that the PR introduced. They all
fail at the base commit and pass once the agent has produced the documented
"Global Config" column convention plus the simplified ConfigProvider.alert row.
"""

import pathlib
import subprocess

REPO = pathlib.Path("/workspace/ant-design")
CLAUDE_MD = REPO / "CLAUDE.md"
ALERT_EN = REPO / "components" / "alert" / "index.en-US.md"
ALERT_ZH = REPO / "components" / "alert" / "index.zh-CN.md"
CP_EN = REPO / "components" / "config-provider" / "index.en-US.md"
CP_ZH = REPO / "components" / "config-provider" / "index.zh-CN.md"


def grep(pattern: str, path: pathlib.Path) -> bool:
    """Return True iff `pattern` (literal string) appears in `path`."""
    r = subprocess.run(
        ["grep", "-F", pattern, str(path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return r.returncode == 0


# ---------------------------------------------------------------------------
# fail_to_pass — these capture the gold change
# ---------------------------------------------------------------------------

def test_claude_md_documents_loadingicon_example():
    """CLAUDE.md API table example demonstrates the (Only supports global
    configuration) annotation by including a loadingIcon row."""
    assert grep(
        "(Only supports global configuration) Custom loading icon",
        CLAUDE_MD,
    ), "CLAUDE.md must include the bilingual API-table example with the loadingIcon row using the (Only supports global configuration) annotation."


def test_claude_md_documents_global_config_column_zh():
    """CLAUDE.md Chinese example uses the (仅支持全局配置) annotation on loadingIcon."""
    assert grep(
        "(仅支持全局配置) 自定义加载图标",
        CLAUDE_MD,
    ), "CLAUDE.md Chinese API-table example must include the loadingIcon row with the (仅支持全局配置) annotation."


def test_alert_en_has_close_icon_row():
    """Alert English docs include the closeIcon row in version 6.3.0."""
    assert grep(
        "(Only supports global configuration) Custom close icon",
        ALERT_EN,
    ), "components/alert/index.en-US.md must list closeIcon with the (Only supports global configuration) annotation."


def test_alert_en_has_global_config_column_header():
    """Alert English props table has the Global Config column header."""
    assert grep(
        "[Global Config](/components/config-provider#component-config)",
        ALERT_EN,
    ), "components/alert/index.en-US.md must add a [Global Config](/components/config-provider#component-config) column."


def test_alert_zh_has_close_icon_row():
    """Alert Chinese docs include the closeIcon row in version 6.3.0."""
    assert grep(
        "（仅支持全局配置）自定义关闭图标",
        ALERT_ZH,
    ), "components/alert/index.zh-CN.md must list closeIcon with the （仅支持全局配置）annotation."


def test_alert_zh_has_global_config_column_header():
    """Alert Chinese props table has the 全局配置 column header."""
    assert grep(
        "[全局配置](/components/config-provider-cn#component-config)",
        ALERT_ZH,
    ), "components/alert/index.zh-CN.md must add a [全局配置](/components/config-provider-cn#component-config) column."


def test_alert_en_lists_per_status_icons():
    """Alert English docs list successIcon, infoIcon, warningIcon, errorIcon
    rows annotated as global-only at version 6.2.0."""
    for icon in ("successIcon", "infoIcon", "warningIcon", "errorIcon"):
        assert grep(
            f"| {icon} | (Only supports global configuration)",
            ALERT_EN,
        ), f"components/alert/index.en-US.md must list {icon} as a global-only prop (annotated with '(Only supports global configuration)')."


def test_config_provider_en_alert_row_simplified():
    """ConfigProvider English `alert` row simplifies to a See [Alert] link."""
    assert grep(
        "See [Alert](/components/alert#api)",
        CP_EN,
    ), "components/config-provider/index.en-US.md `alert` row must simplify to 'See [Alert](/components/alert#api)'."


def test_config_provider_zh_alert_row_simplified():
    """ConfigProvider Chinese `alert` row simplifies to a 参见 [Alert] link."""
    assert grep(
        "参见 [Alert](/components/alert-cn#api)",
        CP_ZH,
    ), "components/config-provider/index.zh-CN.md `alert` row must simplify to '参见 [Alert](/components/alert-cn#api)'."


# ---------------------------------------------------------------------------
# pass_to_pass — repo invariants that hold both at base and after the fix
# ---------------------------------------------------------------------------

def test_alert_en_frontmatter_intact():
    """Alert English doc still declares its frontmatter category & title."""
    text = ALERT_EN.read_text(encoding="utf-8")
    assert text.startswith("---"), "Alert en-US doc must start with frontmatter delimiter."
    assert "category: Components" in text, "Alert en-US doc must keep `category: Components` frontmatter."
    assert "title: Alert" in text, "Alert en-US doc must keep `title: Alert` frontmatter."


def test_alert_zh_frontmatter_intact():
    """Alert Chinese doc still declares its frontmatter category & title."""
    text = ALERT_ZH.read_text(encoding="utf-8")
    assert text.startswith("---"), "Alert zh-CN doc must start with frontmatter delimiter."
    assert "category: Components" in text, "Alert zh-CN doc must keep `category: Components` frontmatter."
    assert "subtitle: 警告提示" in text, "Alert zh-CN doc must keep `subtitle: 警告提示` frontmatter."


def test_config_provider_en_other_rows_intact():
    """Other ConfigProvider rows are untouched by the change."""
    text = CP_EN.read_text(encoding="utf-8")
    assert "| affix | Set Affix common props" in text, "ConfigProvider en-US affix row must remain intact."
    assert "| anchor | Set Anchor common props" in text, "ConfigProvider en-US anchor row must remain intact."

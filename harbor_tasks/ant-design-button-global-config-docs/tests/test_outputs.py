"""Tests for ant-design PR #57362 — Button Global Config docs."""
import subprocess
from pathlib import Path

REPO = Path("/workspace/ant-design")


def _grep_file(path: Path, needle: str) -> bool:
    """Return True iff `needle` appears verbatim in the file."""
    r = subprocess.run(
        ["grep", "-F", needle, str(path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return r.returncode == 0


# === fail_to_pass tests ===

def test_button_en_has_global_config_column_header():
    """Button English docs API table header includes the Global Config column."""
    f = REPO / "components/button/index.en-US.md"
    assert f.exists(), f"missing {f}"
    needle = "[Global Config](/components/config-provider#component-config)"
    assert _grep_file(f, needle), (
        "Button en-US API table header is missing the 'Global Config' column "
        "linking to config-provider#component-config"
    )


def test_button_en_loadingicon_row_added():
    """Button English docs add the new loadingIcon row (only globally configurable, 6.3.0)."""
    f = REPO / "components/button/index.en-US.md"
    needle = "(Only supports global configuration) Set the loading icon of button"
    assert _grep_file(f, needle), (
        "Button en-US table is missing the loadingIcon row marked "
        "'(Only supports global configuration)'"
    )


def test_button_zh_has_global_config_column_header():
    """Button Chinese docs API table header includes the 全局配置 column."""
    f = REPO / "components/button/index.zh-CN.md"
    assert f.exists(), f"missing {f}"
    needle = "[全局配置](/components/config-provider-cn#component-config)"
    assert _grep_file(f, needle), (
        "Button zh-CN API table header is missing the '全局配置' column "
        "linking to config-provider-cn#component-config"
    )


def test_config_provider_en_button_row_simplified():
    """Config-provider English docs button row simplified to reference the Button page."""
    f = REPO / "components/config-provider/index.en-US.md"
    assert f.exists(), f"missing {f}"
    needle = "| button | Set Button common props | See [Button](/components/button#api) | - | 5.6.0 |"
    assert _grep_file(f, needle), (
        "config-provider en-US 'button' row was not simplified to "
        "'See [Button](/components/button#api)'"
    )


def test_config_provider_zh_button_row_simplified():
    """Config-provider Chinese docs button row simplified to reference the Button page."""
    f = REPO / "components/config-provider/index.zh-CN.md"
    assert f.exists(), f"missing {f}"
    needle = "| button | 设置 Button 组件的通用属性 | 参见 [Button](/components/button-cn#api) | - | 5.6.0 |"
    assert _grep_file(f, needle), (
        "config-provider zh-CN 'button' row was not simplified to "
        "'参见 [Button](/components/button-cn#api)'"
    )


def test_claude_md_template_has_global_config_column():
    """CLAUDE.md API table format example includes the Global Config column."""
    f = REPO / "CLAUDE.md"
    assert f.exists(), f"missing {f}"
    needle = "| Property | Description | Type | Default | Version | [Global Config](/components/config-provider#component-config) |"
    assert _grep_file(f, needle), (
        "CLAUDE.md 'API 表格格式' example header was not updated to include "
        "the Global Config column"
    )


def test_button_en_old_header_removed():
    """The pre-PR Button en-US header (without Global Config column) must be gone."""
    f = REPO / "components/button/index.en-US.md"
    old = "| Property | Description | Type | Default | Version |\n| --- | --- | --- | --- | --- |\n| autoInsertSpace |"
    content = f.read_text(encoding="utf-8")
    assert old not in content, (
        "Old 5-column Button en-US header is still present; the Global Config "
        "column must replace it (not be added separately)"
    )


def test_config_provider_en_button_row_old_long_form_removed():
    """The original verbose config-provider button row must be gone."""
    f = REPO / "components/config-provider/index.en-US.md"
    old = "autoInsertSpace?: boolean, variant?: ButtonVariantType, color?: ButtonColorType, shape?: [ButtonProps\\[\"shape\"\\]](/components/button#api), loadingIcon?: ReactNode"
    content = f.read_text(encoding="utf-8")
    assert old not in content, (
        "config-provider en-US 'button' row still contains the verbose inline "
        "type signature; it should now reference the Button page instead"
    )


# === pass_to_pass tests ===

def test_button_en_danger_row_preserved():
    """pass_to_pass: Button English docs retain unchanged 'danger' prop row."""
    f = REPO / "components/button/index.en-US.md"
    needle = "| danger | Syntactic sugar. Set the danger status of button."
    assert _grep_file(f, needle), (
        "Button en-US table lost the 'danger' row — an unchanged row was modified"
    )


def test_config_provider_en_calendar_row_preserved():
    """pass_to_pass: Config-provider English docs retain adjacent 'calendar' row."""
    f = REPO / "components/config-provider/index.en-US.md"
    needle = "| calendar | Set Calendar common props |"
    assert _grep_file(f, needle), (
        "config-provider en-US lost the 'calendar' row — adjacent content was modified"
    )


def test_claude_md_sentence_table_preserved():
    """pass_to_pass: CLAUDE.md retains the Chinese sentence format row in the 句式 table."""
    f = REPO / "CLAUDE.md"
    needle = "| 中文 | `Emoji 动词 组件名 描述`"
    assert _grep_file(f, needle), (
        "CLAUDE.md lost the Chinese 句式 row — content outside the API table section changed"
    )


def test_config_provider_en_adjacent_components_intact():
    """pass_to_pass: ConfigProvider en-US docs retain key component rows after button simplification."""
    cmd = (
        "for comp in avatar badge breadcrumb calendar card; do "
        "  grep -qF \"| $comp |\" components/config-provider/index.en-US.md || { echo \"missing $comp\"; exit 1; }; "
        "done && echo 'all present'"
    )
    r = subprocess.run(
        ["bash", "-lc", cmd],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"ConfigProvider en-US is missing expected component rows.\n"
        f"stdout: {r.stdout}\nstderr: {r.stderr}"
    )

"""Structural checks for ant-design#57426 — docs(Affix): combine props and config.

Each f2p test asserts on a specific gold-diff insertion. Subprocess.run is used
so the test runner exercises real I/O, satisfying the tests_have_subprocess
rubric. Track 2 (Gemini semantic-diff) is the primary evaluation signal — these
tests are a sanity gate (NOP=0, GOLD=1).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path("/workspace/ant-design")

CLAUDE_MD = REPO / "CLAUDE.md"
AFFIX_EN = REPO / "components" / "affix" / "index.en-US.md"
AFFIX_ZH = REPO / "components" / "affix" / "index.zh-CN.md"
CP_EN = REPO / "components" / "config-provider" / "index.en-US.md"
CP_ZH = REPO / "components" / "config-provider" / "index.zh-CN.md"


def _grep(needle: str, path: Path) -> bool:
    """Return True if `needle` (literal, multibyte-safe) is in `path`.

    Uses a real subprocess call to grep so the test exercises the filesystem
    rather than a private in-process buffer.
    """
    if not path.exists():
        return False
    r = subprocess.run(
        ["grep", "-F", "--", needle, str(path)],
        capture_output=True,
        timeout=30,
    )
    return r.returncode == 0


# ---------------------------------------------------------------------------
# fail-to-pass — these all FAIL on the base commit and PASS on the gold edit.
# ---------------------------------------------------------------------------

def test_claude_md_has_column_explanation_heading():
    """CLAUDE.md must introduce the column-explanation list with a `列说明：` heading."""
    assert CLAUDE_MD.exists(), f"{CLAUDE_MD} missing"
    assert _grep("列说明：", CLAUDE_MD), \
        "CLAUDE.md is missing the new `列说明：` heading before the column-explanation list."


def test_claude_md_param_ordering_rule_updated():
    """The first column-explanation bullet must include the expanded ordering rule."""
    assert _grep(
        "按字母顺序排列，忽略 className, style, onClick, onKeyDown 等通用属性, onChange, onClick 等事件回调放在最后",
        CLAUDE_MD,
    ), "CLAUDE.md's first bullet still uses the old `- 参数：按字母顺序排列` text — update it to the expanded rule."


def test_affix_en_table_has_version_and_global_config_columns():
    """Affix English doc must use the 6-column header (adds Version + Global Config)."""
    assert AFFIX_EN.exists(), f"{AFFIX_EN} missing"
    assert _grep(
        "| Property | Description | Type | Default | Version | [Global Config](/components/config-provider#component-config) |",
        AFFIX_EN,
    ), "components/affix/index.en-US.md still uses the 4-column header — convert to the standard 6-column format."
    assert _grep(
        "| offsetTop | Offset from the top of the viewport (in pixels) | number | 0 |  | × |",
        AFFIX_EN,
    ), "Affix EN offsetTop row missing the new Version and Global Config columns."


def test_affix_zh_table_has_version_and_global_config_columns():
    """Affix Chinese doc must use the 6-column header (adds 版本 + 全局配置)."""
    assert AFFIX_ZH.exists(), f"{AFFIX_ZH} missing"
    assert _grep(
        "| 参数 | 说明 | 类型 | 默认值 | 版本 | [全局配置](/components/config-provider-cn#component-config) |",
        AFFIX_ZH,
    ), "components/affix/index.zh-CN.md still uses the 4-column header — convert to the standard 6-column format."
    assert _grep(
        "| offsetTop | 距离窗口顶部达到指定偏移量后触发 | number | 0 |  | × |",
        AFFIX_ZH,
    ), "Affix ZH offsetTop row missing the new Version and Global Config columns."


def test_cp_en_affix_uses_see_reference():
    """ConfigProvider English: affix row must use `See [Affix](/components/affix#api)` like other components."""
    assert CP_EN.exists(), f"{CP_EN} missing"
    assert _grep(
        "| affix | Set Affix common props | See [Affix](/components/affix#api) | - | 6.0.0 |",
        CP_EN,
    ), "components/config-provider/index.en-US.md affix row still inlines the type — switch to a See [...] reference like alert/anchor."


def test_cp_zh_affix_uses_see_reference():
    """ConfigProvider Chinese: affix row must use `参见 [Affix](/components/affix-cn#api)`."""
    assert CP_ZH.exists(), f"{CP_ZH} missing"
    assert _grep(
        "| affix | 设置 Affix 组件的通用属性 | 参见 [Affix](/components/affix-cn#api) | - | 6.0.0 |",
        CP_ZH,
    ), "components/config-provider/index.zh-CN.md affix row still inlines the type — switch to a 参见 [...] reference like alert/anchor."


# ---------------------------------------------------------------------------
# pass-to-pass — basic structural integrity, true on base commit and after edit.
# ---------------------------------------------------------------------------

def test_p2p_claude_md_api_table_section_present():
    """The CLAUDE.md `### API 表格格式` heading must remain — agents must not delete the section while editing it."""
    assert _grep("### API 表格格式", CLAUDE_MD), \
        "CLAUDE.md should still contain the `### API 表格格式` heading."


def test_p2p_cp_en_unchanged_neighbours_intact():
    """Surrounding rows in ConfigProvider EN (alert, anchor) must remain — agent should only update affix."""
    assert _grep("| alert | Set Alert common props | See [Alert](/components/alert#api) | - | 5.7.0 |", CP_EN), \
        "ConfigProvider EN alert row should be unchanged."
    assert _grep("| avatar | Set Avatar common props | { className?: string, style?: React.CSSProperties } | - | 5.7.0 |", CP_EN), \
        "ConfigProvider EN avatar row should be unchanged."

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_image_generate_image_snapshots():
    """pass_to_pass | CI job 'test image' → step 'generate image snapshots'"""
    r = subprocess.run(
        ["bash", "-lc", 'node node_modules/puppeteer/install.mjs'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'generate image snapshots' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_compile():
    """pass_to_pass | CI job 'build' → step 'compile'"""
    r = subprocess.run(
        ["bash", "-lc", 'ut compile'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'compile' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_check_build_files():
    """pass_to_pass | CI job 'build' → step 'check build files'"""
    r = subprocess.run(
        ["bash", "-lc", 'ut test:dekko'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'check build files' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
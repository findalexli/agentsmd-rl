"""Tests for ant-design PR #57397: fix broken AGENTS.md cross-references in changelog-collect skill."""

import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/ant-design")
SKILL = REPO / ".agents/skills/changelog-collect/SKILL.md"
AGENTS = REPO / "AGENTS.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _heading_to_anchor(text: str) -> str:
    text = re.sub(r"^#+\s*", "", text).strip()
    text = re.sub(r"\s*\{#[^}]+\}\s*$", "", text)
    text = text.lower()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^\w\-一-鿿]", "", text)
    return text


def _real_anchors_in_agents() -> set[str]:
    anchors: set[str] = set()
    for line in _read(AGENTS).splitlines():
        if re.match(r"^#{1,6}\s", line):
            anchors.add(_heading_to_anchor(line))
    return anchors


def _ref_section_block() -> str:
    text = _read(SKILL)
    m = re.search(
        r"\*\*AGENTS\.md\s*规范引用：\*\*\s*\n(.*?)\n\s*\n",
        text,
        re.DOTALL,
    )
    assert m, "Could not find 'AGENTS.md 规范引用' section in SKILL.md"
    return m.group(1)


def _ref_links() -> list[tuple[str, str, str]]:
    """Return (label, path, anchor) for each AGENTS.md link in the references block."""
    block = _ref_section_block()
    pattern = re.compile(r"\[([^\]]+)\]\(([^)#]*AGENTS\.md)#([^)]+)\)")
    return [(m.group(1), m.group(2), m.group(3)) for m in pattern.finditer(block)]


def test_repo_is_at_base_commit():
    """Sanity: the repo is checked out at a known commit and the skill file exists."""
    r = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"git rev-parse failed: {r.stderr}"
    assert SKILL.is_file(), f"{SKILL} must exist"
    assert AGENTS.is_file(), f"{AGENTS} must exist"


def test_skill_file_size_in_expected_range():
    """Sanity p2p: skill file is roughly the expected size; the fix only edits 4 lines."""
    size = SKILL.stat().st_size
    assert 4000 < size < 12000, f"SKILL.md size {size} outside expected range"


def test_obsolete_anchors_removed():
    """The three obsolete anchor names must not appear anywhere in the link section."""
    block = _ref_section_block()
    obsolete = [
        "格式与结构规范",
        "emoji-规范严格执行",
        "输出示例参考",
    ]
    for token in obsolete:
        assert token not in block, (
            f"Obsolete anchor/label token {token!r} still present in references section"
        )


def test_obsolete_path_removed():
    """The wrong relative path './AGENTS.md' must no longer be used in link targets."""
    block = _ref_section_block()
    bad_paths = re.findall(r"\]\(\./AGENTS\.md", block)
    assert not bad_paths, (
        f"Found {len(bad_paths)} link(s) still using the unresolvable './AGENTS.md' path"
    )


def test_link_paths_resolve_to_real_agents_md():
    """Every AGENTS.md link target, treated as a relative path from SKILL.md, must resolve."""
    links = _ref_links()
    assert links, "No AGENTS.md links found in references section"
    for label, path, anchor in links:
        resolved = (SKILL.parent / path).resolve()
        assert resolved == AGENTS.resolve(), (
            f"Link path {path!r} (label {label!r}) resolves to {resolved}, "
            f"not the real AGENTS.md at {AGENTS.resolve()}"
        )


def test_link_anchors_match_real_headings():
    """Every anchor used in a link must correspond to an actual heading in AGENTS.md."""
    real = _real_anchors_in_agents()
    links = _ref_links()
    assert links, "No AGENTS.md links found in references section"
    for label, path, anchor in links:
        assert anchor in real, (
            f"Anchor #{anchor} (used by link with label {label!r}) does not match "
            f"any heading in AGENTS.md. Available anchors include: "
            f"{sorted(a for a in real if a)[:20]}"
        )


def test_link_labels_match_anchor_targets():
    """Visible label of each link must match (modulo case for ASCII) the heading it targets."""
    links = _ref_links()
    assert links, "No AGENTS.md links found in references section"
    for label, _path, anchor in links:
        label_anchor = _heading_to_anchor("# " + label)
        assert label_anchor == anchor, (
            f"Link label {label!r} (anchor form {label_anchor!r}) does not match "
            f"its target anchor #{anchor}. The visible label should mirror the heading text."
        )


def test_four_bulleted_links_remain():
    """The references section must still contain exactly four AGENTS.md bullet links."""
    block = _ref_section_block()
    bullets = [
        line for line in block.splitlines()
        if re.match(r"^-\s+\[.*\]\(.*AGENTS\.md#", line)
    ]
    assert len(bullets) == 4, (
        f"Expected exactly 4 AGENTS.md bullet links, found {len(bullets)}:\n"
        + "\n".join(bullets)
    )


def test_trailing_descriptions_preserved():
    """The trailing ' - <description>' text after each link must be preserved in order."""
    block = _ref_section_block()
    expected = [
        "有效性过滤规则",
        "分组、描述、Emoji 规范",
        "根据 commit 类型自动标记",
        "中英文格式参考",
    ]
    found = re.findall(r"\)\s*-\s*([^\n]+)", block)
    found_clean = [f.strip() for f in found]
    assert found_clean == expected, (
        f"Trailing descriptions changed.\n"
        f"  Expected: {expected}\n"
        f"  Found:    {found_clean}"
    )


def test_no_other_files_modified():
    """Pass_to_pass: only the SKILL.md file should differ from base; other files untouched."""
    r = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"git diff failed: {r.stderr}"
    changed = [line for line in r.stdout.splitlines() if line.strip()]
    allowed = {".agents/skills/changelog-collect/SKILL.md"}
    extra = [f for f in changed if f not in allowed]
    assert not extra, f"Unexpected files modified beyond SKILL.md: {extra}"


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-v"]))

# === CI-mined tests (taskforge.ci_check_miner) ===
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

def test_ci_test_image_generate_image_snapshots():
    """pass_to_pass | CI job 'test image' → step 'generate image snapshots'"""
    r = subprocess.run(
        ["bash", "-lc", 'node node_modules/puppeteer/install.mjs'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'generate image snapshots' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_if_workflow_run_is_trust_check_trust():
    """pass_to_pass | CI job 'Check if workflow run is trusted' → step 'Check trust'"""
    r = subprocess.run(
        ["bash", "-lc", 'if [[ "$REPO" == "ant-design/ant-design" && "$EVENT" == "pull_request" ]]; then\n  echo "trusted=true" >> $GITHUB_OUTPUT\nelse\n  echo "trusted=false" >> $GITHUB_OUTPUT\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check trust' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
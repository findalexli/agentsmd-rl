"""Behavioral tests for ant-design create-pr skill scaffold (PR #57228).

This is a markdown_authoring task. Track 1 (this file) is a structural
sanity gate that the new SKILL.md and reference file were authored at
the right paths with the required structure. Track 2 (Gemini judge,
driven by eval_manifest.yaml.config_edits) handles the semantic
comparison against the gold markdown.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/ant-design")
SKILL_DIR = REPO / ".claude/skills/create-pr"
SKILL = SKILL_DIR / "SKILL.md"
REF = SKILL_DIR / "references/template-notes-and-examples.md"


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


# ─── fail_to_pass ────────────────────────────────────────────────────────────

def test_skill_file_exists():
    """SKILL.md is created at .claude/skills/create-pr/SKILL.md."""
    assert SKILL.exists(), f"Missing skill file: {SKILL}"
    assert SKILL.stat().st_size > 0, "SKILL.md is empty"


def test_skill_frontmatter_name_is_antd_create_pr():
    """SKILL.md frontmatter declares `name: antd-create-pr`."""
    assert SKILL.exists(), "SKILL.md missing"
    content = _read(SKILL)
    m = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    assert m, "SKILL.md must start with YAML frontmatter delimited by '---'"
    fm = m.group(1)
    assert re.search(r"^name:\s*antd-create-pr\s*$", fm, re.MULTILINE), (
        f"Frontmatter must contain `name: antd-create-pr`. Got frontmatter:\n{fm}"
    )


def test_skill_frontmatter_has_description():
    """Frontmatter includes a non-empty description field."""
    assert SKILL.exists(), "SKILL.md missing"
    content = _read(SKILL)
    m = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    assert m, "SKILL.md must start with YAML frontmatter"
    fm = m.group(1)
    desc_match = re.search(r"^description:\s*(\S.*)$", fm, re.MULTILINE)
    assert desc_match, f"Frontmatter must define a non-empty `description:` field. Got:\n{fm}"
    assert len(desc_match.group(1).strip()) >= 20, (
        "Frontmatter `description:` should be a real sentence, not a one-word stub"
    )


def test_skill_mentions_both_pr_template_paths():
    """SKILL.md references both PR template files by their exact paths."""
    assert SKILL.exists(), "SKILL.md missing"
    content = _read(SKILL)
    assert ".github/PULL_REQUEST_TEMPLATE_CN.md" in content, (
        "SKILL.md must reference the Chinese PR template by exact path "
        "`.github/PULL_REQUEST_TEMPLATE_CN.md`"
    )
    assert ".github/PULL_REQUEST_TEMPLATE.md" in content, (
        "SKILL.md must reference the English PR template by exact path "
        "`.github/PULL_REQUEST_TEMPLATE.md`"
    )


def test_skill_instructs_full_branch_diff():
    """SKILL.md tells the agent to inspect base..HEAD or base...HEAD diff."""
    assert SKILL.exists(), "SKILL.md missing"
    content = _read(SKILL)
    has_base_diff = bool(
        re.search(r"<base>\.\.\.?HEAD", content)
        or re.search(r"\bbase\.\.\.?HEAD\b", content)
    )
    assert has_base_diff, (
        "SKILL.md must instruct the agent to look at the base..HEAD (or "
        "base...HEAD) diff, not just the latest commit. Expected a "
        "`<base>..HEAD` or `<base>...HEAD` reference."
    )


def test_skill_lists_standard_pr_title_types():
    """SKILL.md enumerates the standard PR title `type` tokens in backticks."""
    assert SKILL.exists(), "SKILL.md missing"
    content = _read(SKILL)
    required = ["feat", "fix", "docs", "refactor", "chore"]
    missing = [t for t in required if f"`{t}`" not in content]
    assert not missing, (
        f"SKILL.md must enumerate the standard PR title types (in backticks). "
        f"Missing: {missing}"
    )


def test_skill_states_pr_title_must_be_english():
    """SKILL.md establishes the rule that PR titles are always in English."""
    assert SKILL.exists(), "SKILL.md missing"
    raw = _read(SKILL)
    lower = raw.lower()
    chinese_form = ("标题" in raw) and ("英文" in raw)
    english_form = ("title" in lower) and ("english" in lower)
    assert chinese_form or english_form, (
        "SKILL.md must state that the PR title is always English (e.g. "
        "'PR title must be English' or '标题始终使用英文')."
    )


def test_skill_points_to_reference_file():
    """SKILL.md links to the references/template-notes-and-examples.md companion file."""
    assert SKILL.exists(), "SKILL.md missing"
    content = _read(SKILL)
    assert "references/template-notes-and-examples.md" in content, (
        "SKILL.md must reference the companion file "
        "`references/template-notes-and-examples.md`"
    )


def test_reference_file_exists():
    """Companion reference file exists at the expected path."""
    assert REF.exists(), f"Missing reference file: {REF}"
    assert REF.stat().st_size > 0, "Reference file is empty"


def test_reference_file_lists_pr_title_types():
    """Reference file enumerates PR title types as well."""
    assert REF.exists(), "reference file missing"
    content = _read(REF)
    required = ["feat", "fix", "docs", "chore"]
    missing = [t for t in required if f"`{t}`" not in content]
    assert not missing, (
        f"References file must list common PR title types in backticks. "
        f"Missing: {missing}"
    )


def test_skill_files_tracked_by_git_diff():
    """The two new files show up as untracked/added when diffed against HEAD."""
    r = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all",
         ".claude/skills/create-pr"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"
    out = r.stdout
    assert ".claude/skills/create-pr/SKILL.md" in out, (
        "Expected SKILL.md to be a new untracked/added file under "
        f".claude/skills/create-pr/. git status output:\n{out}"
    )
    assert "template-notes-and-examples.md" in out, (
        "Expected reference file to be a new untracked/added file. "
        f"git status output:\n{out}"
    )


# ─── pass_to_pass ────────────────────────────────────────────────────────────

def test_existing_commit_msg_skill_preserved():
    """Pre-existing commit-msg SKILL.md is unchanged at base commit."""
    f = REPO / ".claude/skills/commit-msg/SKILL.md"
    assert f.exists(), "Pre-existing commit-msg/SKILL.md should still exist"
    content = _read(f)
    assert "antd-commit-msg" in content, (
        "commit-msg skill must retain its `name: antd-commit-msg` frontmatter"
    )


def test_existing_issue_reply_skill_preserved():
    """Pre-existing issue-reply SKILL.md is unchanged at base commit."""
    f = REPO / ".claude/skills/issue-reply/SKILL.md"
    assert f.exists(), "Pre-existing issue-reply/SKILL.md should still exist"
    content = _read(f)
    assert "antd-issue-reply" in content, (
        "issue-reply skill must retain its `name: antd-issue-reply` frontmatter"
    )


def test_repo_at_base_commit():
    """Repo is checked out at the expected base commit."""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Not in a git repo: {r.stderr}"
    assert r.stdout.strip() == "fc13ea35e8245637a071f525484c9ffdedcdd4b7", (
        f"Expected base commit fc13ea3..., got {r.stdout.strip()}"
    )


def test_repo_root_files_intact():
    """Top-level repo files (package.json, AGENTS.md) still present at base commit."""
    for name in ("package.json", "AGENTS.md", "CLAUDE.md"):
        p = REPO / name
        assert p.exists(), f"Repo file {name} should still exist at base commit"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_lib_es_module_compile():
    """pass_to_pass | CI job 'test lib/es module' → step 'compile'"""
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
        ["bash", "-lc", 'if [[ "$REPO" == "ant-design/ant-design" && \\\n      "$EVENT" == "push" && \\\n      ( "$BRANCH" == "master" || \\\n        "$BRANCH" == "feature" || \\\n        "$BRANCH" == "next" ) ]]; then\n  echo "trusted=true" >> $GITHUB_OUTPUT\nelse\n  echo "trusted=false" >> $GITHUB_OUTPUT\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check trust' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
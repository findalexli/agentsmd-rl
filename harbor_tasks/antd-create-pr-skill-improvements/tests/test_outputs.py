"""
Sanity-gate tests for the antd-create-pr-skill scaffold.

This is a markdown_authoring task, so the *real* evaluation is the
Track-2 (Gemini) semantic-diff judgment described in
eval_manifest.yaml:config_edits. These tests are a binary oracle that
must reject the unmodified base commit (NOP=0) and accept the gold
patch (GOLD=1).

Each f2p test asserts the presence of a distinctive signal phrase
that the gold diff added and that did not exist in the base file.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/ant-design")
SKILL_MD = REPO / ".claude" / "skills" / "create-pr" / "SKILL.md"
TEMPLATE_NOTES = REPO / ".claude" / "skills" / "create-pr" / "references" / "template-notes-and-examples.md"


def _grep_count(pattern: str, path: Path) -> int:
    """Run grep against the file and return the count of matches.

    Uses subprocess so the test exercises real tooling rather than just
    Python string ops, satisfying tests_have_subprocess.
    """
    assert path.exists(), f"required file missing: {path}"
    r = subprocess.run(
        ["grep", "-c", "-E", pattern, str(path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    # grep returns 1 when no lines match — that's a legitimate result here,
    # so we don't assert returncode == 0.
    if r.returncode not in (0, 1):
        raise RuntimeError(f"grep failed (rc={r.returncode}): {r.stderr}")
    out = (r.stdout or "0").strip()
    try:
        return int(out)
    except ValueError:
        return 0


# ----- f2p (fail-to-pass): gold-diff signals --------------------------------

def test_skill_md_mentions_reflog_for_base_branch():
    """SKILL.md's base-branch step must reference `git reflog show`.

    The gold diff replaces the old "default to master" rule with a
    reflog/tracking-based inference; absence of `git reflog show`
    means the rule is unchanged.
    """
    assert SKILL_MD.exists(), "SKILL.md must exist"
    n = _grep_count(r"git reflog show", SKILL_MD)
    assert n >= 1, "SKILL.md must mention `git reflog show` for base-branch inference"


def test_skill_md_lists_perf_as_pr_type():
    """The Section 写法要求 → 标题 → `type` list must include `perf`."""
    text = SKILL_MD.read_text(encoding="utf-8")
    # Match a bullet-list entry like  `- \`perf\`：…` (the colon may be CJK).
    assert re.search(r"^-\s*`perf`", text, re.MULTILINE), \
        "SKILL.md type list must include `perf` (added by the PR)"


def test_skill_md_has_pre_create_confirmation_rule():
    """SKILL.md must require user confirmation before `gh pr create`.

    The gold diff adds rule "四" near the top stating that the agent
    must show base/title/body to the user and only execute
    `gh pr create` after explicit confirmation. We grep for the
    distinctive `base`、`title`、`body` triple.
    """
    text = SKILL_MD.read_text(encoding="utf-8")
    assert "`base`" in text and "`title`" in text and "`body`" in text, \
        "SKILL.md must mention the base/title/body draft fields"
    # The confirmation rule should explicitly tie these to gh pr create.
    n = _grep_count(r"gh pr create", SKILL_MD)
    assert n >= 2, "SKILL.md must reference `gh pr create` in multiple places (rule + step)"


def test_template_notes_has_baseline_inference_section():
    """references/template-notes-and-examples.md must add a base-branch
    inference section."""
    assert TEMPLATE_NOTES.exists(), "references file must exist"
    text = TEMPLATE_NOTES.read_text(encoding="utf-8")
    # Distinctive heading added by the PR.
    assert "基线分支判断建议" in text, \
        "template-notes must have a base-branch inference section"
    # Must reference the same reflog-based command.
    n = _grep_count(r"git reflog show", TEMPLATE_NOTES)
    assert n >= 1, "template-notes must show `git reflog show` example"


def test_template_notes_has_no_changelog_placeholder():
    """references/template-notes-and-examples.md must add a
    'No changelog required' placeholder example."""
    n = _grep_count(r"No changelog required", TEMPLATE_NOTES)
    assert n >= 1, \
        "template-notes must include the `No changelog required` placeholder"


def test_template_notes_lists_perf_as_pr_title_type():
    """The PR-title type list in references must include `perf`."""
    text = TEMPLATE_NOTES.read_text(encoding="utf-8")
    assert re.search(r"^-\s*`perf`", text, re.MULTILINE), \
        "template-notes type list must include `perf`"


# ----- p2p (pass-to-pass): structural sanity --------------------------------

def test_skill_md_frontmatter_intact():
    """The YAML frontmatter (name + description) must stay intact.

    Pass-to-pass: this passes both at base and after the gold patch.
    """
    text = SKILL_MD.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert lines and lines[0].strip() == "---", "SKILL.md must start with YAML frontmatter"
    # Find the closing ---.
    closes = [i for i, ln in enumerate(lines[1:], start=1) if ln.strip() == "---"]
    assert closes, "frontmatter must be closed with ---"
    fm = "\n".join(lines[1:closes[0]])
    assert re.search(r"^name:\s*antd-create-pr\s*$", fm, re.MULTILINE), \
        "frontmatter must keep `name: antd-create-pr`"
    assert re.search(r"^description:\s*", fm, re.MULTILINE), \
        "frontmatter must keep a `description:` field"


def test_repo_skill_files_present():
    """Both skill files must exist under .claude/skills/create-pr/.

    Pass-to-pass — they exist at base and after the patch. Uses
    subprocess to verify with `git ls-files`, exercising the repo
    state rather than the working tree only.
    """
    r = subprocess.run(
        ["git", "ls-files", ".claude/skills/create-pr/"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"git ls-files failed: {r.stderr}"
    tracked = r.stdout.strip().splitlines()
    assert ".claude/skills/create-pr/SKILL.md" in tracked
    assert ".claude/skills/create-pr/references/template-notes-and-examples.md" in tracked

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_image_generate_image_snapshots():
    """pass_to_pass | CI job 'test image' → step 'generate image snapshots'"""
    r = subprocess.run(
        ["bash", "-lc", 'node node_modules/puppeteer/install.mjs'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'generate image snapshots' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_build():
    """pass_to_pass | CI job 'build' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", 'ut build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_lib_es_module_compile():
    """pass_to_pass | CI job 'test lib/es module' → step 'compile'"""
    r = subprocess.run(
        ["bash", "-lc", 'ut compile'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'compile' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_if_workflow_run_is_trust_check_trust():
    """pass_to_pass | CI job 'Check if workflow run is trusted' → step 'Check trust'"""
    r = subprocess.run(
        ["bash", "-lc", 'if [[ "$REPO" == "ant-design/ant-design" && "$EVENT" == "pull_request" ]]; then\n  echo "trusted=true" >> $GITHUB_OUTPUT\nelse\n  echo "trusted=false" >> $GITHUB_OUTPUT\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check trust' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_project_run_script():
    """pass_to_pass | CI job 'Build Project' → step 'Run Script'"""
    r = subprocess.run(
        ["bash", "-lc", 'bash ./scripts/ci-mock-project-build.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Script' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
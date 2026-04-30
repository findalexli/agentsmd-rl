"""Structural checks for slime agent skill files (PR #1646).

The PR adds five .claude/skills/<name>/SKILL.md files plus a
.agents/skills -> ../.claude/skills symlink. These tests verify each
skill file exists with the required frontmatter, the headline content
the gold author chose, and at least one distinctive concrete reference
the agent must include for the skill to be useful (CLI flag, file path,
or specific function signature).

We deliberately keep checks coarse-grained on prose phrasing (greps for
short technical tokens that any faithful re-author would use) and tight
on the structured pieces (frontmatter `name:` field, exact CLI flags,
file paths the skills point to).
"""

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/slime")
SKILLS_DIR = REPO / ".claude" / "skills"
AGENTS_LINK = REPO / ".agents" / "skills"


def _read(path: Path) -> str:
    assert path.exists(), f"missing file: {path}"
    return path.read_text(encoding="utf-8")


def _frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    assert m, "SKILL.md must start with a YAML frontmatter block delimited by ---"
    body = m.group(1)
    fm = {}
    for line in body.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


# --- Repo sanity (pass_to_pass: must hold on base and gold) ---


def test_repo_present():
    """Base repository is checked out at the expected commit."""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True, timeout=30
    )
    assert r.returncode == 0, r.stderr
    head = r.stdout.strip()
    # base commit OR base + gold patch applied (working tree may have new files
    # but HEAD must still be the base commit since solve.sh applies a patch
    # without committing).
    assert head == "6a3bb90e3210171e27ab7d799c8c2888e7465a1f", head


def test_repo_has_known_layout():
    """Sanity: repo layout the skills reference is real at base commit."""
    assert (REPO / "slime" / "rollout").is_dir()
    assert (REPO / "slime" / "utils" / "arguments.py").is_file()


# --- Fail-to-pass: skills must be authored ---


def test_agents_skills_symlink():
    """`.agents/skills` is a symlink pointing to ../.claude/skills.

    The slime repo expects two agent ecosystems (Claude/Codex) to find the
    same skills directory; the gold PR uses a relative symlink.
    """
    assert AGENTS_LINK.is_symlink(), f"{AGENTS_LINK} must be a symlink"
    target = AGENTS_LINK.readlink() if hasattr(AGENTS_LINK, "readlink") else Path(
        __import__("os").readlink(AGENTS_LINK)
    )
    assert str(target) == "../.claude/skills", f"unexpected symlink target: {target}"


def test_skill_add_dynamic_filter_present():
    p = SKILLS_DIR / "add-dynamic-filter" / "SKILL.md"
    text = _read(p)
    fm = _frontmatter(text)
    assert fm.get("name") == "add-dynamic-filter", fm
    assert "description" in fm and len(fm["description"]) > 20

    # All four hook CLI flags the skill exists to teach.
    for flag in [
        "--dynamic-sampling-filter-path",
        "--buffer-filter-path",
        "--rollout-sample-filter-path",
        "--rollout-all-samples-process-path",
    ]:
        assert flag in text, f"missing CLI flag {flag} in {p}"

    # File-path references that ground the skill in real source files.
    for ref in [
        "slime/rollout/filter_hub/base_types.py",
        "slime/rollout/sglang_rollout.py",
        "slime/rollout/data_source.py",
    ]:
        assert ref in text, f"missing reference {ref} in {p}"


def test_skill_add_eval_dataset_config_present():
    p = SKILLS_DIR / "add-eval-dataset-config" / "SKILL.md"
    text = _read(p)
    fm = _frontmatter(text)
    assert fm.get("name") == "add-eval-dataset-config", fm

    for flag in ["--eval-config", "--eval-prompt-data", "--eval-interval"]:
        assert flag in text, f"missing CLI flag {flag} in {p}"

    for ref in [
        "slime/utils/eval_config.py",
        "slime/utils/arguments.py",
    ]:
        assert ref in text, f"missing reference {ref} in {p}"


def test_skill_add_reward_function_present():
    p = SKILLS_DIR / "add-reward-function" / "SKILL.md"
    text = _read(p)
    fm = _frontmatter(text)
    assert fm.get("name") == "add-reward-function", fm

    for flag in ["--custom-rm-path", "--custom-reward-post-process-path"]:
        assert flag in text, f"missing CLI flag {flag} in {p}"

    # Skill must mention both single-sample and group/batch reward modes
    # (this is the central decision the skill explains to agents).
    assert "--group-rm" in text, f"reward skill must mention --group-rm switch: {p}"

    for ref in [
        "slime/rollout/rm_hub/__init__.py",
        "slime/ray/rollout.py",
    ]:
        assert ref in text, f"missing reference {ref} in {p}"


def test_skill_add_rollout_function_present():
    p = SKILLS_DIR / "add-rollout-function" / "SKILL.md"
    text = _read(p)
    fm = _frontmatter(text)
    assert fm.get("name") == "add-rollout-function", fm

    assert "--rollout-function-path" in text, p

    # Output dataclasses and reference rollout files.
    for token in [
        "RolloutFnTrainOutput",
        "RolloutFnEvalOutput",
        "slime/rollout/sglang_rollout.py",
        "slime/rollout/sft_rollout.py",
        "slime/rollout/base_types.py",
    ]:
        assert token in text, f"missing token {token} in {p}"


def test_skill_add_tests_and_ci_present():
    p = SKILLS_DIR / "add-tests-and-ci" / "SKILL.md"
    text = _read(p)
    fm = _frontmatter(text)
    assert fm.get("name") == "add-tests-and-ci", fm

    # CI workflow template + regeneration script are the central
    # idiosyncratic facts of slime CI: edit the .j2, then regenerate.
    for ref in [
        ".github/workflows/pr-test.yml.j2",
        ".github/workflows/generate_github_workflows.py",
    ]:
        assert ref in text, f"missing reference {ref} in {p}"


def test_all_skills_have_required_sections():
    """Every skill must carry the standard skill structure: When to Use +
    Step-by-Step Guide. This is the convention shared by all five files
    in the gold PR and what agents discovering these skills will rely on.
    """
    expected_skills = [
        "add-dynamic-filter",
        "add-eval-dataset-config",
        "add-reward-function",
        "add-rollout-function",
        "add-tests-and-ci",
    ]
    for slug in expected_skills:
        p = SKILLS_DIR / slug / "SKILL.md"
        text = _read(p)
        assert "## When to Use" in text, f"{p}: missing '## When to Use' section"
        assert "## Step-by-Step Guide" in text, f"{p}: missing '## Step-by-Step Guide' section"
        # Frontmatter must declare the slug as the skill name and carry a
        # non-trivial description so agents can discover when to invoke it.
        fm = _frontmatter(text)
        assert fm.get("name") == slug, f"{p}: frontmatter name '{fm.get('name')}' != dir slug '{slug}'"
        assert "description" in fm and len(fm["description"]) > 20,             f"{p}: description missing or too short ({len(fm.get('description', ''))} chars)"

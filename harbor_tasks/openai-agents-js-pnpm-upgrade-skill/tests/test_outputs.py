"""Behavioral tests for openai-agents-js PR #865 — pnpm-upgrade skill."""

import subprocess
from pathlib import Path

import yaml

REPO = Path("/workspace/openai-agents-js")
SKILL = REPO / ".codex/skills/pnpm-upgrade/SKILL.md"
PROMPT = REPO / ".github/codex/prompts/pnpm-upgrade.md"
WORKFLOW = REPO / ".github/workflows/pnpm-upgrade.yml"


def _read(path: Path) -> str:
    assert path.exists(), f"{path} does not exist"
    return path.read_text()


# ---------- fail_to_pass: the new SKILL.md must exist with required content ----------


def test_skill_file_exists():
    """The pnpm-upgrade SKILL.md file must be created."""
    assert SKILL.exists(), f"Expected {SKILL} to exist"
    assert SKILL.stat().st_size > 200, "SKILL.md is suspiciously small"


def test_skill_frontmatter_name():
    """SKILL.md frontmatter must declare name: pnpm-upgrade."""
    content = _read(SKILL)
    # Validate that frontmatter parses and name matches
    assert content.startswith("---\n"), "SKILL.md must start with YAML frontmatter"
    end = content.find("\n---\n", 4)
    assert end > 0, "frontmatter must be terminated with ---"
    fm = yaml.safe_load(content[4:end])
    assert isinstance(fm, dict), "frontmatter must be a YAML mapping"
    assert fm.get("name") == "pnpm-upgrade", f"frontmatter name must be pnpm-upgrade, got {fm.get('name')!r}"
    assert "description" in fm and isinstance(fm["description"], str) and len(fm["description"]) > 30, \
        "frontmatter must include a non-trivial description"


def test_skill_describes_pnpm_self_update():
    """SKILL must instruct using pnpm self-update with corepack fallback."""
    content = _read(SKILL)
    assert "pnpm self-update" in content, "must mention pnpm self-update"
    assert "corepack prepare pnpm@latest" in content, \
        "must mention 'corepack prepare pnpm@latest' as fallback"


def test_skill_aligns_package_manager():
    """SKILL must call out aligning packageManager in package.json."""
    content = _read(SKILL)
    assert "packageManager" in content, "must reference packageManager field"
    assert "package.json" in content, "must reference package.json"


def test_skill_pnpm_action_setup_step():
    """SKILL must instruct using GitHub releases API for pnpm/action-setup tag."""
    content = _read(SKILL)
    assert "pnpm/action-setup" in content, "must reference pnpm/action-setup"
    # Must point at the GitHub releases API endpoint, not just hardcode a tag
    assert "api.github.com/repos/pnpm/action-setup/releases/latest" in content, \
        "must instruct querying the GitHub releases API for the latest tag"


def test_skill_no_blanket_regex():
    """SKILL must warn against blunt search/replace across workflows."""
    content = _read(SKILL)
    # PR explicitly requires "no broad regex" / explicit edits
    lower = content.lower()
    assert ("no broad regex" in lower) or ("no blanket regex" in lower) or \
           ("blunt search/replace" in lower) or ("blunt search-replace" in lower) or \
           ("avoid multiline sed" in lower), \
        "SKILL must warn against blanket regex / sed-style replacements across workflows"


# ---------- fail_to_pass: the prompt file must exist ----------


def test_prompt_file_exists():
    """The Codex prompt for the scheduled run must exist."""
    assert PROMPT.exists(), f"Expected {PROMPT} to exist"
    content = _read(PROMPT)
    assert "pnpm-upgrade" in content
    assert "PNPM_VERSION" in content, "prompt must reference PNPM_VERSION capture step"


# ---------- fail_to_pass: the new scheduled workflow must exist ----------


def test_workflow_file_exists_and_parses():
    """The pnpm-upgrade workflow YAML must exist and parse."""
    assert WORKFLOW.exists(), f"Expected {WORKFLOW} to exist"
    doc = yaml.safe_load(_read(WORKFLOW))
    assert isinstance(doc, dict), "workflow must parse as a YAML mapping"
    # PyYAML parses bare 'on:' key as Python True. Accept either form.
    assert "jobs" in doc, "workflow must declare 'jobs'"
    triggers = doc.get("on") if "on" in doc else doc.get(True)
    assert triggers is not None, "workflow must declare an 'on:' trigger block"
    assert "schedule" in triggers, "workflow must run on schedule"
    sched = triggers["schedule"]
    assert isinstance(sched, list) and any("cron" in s for s in sched), \
        "workflow schedule must include a cron entry"
    assert "workflow_dispatch" in triggers, "workflow must support manual workflow_dispatch"


def test_workflow_uses_codex_action():
    """The workflow must invoke the Codex action with the pnpm-upgrade prompt."""
    content = _read(WORKFLOW)
    assert "openai/codex-action" in content, "must use openai/codex-action"
    assert ".github/codex/prompts/pnpm-upgrade.md" in content, \
        "must reference the pnpm-upgrade prompt file"
    assert "--skill pnpm-upgrade" in content, \
        "must pass the pnpm-upgrade skill to codex"


def test_workflow_creates_pull_request():
    """The workflow must open a PR with the upgraded toolchain (peter-evans/create-pull-request)."""
    content = _read(WORKFLOW)
    assert "peter-evans/create-pull-request" in content, \
        "must use peter-evans/create-pull-request to open the upgrade PR"
    assert "chore: upgrade pnpm toolchain" in content, \
        "PR commit/title must use the conventional 'chore: upgrade pnpm toolchain' message"


# ---------- fail_to_pass: existing workflows pinned to a specific tag ----------


def test_existing_workflows_pin_action_setup():
    """Every workflow that references pnpm/action-setup must pin to a SemVer tag, not @v4."""
    workflows_dir = REPO / ".github/workflows"
    affected = []
    for wf in workflows_dir.glob("*.yml"):
        text = wf.read_text()
        if "pnpm/action-setup@" not in text:
            continue
        affected.append(wf.name)
        # No bare @v4 / @v3 — must be a pinned x.y.z (or full SHA)
        for line in text.splitlines():
            line = line.strip()
            if "pnpm/action-setup@" not in line:
                continue
            tag = line.split("pnpm/action-setup@", 1)[1].split()[0].rstrip(",")
            # SemVer x.y.z, vX.Y.Z, or 40-char SHA
            import re
            assert re.match(r"^v?\d+\.\d+\.\d+$", tag) or re.match(r"^[0-9a-f]{40}$", tag), \
                f"{wf.name}: pnpm/action-setup pinned to non-specific tag {tag!r} — should be vX.Y.Z or full SHA"
    # Sanity: at least the four workflows from the PR must be present
    for required in ("changeset.yml", "test.yml", "update-docs.yml", "release.yml", "docs.yml"):
        assert required in affected, f"workflow {required} should reference pnpm/action-setup"


# ---------- pass_to_pass: repo-level structural sanity (must hold at base AND gold) ----------


def test_repo_clone_is_intact():
    """Sanity: the cloned repo has its expected entry-point files (pass_to_pass)."""
    assert (REPO / "AGENTS.md").exists(), "AGENTS.md must exist in the repo root"
    assert (REPO / "package.json").exists(), "package.json must exist in the repo root"
    assert (REPO / ".codex/skills").is_dir(), ".codex/skills directory must exist"


def test_yaml_workflows_all_parse():
    """All workflow YAML files must remain valid (pass_to_pass)."""
    workflows_dir = REPO / ".github/workflows"
    failures = []
    for wf in workflows_dir.glob("*.yml"):
        try:
            yaml.safe_load(wf.read_text())
        except yaml.YAMLError as e:
            failures.append(f"{wf.name}: {e}")
    assert not failures, "YAML parse errors:\n" + "\n".join(failures)


def test_git_status_clean_or_only_expected_paths():
    """Sanity check that git can describe the working tree (pass_to_pass)."""
    r = subprocess.run(["git", "status", "--porcelain"], cwd=REPO, capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, f"git status failed: {r.stderr}"

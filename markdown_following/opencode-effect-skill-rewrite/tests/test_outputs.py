"""Structural checks for the Effect SKILL.md rewrite (markdown_authoring oracle)."""
import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/opencode")
SKILL_PATH = REPO / ".opencode/skills/effect/SKILL.md"

OLD_DESCRIPTION = "Answer questions about the Effect framework"


def _read_skill() -> str:
    r = subprocess.run(
        ["cat", str(SKILL_PATH)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, f"cat failed: {r.stderr}"
    return r.stdout


def _frontmatter_description(text: str) -> str:
    m = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL | re.MULTILINE)
    assert m, "Could not locate YAML frontmatter delimited by --- ... ---"
    fm = m.group(1)
    md = re.search(r"^\s*description:\s*(.+?)\s*$", fm, re.MULTILINE)
    assert md, "Could not locate `description:` field in frontmatter"
    return md.group(1).strip()


def test_skill_file_exists():
    """SKILL.md still lives at the same path."""
    assert SKILL_PATH.exists(), f"{SKILL_PATH} does not exist"


def test_skill_description_updated():
    """Frontmatter `description:` is no longer the original generic line."""
    desc = _frontmatter_description(_read_skill())
    assert desc != OLD_DESCRIPTION, (
        f"description is still the original generic line: {desc!r}. "
        "It should be rewritten to describe the repo's actual Effect usage."
    )


def test_skill_mentions_effect_v4():
    """Skill calls out Effect v4 (the version this repo targets)."""
    text = _read_skill()
    assert "Effect v4" in text, (
        "SKILL.md should explicitly mention `Effect v4` so agents do not fall back to "
        "older Effect v2/v3 patterns from memory."
    )


def test_skill_mentions_effect_smol_reference():
    """Skill points at the local effect-smol reference clone."""
    text = _read_skill()
    assert ".opencode/references/effect-smol" in text, (
        "SKILL.md should reference the local clone path `.opencode/references/effect-smol`."
    )


def test_skill_requires_effect_fn_pattern():
    """Skill prescribes the `Effect.fn` naming pattern for traced effects."""
    text = _read_skill()
    assert "Effect.fn" in text, (
        "SKILL.md should require `Effect.fn` (the traced/named effect helper) for "
        "reusable service methods."
    )


def test_skill_requires_schema_taggederrorclass():
    """Skill prescribes `Schema.TaggedErrorClass` for typed domain errors."""
    text = _read_skill()
    assert "Schema.TaggedErrorClass" in text, (
        "SKILL.md should name `Schema.TaggedErrorClass` as the way to model typed "
        "domain errors."
    )


def test_skill_forbids_any_and_non_null_assertions():
    """Skill explicitly bans `any` and non-null assertions."""
    text = _read_skill()
    assert "any" in text and "non-null assertions" in text, (
        "SKILL.md should forbid introducing `any`, non-null assertions, unchecked "
        "casts, or older Effect APIs."
    )


def test_skill_substantively_expanded():
    """Skill is substantively longer than the base placeholder."""
    text = _read_skill()
    line_count = text.count("\n") + 1
    assert line_count >= 25, (
        f"SKILL.md only has {line_count} lines; it should be substantively expanded "
        "with concrete rules covering Effect v4 API patterns, schemas, errors, "
        "HTTP handler shape, and testing guidance."
    )


def test_skill_keeps_yaml_frontmatter_structure():
    """Frontmatter still has `name: effect` and a `description:` line."""
    text = _read_skill()
    m = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL | re.MULTILINE)
    assert m, "YAML frontmatter delimiters missing"
    fm = m.group(1)
    assert re.search(r"^\s*name:\s*effect\s*$", fm, re.MULTILINE), \
        "frontmatter must keep `name: effect`"
    assert re.search(r"^\s*description:\s*\S", fm, re.MULTILINE), \
        "frontmatter must keep a non-empty `description:`"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_e2e_run_app_e2e_tests():
    """pass_to_pass | CI job 'e2e' → step 'Run app e2e tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/app test:e2e:local'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run app e2e tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_run_unit_tests():
    """pass_to_pass | CI job 'unit' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun turbo test:ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_typecheck_run_typecheck():
    """pass_to_pass | CI job 'typecheck' → step 'Run typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
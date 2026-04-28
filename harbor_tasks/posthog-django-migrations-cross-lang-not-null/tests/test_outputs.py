"""Behavioral tests for the django-migrations SKILL.md cross-language NOT NULL hazard task.

This is a markdown_authoring task: the agent must add guidance to the
`.agents/skills/django-migrations/SKILL.md` file about a Django/Postgres
cross-language NOT NULL hazard. Tests verify the gold rule is present
verbatim or near-verbatim by grepping for distinctive signal lines.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/posthog")
SKILL = REPO / ".agents/skills/django-migrations/SKILL.md"


def _read_skill() -> str:
    assert SKILL.exists(), f"Skill file missing: {SKILL}"
    return SKILL.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# fail_to_pass — these MUST fail on the base commit and pass on a correct fix
# ---------------------------------------------------------------------------


def test_skill_has_cross_language_section_heading() -> None:
    """The skill must add a new section heading about the cross-language NOT NULL hazard."""
    text = _read_skill()
    # Match a markdown heading containing the distinctive phrase. Allow ## or ###
    # so the agent has some flexibility in heading depth.
    pattern = re.compile(
        r"^#{2,3}\s+.*cross-language.*not\s*null.*hazard.*$",
        re.IGNORECASE | re.MULTILINE,
    )
    assert pattern.search(text), (
        "Expected a markdown section heading about the cross-language NOT NULL hazard "
        "(e.g. '## Cross-language `NOT NULL` hazard'), but none was found in SKILL.md."
    )


def test_skill_explains_python_only_default() -> None:
    """The skill must explain that Django default=... is Python-only, not Postgres-level."""
    text = _read_skill().lower()
    # The agent must explain that Django's `default=...` is applied only in Python
    # (so Postgres sees no column DEFAULT). Accept several phrasings.
    has_default_mention = (
        "default=list" in text
        or "default=dict" in text
        or "default=<callable>" in text
        or "default=callable" in text
    )
    has_python_only = (
        "python only" in text
        or "python-only" in text
        or "applied in python" in text
        or "python side" in text
        or "python-side" in text
    )
    has_postgres_no_default = (
        "no column default" in text
        or "no column `default`" in text
        or "without a column default" in text
        or "postgres sees" in text
        or "not visible to postgres" in text
        or "invisible to postgres" in text
    )
    assert has_default_mention, (
        "SKILL.md must mention Django's `default=list` / `default=dict` / "
        "`default=<callable>` pattern in its hazard explanation."
    )
    assert has_python_only, (
        "SKILL.md must state that Django's `default=...` is applied in Python only."
    )
    assert has_postgres_no_default, (
        "SKILL.md must explain that Postgres sees no column DEFAULT (the Python-side "
        "default does not propagate to the database)."
    )


def test_skill_recommends_runsql_default() -> None:
    """The skill must show the migrations.RunSQL ALTER COLUMN ... SET DEFAULT remediation."""
    text = _read_skill()
    # Lower-cased copy for case-insensitive checks of SQL fragments.
    lower = text.lower()
    has_runsql = "migrations.runsql" in lower or "RunSQL(" in text
    has_alter_set_default = bool(
        re.search(
            r"alter\s+table\s+[^\n]*\balter\s+column\b[^\n]*\bset\s+default\b",
            lower,
        )
    )
    assert has_runsql, (
        "SKILL.md must show the `migrations.RunSQL(...)` pattern as a remediation."
    )
    assert has_alter_set_default, (
        "SKILL.md must include an `ALTER TABLE ... ALTER COLUMN ... SET DEFAULT ...` "
        "snippet to set a Postgres-level default."
    )


def test_skill_mentions_non_django_writers() -> None:
    """The skill must call out non-Django writers (plugin-server, rust, etc.) of the table."""
    text = _read_skill().lower()
    # The hazard is about external writers; the skill should name at least two
    # of the typical sources.
    targets = ["nodejs", "rust", "temporal", "raw sql", "raw-sql", "plugin-server", "plugin server"]
    hits = [t for t in targets if t in text]
    assert len(hits) >= 2, (
        "SKILL.md must mention at least two non-Django writers that may bypass "
        "Django's Python-side default (e.g. plugin-server `nodejs/`, `rust/`, Temporal workers, "
        f"ad-hoc raw-SQL scripts). Found: {hits}"
    )


def test_classify_step_links_to_hazard() -> None:
    """Step 1 (Classify) of the workflow must reference the new hazard section."""
    text = _read_skill()
    # Find the line for step 1 (numbered list item starting with "1. **Classify**").
    classify_match = re.search(
        r"^1\.\s+\*\*Classify\*\*[^\n]*$", text, re.MULTILINE
    )
    assert classify_match, "Step 1 ('1. **Classify** ...') line not found in SKILL.md."
    classify_line = classify_match.group(0).lower()
    # The agent must add a cross-reference from step 1 to the new hazard section.
    has_link = (
        "cross-language" in classify_line
        and ("not null" in classify_line or "not null" in classify_line or "not-null" in classify_line)
    )
    assert has_link, (
        "Step 1 ('Classify') of the Workflow must reference the cross-language NOT NULL "
        "hazard so readers see the cross-link from the classify step."
    )


def test_grep_signal_via_subprocess() -> None:
    """Subprocess sanity: grep for the distinctive section heading in SKILL.md."""
    r = subprocess.run(
        ["grep", "-iE", r"cross-language[^\n]*not[ -]?null[^\n]*hazard", str(SKILL)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        "grep could not find a 'cross-language ... NOT NULL ... hazard' line in SKILL.md.\n"
        f"stdout={r.stdout!r}\nstderr={r.stderr!r}"
    )


# ---------------------------------------------------------------------------
# pass_to_pass — must hold on both base and post-fix commits
# ---------------------------------------------------------------------------


def test_skill_frontmatter_intact() -> None:
    """The required YAML frontmatter (name, description) must be preserved."""
    text = _read_skill()
    # Frontmatter must start the file and contain `name:` and `description:`.
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert fm, "SKILL.md must start with a YAML frontmatter block delimited by '---'."
    body = fm.group(1)
    assert re.search(r"^name:\s*django-migrations\s*$", body, re.MULTILINE), (
        "Frontmatter must contain `name: django-migrations`."
    )
    assert re.search(r"^description:\s*.+", body, re.MULTILINE), (
        "Frontmatter must contain a non-empty `description:` field."
    )


def test_skill_preserves_workflow_steps() -> None:
    """All four original Workflow steps must remain (Classify, Generate, Apply, Validate)."""
    text = _read_skill()
    # The four original numbered steps must still be present.
    for step_num, keyword in (
        (1, "Classify"),
        (2, "Generate"),
        (3, "Apply safety rules"),
        (4, "Validate"),
    ):
        pattern = rf"^{step_num}\.\s+\*\*{re.escape(keyword)}"
        assert re.search(pattern, text, re.MULTILINE), (
            f"Workflow step {step_num} ('{keyword}') is missing — original "
            "workflow content must be preserved."
        )


def test_skill_clickhouse_pointer_intact() -> None:
    """The pre-existing ClickHouse-migrations pointer must be preserved."""
    text = _read_skill()
    assert "clickhouse-migrations" in text, (
        "SKILL.md must keep the existing pointer to the `clickhouse-migrations` skill."
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_storybook_build_storybook():
    """pass_to_pass | CI job 'Build Storybook' → step 'Build Storybook'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter=@posthog/storybook build --test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build Storybook' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_hog_tests_check_if_antlr_definitions_are_up_to_dat():
    """pass_to_pass | CI job 'Hog tests' → step 'Check if ANTLR definitions are up to date'"""
    r = subprocess.run(
        ["bash", "-lc", 'antlr | grep "Version" && npm run grammar:build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check if ANTLR definitions are up to date' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_hog_tests_check_if_stl_bytecode_is_up_to_date():
    """pass_to_pass | CI job 'Hog tests' → step 'Check if STL bytecode is up to date'"""
    r = subprocess.run(
        ["bash", "-lc", 'python -m common.hogvm.stl.compile'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check if STL bytecode is up to date' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_hog_tests_run_hogvm_python_tests():
    """pass_to_pass | CI job 'Hog tests' → step 'Run HogVM Python tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pytest common/hogvm'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run HogVM Python tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_hog_tests_run_hogvm_typescript_tests():
    """pass_to_pass | CI job 'Hog tests' → step 'Run HogVM TypeScript tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter=@posthog/hogvm install --frozen-lockfile && pnpm --filter=@posthog/hogvm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run HogVM TypeScript tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_hog_tests_run_hog_tests():
    """pass_to_pass | CI job 'Hog tests' → step 'Run Hog tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter=@posthog/hogvm install --frozen-lockfile && pnpm --filter=@posthog/hogvm compile:stl && ./test.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Hog tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build___test_type_check():
    """pass_to_pass | CI job 'Build & Test' → step 'Type check'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Type check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build___test_run_tests():
    """pass_to_pass | CI job 'Build & Test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
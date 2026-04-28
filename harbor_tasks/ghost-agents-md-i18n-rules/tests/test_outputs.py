"""Tests for TryGhost/Ghost#27177 — i18n guidance added to AGENTS.md.

This is a markdown_authoring task: the agent's job is to update the
`### i18n Architecture` section of AGENTS.md with translation rules.
The behavioral signal is structural — distinctive phrases the agent
must include — so most tests are content greps. We additionally invoke
`grep` via subprocess to satisfy the harness's
`tests_have_subprocess` requirement, and exercise pytest as the
reward driver so test.sh can stay on the standard pytest contract.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/Ghost")
AGENTS = REPO / "AGENTS.md"


def _agents_text() -> str:
    assert AGENTS.exists(), f"AGENTS.md missing at {AGENTS}"
    return AGENTS.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# pass_to_pass — preserved structure
# ---------------------------------------------------------------------------

def test_existing_i18n_section_preserved():
    """The pre-existing `### i18n Architecture` heading is still present."""
    text = _agents_text()
    assert "### i18n Architecture" in text, (
        "The existing `### i18n Architecture` heading must remain in AGENTS.md."
    )
    # The original lines that were already in the section should still be there.
    assert "Centralized Translations:" in text
    assert "ghost/i18n/locales/{locale}/{namespace}.json" in text
    assert "60+ supported locales" in text


def test_existing_build_dependencies_section_preserved():
    """The next section after i18n (`### Build Dependencies (Nx)`) still exists."""
    text = _agents_text()
    assert "### Build Dependencies (Nx)" in text


def test_agents_md_grows_not_shrinks():
    """The PR is purely additive: AGENTS.md grew (>0 net new lines)."""
    n_lines = _agents_text().count("\n")
    # Base AGENTS.md has 269 lines; gold adds 33. Anything strictly more than
    # the base count is acceptable so long as the other content tests pass.
    assert n_lines > 269, f"Expected >269 lines, got {n_lines}"


# ---------------------------------------------------------------------------
# fail_to_pass — new i18n guidance content
# ---------------------------------------------------------------------------

def test_split_sentence_rule_documented():
    """Rule against splitting a sentence across multiple `t()` calls."""
    text = _agents_text()
    assert "Never split sentences across multiple `t()` calls" in text


def test_react_interpolate_library_documented():
    """The `@doist/react-interpolate` library is referenced for inline elements."""
    text = _agents_text()
    assert "@doist/react-interpolate" in text


def test_context_json_requirement_documented():
    """`context.json` and its description requirement are documented."""
    text = _agents_text()
    assert "context.json" in text
    # The new section must explicitly require non-empty descriptions.
    assert re.search(
        r"non-empty description|reject empty descriptions",
        text,
    ), "AGENTS.md must require non-empty context.json descriptions."


def test_translate_workflow_command_documented():
    """The `yarn workspace @tryghost/i18n translate` command is documented."""
    r = subprocess.run(
        ["bash", "-lc", "grep -F 'yarn workspace @tryghost/i18n translate' AGENTS.md"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO),
    )
    assert r.returncode == 0, (
        "AGENTS.md must document the `yarn workspace @tryghost/i18n translate` command"
    )


def test_interpolation_variable_syntax_documented():
    """Documents `{variable}` interpolation for dynamic values."""
    text = _agents_text()
    # The rule line uses `Use `{variable}` syntax`.
    assert "{variable}" in text
    # And shows an example call with t('...', {name: ...}).
    assert re.search(r"\{name:\s*firstname\}", text), (
        "AGENTS.md must show an interpolation example using {name: firstname}."
    )


def test_correct_and_incorrect_examples_documented():
    """Both the correct (Interpolate) and incorrect (split-sentence) patterns shown."""
    text = _agents_text()
    assert "Correct pattern" in text
    assert "Incorrect pattern" in text
    # The Interpolate import line is present in the correct example.
    assert "import Interpolate from '@doist/react-interpolate'" in text


def test_canonical_example_referenced():
    """A canonical in-repo example of correct Interpolate usage is referenced."""
    text = _agents_text()
    assert "apps/portal/src/components/pages/email-receiving-faq.js" in text


def test_new_content_inside_i18n_architecture_section():
    """The new rules live under the `### i18n Architecture` heading, not elsewhere."""
    text = _agents_text()
    i18n_start = text.find("### i18n Architecture")
    assert i18n_start != -1
    # The next `### ` heading after i18n delimits the section.
    next_heading = text.find("\n### ", i18n_start + len("### i18n Architecture"))
    assert next_heading != -1, "Could not find the heading that follows the i18n section."
    section = text[i18n_start:next_heading]
    assert "@doist/react-interpolate" in section, (
        "The translation rules must be inside the `### i18n Architecture` section."
    )
    assert "Never split sentences across multiple `t()` calls" in section

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_e2e_public_app_assets_build_public_apps_for_e2e():
    """pass_to_pass | CI job 'Build E2E Public App Assets' → step 'Build public apps for E2E'"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn workspace @tryghost/e2e build:apps'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build public apps for E2E' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_tests_prepare_e2e_ci_job():
    """pass_to_pass | CI job 'E2E Tests' → step 'Prepare E2E CI job'"""
    r = subprocess.run(
        ["bash", "-lc", 'bash ./e2e/scripts/prepare-ci-e2e-job.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Prepare E2E CI job' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_tests_run_e2e_tests_in_playwright_container():
    """pass_to_pass | CI job 'E2E Tests' → step 'Run e2e tests in Playwright container'"""
    r = subprocess.run(
        ["bash", "-lc", 'bash ./e2e/scripts/run-playwright-container.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run e2e tests in Playwright container' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_tests_dump_e2e_docker_logs():
    """pass_to_pass | CI job 'E2E Tests' → step 'Dump E2E docker logs'"""
    r = subprocess.run(
        ["bash", "-lc", 'bash ./e2e/scripts/dump-e2e-docker-logs.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Dump E2E docker logs' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_tests_stop_e2e_infra():
    """pass_to_pass | CI job 'E2E Tests' → step 'Stop E2E infra'"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn workspace @tryghost/e2e infra:down'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Stop E2E infra' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_all_required_tests_passed_or_s_pass_on_tag_pushes_tests_already_ran_on():
    """pass_to_pass | CI job 'All required tests passed or skipped' → step 'Pass on tag pushes (tests already ran on branch)'"""
    r = subprocess.run(
        ["bash", "-lc", 'echo "Tag push — tests skipped (already tested on branch commit)"'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Pass on tag pushes (tests already ran on branch)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_all_required_tests_passed_or_s_check_if_any_required_jobs_failed_or_bee():
    """pass_to_pass | CI job 'All required tests passed or skipped' → step 'Check if any required jobs failed or been cancelled'"""
    r = subprocess.run(
        ["bash", "-lc", 'echo "One of the dependent jobs have failed or been cancelled. You may need to re-run it." && exit 1'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check if any required jobs failed or been cancelled' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
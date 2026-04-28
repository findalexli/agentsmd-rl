"""Verify the e2e testing guide gained the three new state-first sections.

This is a markdown_authoring task: the gold PR primarily adds three new H3
sections to packages/app/e2e/AGENTS.md formalising state-first conventions.
We grep the file via subprocess (so the test exercises the on-disk artifact
the agent produced, not a re-implementation of file reading).
"""
import subprocess
from pathlib import Path

REPO = Path("/workspace/opencode")
GUIDE = REPO / "packages/app/e2e/AGENTS.md"


def _grep(pattern: str) -> bool:
    """Return True iff `pattern` (fixed string, anchored as a line) is present
    in the e2e testing guide. We invoke real `grep` so the test exercises the
    file as produced by the agent, not an in-process Python re-read."""
    r = subprocess.run(
        ["grep", "-Fxq", pattern, str(GUIDE)],
        capture_output=True,
    )
    return r.returncode == 0


def _grep_substr(pattern: str) -> bool:
    r = subprocess.run(
        ["grep", "-Fq", pattern, str(GUIDE)],
        capture_output=True,
    )
    return r.returncode == 0


def test_guide_file_present():
    """Pass-to-pass: the e2e testing guide exists at the canonical path."""
    r = subprocess.run(["test", "-f", str(GUIDE)], capture_output=True)
    assert r.returncode == 0, f"missing {GUIDE}"


def test_section_wait_on_state():
    """Fail-to-pass: an H3 section titled 'Wait on state' exists."""
    assert _grep("### Wait on state"), (
        "expected an H3 heading '### Wait on state' in "
        f"{GUIDE.relative_to(REPO)}"
    )


def test_section_add_hooks():
    """Fail-to-pass: an H3 section titled 'Add hooks' exists."""
    assert _grep("### Add hooks"), (
        f"expected an H3 heading '### Add hooks' in {GUIDE.relative_to(REPO)}"
    )


def test_section_prefer_helpers():
    """Fail-to-pass: an H3 section titled 'Prefer helpers' exists."""
    assert _grep("### Prefer helpers"), (
        "expected an H3 heading '### Prefer helpers' in "
        f"{GUIDE.relative_to(REPO)}"
    )


def test_wait_on_state_mentions_waitForTimeout():
    """Fail-to-pass: the 'Wait on state' section names `page.waitForTimeout`
    as the wall-clock anti-pattern to avoid. Without naming it, the rule is
    too vague to act on."""
    # Slice file text around the heading and assert waitForTimeout appears
    # before the next H2/H3.
    text = GUIDE.read_text()
    needle = "### Wait on state"
    if needle not in text:
        # Already covered by test_section_wait_on_state
        raise AssertionError("'### Wait on state' heading missing")
    start = text.index(needle)
    after = text[start + len(needle):]
    # End of section: next H2 or H3
    end = len(after)
    for marker in ("\n## ", "\n### "):
        idx = after.find(marker)
        if idx >= 0 and idx < end:
            end = idx
    section = after[:end]
    assert "page.waitForTimeout" in section, (
        "'Wait on state' section should name `page.waitForTimeout(...)` as "
        "the wall-clock anti-pattern; got section body without it"
    )


def test_add_hooks_references_terminal_driver_style():
    """Fail-to-pass: the 'Add hooks' section points at the existing terminal
    test-driver as the style to mirror — `packages/app/src/testing/terminal.ts`."""
    text = GUIDE.read_text()
    needle = "### Add hooks"
    if needle not in text:
        raise AssertionError("'### Add hooks' heading missing")
    start = text.index(needle)
    after = text[start + len(needle):]
    end = len(after)
    for marker in ("\n## ", "\n### "):
        idx = after.find(marker)
        if idx >= 0 and idx < end:
            end = idx
    section = after[:end]
    assert "packages/app/src/testing/terminal.ts" in section, (
        "'Add hooks' section should cite "
        "`packages/app/src/testing/terminal.ts` as the style template"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_typecheck_run_typecheck():
    """pass_to_pass | CI job 'typecheck' → step 'Run typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_run_unit_tests():
    """pass_to_pass | CI job 'unit' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun turbo test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_run_app_e2e_tests():
    """fail_to_pass | CI job 'e2e' → step 'Run app e2e tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/app test:e2e:local'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run app e2e tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
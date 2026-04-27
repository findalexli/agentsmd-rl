"""Behavioral checks for TanStack/router PR #6671 — AGENTS.md update.

The PR replaces `npx nx`/`npx vitest` invocations with `pnpm nx ...` style
and adds a new "Agent execution guardrails" subsection. We verify both the
verbatim additions and the removal of the old `npx nx`/`npx vitest`
recommendations.
"""

import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/router")
AGENTS_MD = REPO / "AGENTS.md"


def _read_agents_md() -> str:
    assert AGENTS_MD.exists(), f"AGENTS.md missing at {AGENTS_MD}"
    return AGENTS_MD.read_text(encoding="utf-8")


# ----------------------------- Pass-to-pass -------------------------------- #

def test_repo_checked_out():
    """The TanStack/router repo is checked out at the expected base commit."""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"git rev-parse failed: {r.stderr}"
    head = r.stdout.strip()
    # Either base commit (nop) or any descendant after applying changes
    assert len(head) == 40, f"unexpected HEAD format: {head}"


def test_agents_md_present_and_nonempty():
    """AGENTS.md remains a non-empty markdown file."""
    text = _read_agents_md()
    assert len(text) > 500, "AGENTS.md should retain its substantive content"
    assert text.startswith("# AGENTS.md"), "AGENTS.md must keep its top-level heading"


# ---------------------------- Fail-to-pass --------------------------------- #

def test_agent_execution_guardrails_subsection_added():
    """A new bullet introduces 'Agent execution guardrails (important):'."""
    text = _read_agents_md()
    assert "**Agent execution guardrails (important):**" in text, (
        "AGENTS.md must add a bolded 'Agent execution guardrails (important):' "
        "bullet under the 'Dev environment tips' section."
    )


def test_sandbox_command_documented():
    """The sandbox-mode command is documented verbatim."""
    text = _read_agents_md()
    assert "CI=1 NX_DAEMON=false pnpm nx run <project>:<target> --outputStyle=stream --skipRemoteCache" in text, (
        "AGENTS.md must document the sandbox Nx invocation verbatim."
    )


def test_one_command_at_a_time_rule():
    """Single-command-at-a-time rule is included."""
    text = _read_agents_md()
    assert "Run only one Nx command at a time." in text, (
        "AGENTS.md must instruct agents to run only one Nx command at a time."
    )


def test_nx_reset_recovery_rule():
    """The hang-recovery rule references `pnpm nx reset` and the ~20s threshold."""
    text = _read_agents_md()
    assert "pnpm nx reset" in text, "AGENTS.md must mention `pnpm nx reset`."
    assert "20 seconds" in text, (
        "AGENTS.md must mention the ~20-second no-output threshold for hang recovery."
    )


def test_no_loop_retries_rule():
    """Escalation rule against indefinite retries is present."""
    text = _read_agents_md()
    assert "Do not loop retries indefinitely." in text, (
        "AGENTS.md must include the 'Do not loop retries indefinitely.' rule."
    )


def test_pnpm_nx_show_projects_replacement():
    """The `pnpm nx show projects` form is used (replacing `npx nx show projects`)."""
    text = _read_agents_md()
    assert "pnpm nx show projects" in text, (
        "AGENTS.md must document `pnpm nx show projects` (replacing `npx nx show projects`)."
    )


def test_no_npx_nx_show_projects_left():
    """The old `npx nx show projects` form has been removed."""
    text = _read_agents_md()
    assert "npx nx show projects" not in text, (
        "Old `npx nx show projects` invocation must be removed."
    )


def test_no_npx_nx_run_left():
    """No `npx nx run` invocations remain anywhere in AGENTS.md."""
    text = _read_agents_md()
    assert "npx nx run" not in text, (
        "All `npx nx run ...` invocations must be replaced by `pnpm nx run ...`."
    )


def test_no_npx_nx_affected_left():
    """No `npx nx affected` invocations remain."""
    text = _read_agents_md()
    assert "npx nx affected" not in text, (
        "All `npx nx affected` invocations must be replaced by `pnpm nx affected`."
    )


def test_no_npx_vitest_run_left():
    """Direct `npx vitest run` invocations are no longer recommended."""
    text = _read_agents_md()
    assert "npx vitest run" not in text, (
        "AGENTS.md must no longer recommend running `npx vitest run` directly; "
        "filter args should go through `pnpm nx run ...:test:unit -- ...`."
    )

"""Structural + behavioral checks for the monitor-run SKILL.md rewrite.

The agent's task is to rewrite ``skills/monitor-run/SKILL.md`` so that it
documents a runbook-style monitoring procedure with periodic STATUS.md
check-ins and tmux-mediated restart safety. The tests below assert that
the distinctive new content is present, that the YAML frontmatter is
preserved, and that the file is still well-formed markdown.
"""

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/prime-rl")
SKILL = REPO / "skills" / "monitor-run" / "SKILL.md"


def _read_skill() -> str:
    assert SKILL.exists(), f"{SKILL} does not exist"
    return SKILL.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Fail-to-pass: distinctive new content from the gold rewrite
# ---------------------------------------------------------------------------


def test_runbook_section_present():
    """The rewrite organises the skill around a top-level Runbook section."""
    text = _read_skill()
    assert re.search(r"(?m)^## Runbook\s*$", text), (
        "expected a top-level '## Runbook' section in skills/monitor-run/SKILL.md"
    )


def test_status_md_periodic_checkin_documented():
    """A STATUS.md check-in template must be documented."""
    text = _read_skill()
    assert "STATUS.md" in text, "STATUS.md (the per-run status file) must be documented"
    # The check-in template documents Step / Health markers that the agent
    # writes at every check-in.
    assert "**Step**" in text, "STATUS.md template must include a **Step** field"
    assert "**Health**" in text, "STATUS.md template must include a **Health** field"


def test_tmux_send_keys_restart_safety():
    """Restart commands must be dispatched via tmux send-keys, not run directly."""
    text = _read_skill()
    assert "tmux send-keys" in text, (
        "the skill must instruct the agent to dispatch restart commands via "
        "'tmux send-keys' to the Launcher window"
    )
    # The Launcher window name is part of the safety contract.
    assert "Launcher" in text, "the Launcher tmux window must be named"


def test_reference_section_present():
    """Restructure splits the skill into Runbook (what to do) + Reference (how)."""
    text = _read_skill()
    assert re.search(r"(?m)^## Reference\s*$", text), (
        "expected a top-level '## Reference' section in skills/monitor-run/SKILL.md"
    )


def test_errors_and_warnings_section():
    """An 'Errors and warnings' section with grep guidance must exist."""
    text = _read_skill()
    assert re.search(r"(?mi)^### Errors and warnings\s*$", text), (
        "expected an '### Errors and warnings' subsection under Reference"
    )
    # Grep guidance for log scanning is part of the new content.
    assert re.search(r'grep .*"WARNING\|ERROR"', text) or 'WARNING|ERROR' in text, (
        "errors-and-warnings section should show how to grep for WARNING/ERROR"
    )


def test_vllm_metrics_endpoint_documented():
    """vLLM Prometheus metrics endpoint guidance must be present."""
    text = _read_skill()
    assert "vllm:gpu_cache_usage_perc" in text, (
        "vLLM KV cache metric 'vllm:gpu_cache_usage_perc' must be documented"
    )
    assert "/metrics" in text, "the vLLM /metrics endpoint must be referenced"


# ---------------------------------------------------------------------------
# Pass-to-pass: structural sanity (must hold both at base and after rewrite)
# ---------------------------------------------------------------------------


def test_frontmatter_preserved():
    """YAML frontmatter (name + description) must be preserved by the rewrite."""
    text = _read_skill()
    # Frontmatter is the first thing in the file.
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    assert m is not None, "SKILL.md must start with a '---' YAML frontmatter block"
    fm = m.group(1)
    assert re.search(r"(?m)^name:\s*monitor-run\s*$", fm), (
        "frontmatter must keep 'name: monitor-run'"
    )
    assert re.search(r"(?m)^description:\s*\S", fm), (
        "frontmatter must keep a non-empty 'description:' field"
    )


def test_file_is_well_formed_markdown():
    """Sanity: the file parses as valid UTF-8 and contains balanced code fences."""
    raw = SKILL.read_bytes()
    text = raw.decode("utf-8")  # raises if invalid UTF-8
    fences = re.findall(r"(?m)^```", text)
    assert len(fences) % 2 == 0, (
        f"unbalanced ``` code fences in SKILL.md ({len(fences)} found)"
    )


def test_git_repo_intact():
    """The repo working tree must still be a valid git checkout (no corruption)."""
    r = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"git rev-parse failed:\n{r.stderr}"
    assert r.stdout.strip() == str(REPO), (
        f"unexpected toplevel: {r.stdout.strip()!r} (expected {REPO})"
    )

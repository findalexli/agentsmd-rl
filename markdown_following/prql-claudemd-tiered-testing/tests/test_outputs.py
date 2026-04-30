"""Behavioral oracle for prql-claudemd-tiered-testing.

This is a markdown_authoring task — the PR's only change is to the root
CLAUDE.md "Development Workflow" section. The structural greps below are a
sanity gate; the real evaluation signal is the Gemini Track-2 semantic diff
defined in eval_manifest.yaml.config_edits.
"""

import subprocess
from pathlib import Path

REPO = Path("/workspace/prql")
CLAUDE_MD = REPO / "CLAUDE.md"


def _read_claude_md() -> str:
    assert CLAUDE_MD.is_file(), f"CLAUDE.md missing at {CLAUDE_MD}"
    return CLAUDE_MD.read_text(encoding="utf-8")


def _grep(pattern: str, path: Path) -> subprocess.CompletedProcess:
    """Run plain `grep -F` (fixed-string) so the caller doesn't need to
    worry about regex escaping in distinctive phrases. `grep` exits 0 on
    match, 1 on no-match. Use `subprocess.run` so the test exercises a real
    process and isn't pure Python text inspection."""
    return subprocess.run(
        ["grep", "-F", "-q", pattern, str(path)],
        capture_output=True,
        timeout=30,
    )


# ---------------------------------------------------------------------------
# fail_to_pass — these MUST fail at the base commit and pass on the gold edit
# ---------------------------------------------------------------------------

def test_claudemd_introduces_tiered_testing_phrase():
    """Gold rewrites the workflow framing as a 'tiered testing approach'."""
    r = _grep("tiered testing approach", CLAUDE_MD)
    assert r.returncode == 0, (
        "CLAUDE.md does not describe a 'tiered testing approach'. "
        "Found content begins with:\n" + _read_claude_md()[:400]
    )


def test_claudemd_documents_prqlc_pull_request_command():
    """Gold introduces `task prqlc:pull-request` as the default ~30s validation."""
    r = _grep("task prqlc:pull-request", CLAUDE_MD)
    assert r.returncode == 0, (
        "CLAUDE.md does not mention `task prqlc:pull-request`. "
        "Default validation should be this command, not `task test-all`."
    )


def test_claudemd_has_cross_binding_tier():
    """Gold adds a 'Cross-binding changes only' tier that scopes `task test-all`."""
    r = _grep("Cross-binding changes only", CLAUDE_MD)
    assert r.returncode == 0, (
        "CLAUDE.md is missing the 'Cross-binding changes only' tier. "
        "`task test-all` should be scoped to JS/Python/wasm binding changes."
    )


def test_claudemd_inner_loop_retimed_to_5s():
    """Gold's inner-loop heading is `**Inner loop** (during development, ~5s):`.

    The base used `**Inner loop** (fast, focused, <5s):`. The phrase
    'during development' is distinctive enough to disambiguate.
    """
    r = _grep("during development", CLAUDE_MD)
    assert r.returncode == 0, (
        "Inner-loop heading does not include 'during development'. "
        "Gold reframes the inner loop as the during-development tier."
    )


# ---------------------------------------------------------------------------
# pass_to_pass — must hold both pre- and post-edit (guards against the agent
# deleting unchanged sections of CLAUDE.md while editing the workflow block).
# ---------------------------------------------------------------------------

def test_claudemd_keeps_task_test_all_reference():
    """Gold keeps `task test-all` (now scoped to bindings) — it must not vanish."""
    r = _grep("task test-all", CLAUDE_MD)
    assert r.returncode == 0, "CLAUDE.md no longer references `task test-all`."


def test_claudemd_keeps_tests_section():
    """The `## Tests` section (insta snapshots guidance) must remain intact."""
    r = _grep("## Tests", CLAUDE_MD)
    assert r.returncode == 0, "CLAUDE.md is missing its `## Tests` section."


def test_claudemd_keeps_error_messages_section():
    """The `## Error Messages` section (2nd-person guidance) must remain intact."""
    r = _grep("## Error Messages", CLAUDE_MD)
    assert r.returncode == 0, "CLAUDE.md is missing its `## Error Messages` section."


def test_claudemd_keeps_linting_section():
    """The `## Linting` section must remain intact."""
    r = _grep("## Linting", CLAUDE_MD)
    assert r.returncode == 0, "CLAUDE.md is missing its `## Linting` section."

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_grammars_build_grammar():
    """pass_to_pass | CI job 'test-grammars' → step 'Build grammar'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run build'], cwd=os.path.join(REPO, 'grammars/prql-lezer/'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build grammar' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_grammars_test_grammar():
    """pass_to_pass | CI job 'test-grammars' → step 'Test grammar'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run test'], cwd=os.path.join(REPO, 'grammars/prql-lezer/'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test grammar' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
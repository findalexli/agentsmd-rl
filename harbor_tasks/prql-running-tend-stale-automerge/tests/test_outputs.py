"""Tests for prql running-tend SKILL.md stale-automerge fix.

Track 1 sanity gate for a markdown_authoring task. The agent must update
`.claude/skills/running-tend/SKILL.md` so that:

  - the stale claim "auto-merges single-commit ..." is gone, and
  - the skill clarifies the new merge status (manual / removed / not
    configured / etc.) so future tend runs don't assume bot PRs auto-merge.

The deeper semantic comparison happens in Track 2 via `config_edits` in
eval_manifest.yaml.
"""
import subprocess
from pathlib import Path

REPO = Path("/workspace/prql")
SKILL = REPO / ".claude/skills/running-tend/SKILL.md"
WORKFLOW = REPO / ".github/workflows/pull-request-target.yaml"


# ── pass_to_pass ────────────────────────────────────────────────────────────

def test_skill_file_present():
    """The running-tend SKILL.md exists at its expected path (p2p)."""
    r = subprocess.run(
        ["test", "-f", str(SKILL)], capture_output=True,
    )
    assert r.returncode == 0, f"SKILL.md missing at {SKILL}"


def test_ci_structure_section_preserved():
    """The '## CI structure' section heading is preserved (p2p)."""
    r = subprocess.run(
        ["grep", "-c", "^## CI structure$", str(SKILL)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"grep failed: {r.stderr}"
    assert r.stdout.strip() == "1", (
        f"expected exactly 1 '## CI structure' heading, got {r.stdout.strip()}"
    )


def test_pr_conventions_section_preserved():
    """The '## PR conventions' section heading is preserved (p2p)."""
    r = subprocess.run(
        ["grep", "-c", "^## PR conventions$", str(SKILL)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"grep failed: {r.stderr}"
    assert r.stdout.strip() == "1"


def test_workflow_actually_has_no_automerge():
    """Sanity: the workflow file at base really has no automerge job (p2p).

    Confirms the premise of the task — if this fails, the task itself is wrong.
    """
    r = subprocess.run(
        ["grep", "-iE", "auto[-_ ]?merge", str(WORKFLOW)],
        capture_output=True, text=True,
    )
    # grep returns 1 when zero lines match, 0 when ≥1 match
    assert r.returncode == 1, (
        f"workflow unexpectedly contains automerge text: {r.stdout!r}"
    )


# ── fail_to_pass ────────────────────────────────────────────────────────────

def test_stale_automerge_claim_removed():
    """The stale phrase 'auto-merges single-commit' must be gone (f2p).

    The base skill says: "pull-request-target.yaml auto-merges single-commit
    `prql-bot` PRs once CI passes". The workflow doesn't do that, so the
    rewrite must remove this claim.
    """
    content = SKILL.read_text(encoding="utf-8")
    assert "auto-merges single-commit" not in content, (
        "SKILL.md still claims pull-request-target.yaml auto-merges "
        "single-commit prql-bot PRs — this assertion is stale and must "
        "be removed or rewritten"
    )


def test_automerge_status_clarified():
    """The skill must clarify the new automerge status (f2p).

    A correct rewrite communicates that automatic merging is no longer in
    effect — accepted indicators include words like 'manual', 'manually',
    'removed', 'no longer', 'not configured', 'must be merged', or
    'no automerge'.
    """
    content = SKILL.read_text(encoding="utf-8").lower()
    indicators = [
        "manual",          # also matches "manually"
        "removed",
        "no longer",
        "not configured",
        "must be merged",
        "no automerge",
    ]
    assert any(i in content for i in indicators), (
        "SKILL.md does not clarify the new merge status — expected one of "
        f"{indicators} to appear after the rewrite"
    )

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
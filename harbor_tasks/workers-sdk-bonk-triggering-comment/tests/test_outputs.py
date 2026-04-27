"""Verifies the Bonk triggering-comment fix landed in both the workflow YAML
and the agent instruction markdown."""

import subprocess
from pathlib import Path

import yaml

REPO = Path("/workspace/workers-sdk")
WORKFLOW = REPO / ".github/workflows/bonk.yml"
AGENT_MD = REPO / ".opencode/agents/bonk.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ─── Workflow (.github/workflows/bonk.yml) ────────────────────────────────────

def test_workflow_yaml_is_valid():
    """The workflow file parses as YAML after the change (subprocess gate)."""
    r = subprocess.run(
        ["python3", "-c",
         "import sys, yaml; yaml.safe_load(open(sys.argv[1]).read())",
         str(WORKFLOW)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Workflow YAML failed to parse:\n{r.stderr}"


def test_workflow_has_build_prompt_step():
    """The workflow defines a step that builds a prompt from the triggering
    comment before calling the ask-bonk action."""
    doc = yaml.safe_load(_read(WORKFLOW))
    steps = doc["jobs"]["bonk"]["steps"]
    names = [s.get("name", "") for s in steps]
    assert "Build prompt with triggering comment" in names, (
        f"Expected a step named 'Build prompt with triggering comment'; got {names}"
    )


def test_build_prompt_step_uses_comment_body():
    """The new step injects the triggering comment body via env (not via a raw
    template substitution that would risk shell injection)."""
    doc = yaml.safe_load(_read(WORKFLOW))
    steps = doc["jobs"]["bonk"]["steps"]
    target = next(
        (s for s in steps if s.get("name") == "Build prompt with triggering comment"),
        None,
    )
    assert target is not None
    env = target.get("env") or {}
    assert "COMMENT_BODY" in env, f"step env missing COMMENT_BODY: {env}"
    assert "github.event.comment.body" in env["COMMENT_BODY"], env["COMMENT_BODY"]
    run_block = target.get("run", "")
    assert "$COMMENT_BODY" in run_block, (
        "run script must reference the injected env var, not interpolate the "
        "raw expression"
    )


def test_build_prompt_step_writes_github_output():
    """The step writes its assembled prompt to $GITHUB_OUTPUT under id `prompt`."""
    doc = yaml.safe_load(_read(WORKFLOW))
    steps = doc["jobs"]["bonk"]["steps"]
    target = next(
        (s for s in steps if s.get("name") == "Build prompt with triggering comment"),
        None,
    )
    assert target is not None
    assert target.get("id") == "prompt", f"step id should be 'prompt'; got {target.get('id')!r}"
    run_block = target.get("run", "")
    assert "GITHUB_OUTPUT" in run_block, "step must write to $GITHUB_OUTPUT"


def test_run_bonk_passes_prompt_parameter():
    """The Run Bonk step passes the assembled prompt to the ask-bonk action."""
    doc = yaml.safe_load(_read(WORKFLOW))
    steps = doc["jobs"]["bonk"]["steps"]
    run_step = next((s for s in steps if s.get("name") == "Run Bonk"), None)
    assert run_step is not None, f"steps: {[s.get('name') for s in steps]}"
    with_block = run_step.get("with") or {}
    prompt = with_block.get("prompt", "")
    assert "steps.prompt.outputs" in prompt, (
        f"Run Bonk's `with.prompt` must reference the build step output; got {prompt!r}"
    )


def test_build_prompt_step_runs_before_run_bonk():
    """Ordering: the build-prompt step must precede the Run Bonk step."""
    doc = yaml.safe_load(_read(WORKFLOW))
    steps = doc["jobs"]["bonk"]["steps"]
    names = [s.get("name", "") for s in steps]
    assert names.index("Build prompt with triggering comment") < names.index("Run Bonk")


# ─── Agent instruction (.opencode/agents/bonk.md) ────────────────────────────

def test_agent_md_has_triggering_comment_rule():
    """The non-negotiable rule that the triggering comment is the primary task
    must appear in bonk.md."""
    text = _read(AGENT_MD)
    assert "Triggering comment is the task" in text, (
        "missing the 'Triggering comment is the task' non-negotiable rule"
    )


def test_agent_md_has_no_rereview_rule():
    """The non-negotiable rule that bans re-reviewing on fixup requests must
    appear in bonk.md."""
    text = _read(AGENT_MD)
    assert "No re-reviewing on fixup requests" in text, (
        "missing the 'No re-reviewing on fixup requests' non-negotiable rule"
    )


def test_triggering_comment_rule_is_inside_non_negotiable_block():
    """The new rule belongs in the <non_negotiable_rules> block, not in some
    other section."""
    text = _read(AGENT_MD)
    start = text.find("<non_negotiable_rules>")
    end = text.find("</non_negotiable_rules>")
    assert start != -1 and end != -1 and start < end, (
        "non_negotiable_rules block not found"
    )
    block = text[start:end]
    assert "Triggering comment is the task" in block, (
        "Triggering-comment rule must live inside <non_negotiable_rules>"
    )
    assert "No re-reviewing on fixup requests" in block, (
        "No-re-reviewing rule must live inside <non_negotiable_rules>"
    )


def test_implementation_workflow_starts_from_triggering_comment():
    """The implementation-mode workflow must lead with the triggering comment as
    step 1, not with reading the full issue/PR."""
    text = _read(AGENT_MD)
    start = text.find("<implementation>")
    end = text.find("</implementation>")
    assert start != -1 and end != -1 and start < end
    block = text[start:end]
    # Find the first numbered step
    import re
    m = re.search(r"^\s*1\.\s+(.+)$", block, re.MULTILINE)
    assert m is not None, "no '1.' step found in implementation block"
    step1 = m.group(1).lower()
    # Step 1 must mention the triggering comment as the starting point
    assert "triggering comment" in step1, (
        f"step 1 must start from the triggering comment; got: {m.group(1)!r}"
    )


def test_examples_section_has_plural_negative_examples():
    """The examples section must accommodate multiple negative examples (the
    fix added two new negative cases for the failure mode)."""
    text = _read(AGENT_MD)
    assert "Negative examples:" in text, (
        "Examples section heading must read 'Negative examples:' (plural) "
        "after the new cases are added"
    )


def test_negative_examples_cover_post_review_fixup():
    """The negative examples must cover the specific failure mode: a fixup
    request after a prior review that the agent then ignores by re-reviewing."""
    text = _read(AGENT_MD)
    start = text.find("<examples>")
    end = text.find("</examples>")
    assert start != -1 and end != -1 and start < end
    block = text[start:end].lower()
    # Two distinct signals: a "previously reviewed" framing AND a fixup trigger
    assert "previously reviewed" in block or "already reviewed" in block, (
        "negative examples should explicitly frame the failure as occurring "
        "after a prior review"
    )
    assert "address the review comments" in block, (
        "negative examples should include an 'address the review comments' "
        "trigger to capture the observed failure mode"
    )

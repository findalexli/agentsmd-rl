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


# --- Workflow (.github/workflows/bonk.yml) ------------------------------------

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
    expected = "Build prompt with triggering comment"
    assert expected in names, f"Expected step {expected!r}; got {names}"


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
    """The step writes its assembled prompt to $GITHUB_OUTPUT under id prompt."""
    doc = yaml.safe_load(_read(WORKFLOW))
    steps = doc["jobs"]["bonk"]["steps"]
    target = next(
        (s for s in steps if s.get("name") == "Build prompt with triggering comment"),
        None,
    )
    assert target is not None
    sid = target.get("id")
    assert sid == "prompt", "step id should be 'prompt'; got {!r}".format(sid)
    run_block = target.get("run", "")
    assert "GITHUB_OUTPUT" in run_block, "step must write to $GITHUB_OUTPUT"


def test_run_bonk_passes_prompt_parameter():
    """The Run Bonk step passes the assembled prompt to the ask-bonk action."""
    doc = yaml.safe_load(_read(WORKFLOW))
    steps = doc["jobs"]["bonk"]["steps"]
    run_step = next((s for s in steps if s.get("name") == "Run Bonk"), None)
    step_names = [s.get("name") for s in steps]
    assert run_step is not None, f"steps: {step_names}"
    with_block = run_step.get("with") or {}
    prompt = with_block.get("prompt", "")
    assert "steps.prompt.outputs" in prompt, (
        "Run Bonk with.prompt must reference the build step output; got {!r}".format(prompt)
    )


def test_build_prompt_step_runs_before_run_bonk():
    """Ordering: the build-prompt step must precede the Run Bonk step."""
    doc = yaml.safe_load(_read(WORKFLOW))
    steps = doc["jobs"]["bonk"]["steps"]
    names = [s.get("name", "") for s in steps]
    assert names.index("Build prompt with triggering comment") < names.index("Run Bonk")


# --- Agent instruction (.opencode/agents/bonk.md) ----------------------------

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
    import re
    m = re.search(r"^\s*1\.\s+(.+)$", block, re.MULTILINE)
    assert m is not None, "no '1.' step found in implementation block"
    step1 = m.group(1).lower()
    assert "triggering comment" in step1, (
        "step 1 must start from the triggering comment; got: {!r}".format(m.group(1))
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
    assert "previously reviewed" in block or "already reviewed" in block, (
        "negative examples should explicitly frame the failure as occurring "
        "after a prior review"
    )
    assert "address the review comments" in block, (
        "negative examples should include an 'address the review comments' "
        "trigger to capture the observed failure mode"
    )


# === pass_to_pass regression guards ===

def test_run_bonk_step_preserved_after_edit():
    """The Run Bonk step must still exist and reference the ask-bonk action
    (the action referenced in the Background section) after the edit."""
    doc = yaml.safe_load(_read(WORKFLOW))
    steps = doc["jobs"]["bonk"]["steps"]
    run_step = next((s for s in steps if s.get("name") == "Run Bonk"), None)
    assert run_step is not None, "Run Bonk step must still be present after the edit"
    uses = run_step.get("uses", "")
    assert "ask-bonk" in uses, (
        "Run Bonk step must still reference the ask-bonk action; got {!r}".format(uses)
    )


def test_non_negotiable_rules_block_structure_intact():
    """The non-negotiable rules block must remain well-formed after the edit,
    with the existing rule count preserved alongside the two new rules."""
    text = _read(AGENT_MD)
    start = text.find("<non_negotiable_rules>")
    end = text.find("</non_negotiable_rules>")
    assert start != -1 and end != -1 and start < end
    block = text[start:end]
    # Count bold rule labels (lines matching "- **Label:**")
    rule_count = sum(1 for line in block.split("\n")
                     if line.strip().startswith("- **"))
    assert rule_count >= 5, (
        "Expected at least 5 bold rule labels inside <non_negotiable_rules> "
        "(existing rules must survive the edit); found {}".format(rule_count)
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_build():
    """pass_to_pass | CI job 'build' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build --filter="./packages/*"'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_upload_packages():
    """pass_to_pass | CI job 'build' → step 'Upload packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'node -r esbuild-register .github/prereleases/upload.mjs'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Upload packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cleanup_test_projects_cleanup_e2e_test_projects():
    """pass_to_pass | CI job 'Cleanup Test Projects' → step 'Cleanup E2E test projects'"""
    r = subprocess.run(
        ["bash", "-lc", 'node -r esbuild-register tools/e2e/e2eCleanup.ts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Cleanup E2E test projects' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
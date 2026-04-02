"""
Task: sglang-rerun-ut-duplicate-urls
Repo: sgl-project/sglang @ c580ddd19d613862b8720e307442946d0b9c41e2
PR:   #21495

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import io
import re
import sys
import time
from pathlib import Path
from unittest import mock

import yaml

REPO = "/repo"
HANDLER_PATH = "scripts/ci/utils/slash_command_handler.py"
WORKFLOW_PATH = ".github/workflows/rerun-ut.yml"


def _capture_title(test_command=None, pr_head_sha=None, target_stage="rerun-ut"):
    """Call find_workflow_run_url with mocked HTTP, return the expected_title from stdout."""
    mock_resp = mock.MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"workflow_runs": []}

    mock_repo = mock.MagicMock()
    mock_repo.full_name = "test/repo"

    from scripts.ci.utils.slash_command_handler import find_workflow_run_url

    kwargs = dict(
        gh_repo=mock_repo,
        workflow_id=123,
        branch="main",
        target_stage=target_stage,
        token="tok",
        dispatch_time=time.time(),
        max_wait=5,
    )
    if pr_head_sha is not None:
        kwargs["pr_head_sha"] = pr_head_sha
    if test_command is not None:
        kwargs["test_command"] = test_command

    with mock.patch("requests.get", return_value=mock_resp), mock.patch("time.sleep"):
        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            find_workflow_run_url(**kwargs)
        finally:
            sys.stdout = old_stdout
    return captured.getvalue()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_handler_syntax():
    """slash_command_handler.py must parse without syntax errors."""
    import py_compile

    py_compile.compile(f"{REPO}/{HANDLER_PATH}", doraise=True)


# [static] pass_to_pass
def test_workflow_yaml_syntax():
    """rerun-ut.yml must be valid YAML."""
    with open(f"{REPO}/{WORKFLOW_PATH}") as f:
        data = yaml.safe_load(f)
    assert data is not None, "YAML file is empty or invalid"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_title_includes_test_command():
    """find_workflow_run_url builds title containing test_command when provided."""
    for cmd in ["test_foo.py", "test_srt_engine.py", "test_openai_server.py"]:
        output = _capture_title(test_command=cmd)
        assert cmd in output, f"Expected '{cmd}' in printed title: {output}"
        assert "[rerun-ut]" in output, f"Expected '[rerun-ut]' in output: {output}"


# [pr_diff] fail_to_pass
def test_different_commands_unique_titles():
    """Different test_commands produce different expected titles."""
    commands = ["test_foo.py", "test_bar.py", "test_baz.py"]
    titles = [_capture_title(test_command=cmd) for cmd in commands]
    for i, cmd in enumerate(commands):
        assert cmd in titles[i], f"Expected '{cmd}' in title: {titles[i]}"
    assert len(set(titles)) == len(titles), "Some test_commands produced identical titles"


# [pr_diff] fail_to_pass
def test_title_with_sha_and_command():
    """Title includes both test_command and pr_head_sha for fork PRs."""
    cases = [
        ("test_baz.py", "abc123def"),
        ("test_openai_server.py", "deadbeef42"),
        ("test_srt_engine.py", "f00dcafe99"),
    ]
    for cmd, sha in cases:
        output = _capture_title(test_command=cmd, pr_head_sha=sha)
        assert cmd in output, f"Missing test_command '{cmd}' in title: {output}"
        assert sha in output, f"Missing sha '{sha}' in title: {output}"
        assert "[rerun-ut]" in output, f"Missing stage tag in title: {output}"


# [pr_diff] fail_to_pass
def test_yaml_run_name_includes_test_command():
    """rerun-ut.yml run-name template references test_command input."""
    with open(f"{REPO}/{WORKFLOW_PATH}") as f:
        data = yaml.safe_load(f)
    run_name = data.get("run-name", "")
    assert "test_command" in run_name, (
        f"run-name does not reference test_command: {run_name}"
    )


# [pr_diff] fail_to_pass
def test_rerun_ut_no_pre_find_trigger_comment():
    """handle_rerun_ut must not post a standalone trigger comment before find_workflow_run_url.

    On base commit, there is a create_issue_comment('Triggered ...') call before
    find_workflow_run_url. The fix removes it and consolidates into a single comment after.
    """
    # Source inspection because: handle_rerun_ut orchestrates GitHub API calls
    # (workflow dispatch, polling, comment posting) that require extensive mocking
    # of PyGithub objects and HTTP calls — behavioral testing is impractical
    src = Path(f"{REPO}/{HANDLER_PATH}").read_text()
    lines = src.split("\n")

    # Anti-stub: function must call find_workflow_run_url and create_issue_comment
    func_body = []
    in_func = False
    for line in lines:
        if "def handle_rerun_ut" in line:
            in_func = True
            continue
        if in_func and line.strip().startswith("def ") and "handle_rerun_ut" not in line:
            break
        if in_func:
            func_body.append(line)
    body_text = "\n".join(func_body)
    assert "find_workflow_run_url" in body_text, (
        "handle_rerun_ut is missing find_workflow_run_url call (stub?)"
    )
    assert "create_issue_comment" in body_text, (
        "handle_rerun_ut is missing create_issue_comment call (stub?)"
    )

    # Core check: no create_issue_comment between "if success:" and find_workflow_run_url
    in_success = False
    found_pre_trigger = False
    for line in func_body:
        if "if success:" in line:
            in_success = True
            continue
        if in_success:
            if "find_workflow_run_url" in line:
                break
            if "create_issue_comment" in line:
                found_pre_trigger = True

    assert not found_pre_trigger, (
        "handle_rerun_ut still posts a standalone trigger comment before find_workflow_run_url"
    )


# [pr_diff] fail_to_pass
def test_rerun_stage_no_separate_link_comment():
    """handle_rerun_stage must not post a standalone comment before find_workflow_run_url.

    On base commit, there is a create_issue_comment call between create_reaction("+1")
    and find_workflow_run_url. The fix removes it and consolidates into one comment after.
    """
    # Source inspection because: handle_rerun_stage orchestrates GitHub API calls
    # (workflow dispatch, polling, comment posting) that require extensive mocking
    # of PyGithub objects and HTTP calls — behavioral testing is impractical
    src = Path(f"{REPO}/{HANDLER_PATH}").read_text()
    match = re.search(r"def handle_rerun_stage\b.*?(?=\ndef \w|\Z)", src, re.DOTALL)
    assert match, "handle_rerun_stage function not found"
    body = match.group(0)

    # Anti-stub: function must call find_workflow_run_url and create_issue_comment
    assert "find_workflow_run_url" in body, (
        "handle_rerun_stage is missing find_workflow_run_url call (stub?)"
    )
    assert "create_issue_comment" in body, (
        "handle_rerun_stage is missing create_issue_comment call (stub?)"
    )

    # Core check: no create_issue_comment between create_reaction("+1") and find_workflow_run_url
    lines = body.split("\n")
    past_reaction = False
    found_pre_comment = False

    for line in lines:
        stripped = line.strip()
        if 'create_reaction("+1")' in stripped or "create_reaction('+1')" in stripped:
            past_reaction = True
            continue
        if past_reaction:
            if "find_workflow_run_url" in stripped:
                break
            if "create_issue_comment" in stripped:
                found_pre_comment = True

    assert not found_pre_comment, (
        "handle_rerun_stage still posts a standalone comment before find_workflow_run_url"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_title_without_command_backward_compat():
    """find_workflow_run_url without test_command still produces correct titles."""
    # With sha
    output = _capture_title(target_stage="stage-b", pr_head_sha="sha456")
    assert "[stage-b] sha456" in output, (
        f"Expected '[stage-b] sha456' in output: {output}"
    )
    # Without sha
    output = _capture_title(target_stage="rerun-stage")
    assert "[rerun-stage]" in output, (
        f"Expected '[rerun-stage]' in output: {output}"
    )
    # Different stage + sha
    output = _capture_title(target_stage="stage-a", pr_head_sha="deadbeef")
    assert "[stage-a] deadbeef" in output, (
        f"Expected '[stage-a] deadbeef' in output: {output}"
    )


# ---------------------------------------------------------------------------
# Anti-stub (static) — ensure handler wasn't gutted
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_handler_exports_public_api():
    """Handler module exports find_workflow_run_url, handle_rerun_ut, handle_rerun_stage."""
    from scripts.ci.utils import slash_command_handler as m

    for name in ("find_workflow_run_url", "handle_rerun_ut", "handle_rerun_stage"):
        assert hasattr(m, name), f"Handler missing public function: {name}"

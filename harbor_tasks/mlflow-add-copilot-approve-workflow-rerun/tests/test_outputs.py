"""
Task: mlflow-add-copilot-approve-workflow-rerun
Repo: mlflow/mlflow @ 39f35acce9e63788371bfaaa2c57cafef10a02ec
PR:   22330

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/mlflow"
APPROVE_SH = Path(REPO) / ".claude" / "skills" / "copilot" / "approve.sh"
SKILL_MD = Path(REPO) / ".claude" / "skills" / "copilot" / "SKILL.md"

# Mock gh CLI template.  Placeholders __DATA_FILE__ / __POST_LOG__ are
# replaced at runtime.  The mock handles three call patterns:
#   gh pr view ...          -> returns a deterministic HEAD SHA
#   gh api <url> --jq ...   -> applies the jq filter to the test JSON
#   gh api --method POST .. -> logs the URL and returns {}
_MOCK_GH = r"""#!/usr/bin/env bash
DATA_FILE="__DATA_FILE__"
POST_LOG="__POST_LOG__"

# --- gh pr view ---
if [[ "$1" == "pr" && "$2" == "view" ]]; then
    has_jq=0
    for arg in "$@"; do
        [[ "$arg" == "--jq" || "$arg" == --jq=* ]] && has_jq=1
    done
    if [[ "$has_jq" == "1" ]]; then
        echo "fake_sha_abc123"
    else
        echo '{"headRefOid":"fake_sha_abc123"}'
    fi
    exit 0
fi

# --- gh api ---
if [[ "$1" == "api" ]]; then
    method=""
    url=""
    jq_filter=""
    shift
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --method)   shift; method="$1" ;;
            --method=*) method="${1#--method=}" ;;
            --jq)       shift; jq_filter="$1" ;;
            --jq=*)     jq_filter="${1#--jq=}" ;;
            --input|--template|--hostname|--header|-H) shift ;;
            --paginate|--silent|-q) ;;
            -*) ;;
            *)  [[ -z "$url" ]] && url="$1" ;;
        esac
        shift
    done

    if [[ "$method" == "POST" || "$method" == "post" ]]; then
        echo "$url" >> "$POST_LOG"
        echo '{}'
        exit 0
    fi

    # GET - route by URL pattern
    if [[ "$url" == *"/pulls/"* || "$url" == *"/pulls?"* || "$url" == *"/pulls" ]]; then
        pr_json='{"head":{"sha":"fake_sha_abc123"},"headRefOid":"fake_sha_abc123"}'
        if [[ -n "$jq_filter" ]] && command -v jq &>/dev/null; then
            echo "$pr_json" | jq -r "$jq_filter"
        else
            echo "$pr_json"
        fi
    else
        if [[ -n "$jq_filter" ]] && command -v jq &>/dev/null; then
            jq -r "$jq_filter" < "$DATA_FILE"
        else
            cat "$DATA_FILE"
        fi
    fi
    exit 0
fi

exit 0
"""


def _mock_gh(tmpdir, runs_data):
    """Create a mock gh binary and its data file.  Return (mock_path, post_log)."""
    data_file = os.path.join(tmpdir, "data.json")
    post_log = os.path.join(tmpdir, "posts.log")
    mock = os.path.join(tmpdir, "gh")
    with open(data_file, "w") as f:
        json.dump(runs_data, f)
    script = _MOCK_GH.replace("__DATA_FILE__", data_file).replace("__POST_LOG__", post_log)
    with open(mock, "w") as f:
        f.write(script)
    os.chmod(mock, 0o755)
    return mock, post_log


def _run_approve(mock_path, repo_arg="test-owner/test-repo", pr_arg="42"):
    """Execute approve.sh with the mock gh first on PATH."""
    env = os.environ.copy()
    env["PATH"] = os.path.dirname(mock_path) + ":" + env.get("PATH", "")
    return subprocess.run(
        ["bash", str(APPROVE_SH), repo_arg, pr_arg],
        capture_output=True, text=True, timeout=30, env=env,
    )


def _posts(log_path):
    """Read the POST-call log written by the mock."""
    if os.path.exists(log_path):
        return [l for l in Path(log_path).read_text().strip().splitlines() if l]
    return []


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_approve_sh_syntax():
    """approve.sh must exist and have valid bash syntax."""
    assert APPROVE_SH.exists(), f"{APPROVE_SH} does not exist"
    r = subprocess.run(
        ["bash", "-n", str(APPROVE_SH)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Syntax error in approve.sh:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_approve_sh_exits_on_missing_args():
    """approve.sh must fail when called without required arguments."""
    assert APPROVE_SH.exists(), f"{APPROVE_SH} does not exist"
    r = subprocess.run(
        ["bash", str(APPROVE_SH)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode != 0, (
        "approve.sh should exit nonzero when called without arguments"
    )


# [pr_diff] fail_to_pass
def test_approve_sh_rerun_not_approve_api():
    """Script must call /rerun, not /approve, to re-trigger workflows."""
    assert APPROVE_SH.exists(), f"{APPROVE_SH} does not exist"
    runs = {"workflow_runs": [
        {"id": 99001, "conclusion": "action_required",
         "actor": {"login": "Copilot"}},
    ]}
    with tempfile.TemporaryDirectory() as td:
        mock, log = _mock_gh(td, runs)
        _run_approve(mock)
        posts = _posts(log)
        rerun = [p for p in posts if "/rerun" in p]
        approve = [p for p in posts if "/approve" in p]
        assert rerun, (
            f"approve.sh must call the /rerun API endpoint; POST calls: {posts}"
        )
        assert not approve, (
            f"approve.sh must NOT call /approve API; found: {approve}"
        )


# [pr_diff] fail_to_pass
def test_approve_sh_filters_copilot_action_required():
    """Script must only rerun action_required runs triggered by Copilot."""
    assert APPROVE_SH.exists(), f"{APPROVE_SH} does not exist"
    runs = {"workflow_runs": [
        {"id": 11111, "conclusion": "action_required",
         "actor": {"login": "Copilot"}},
        {"id": 22222, "conclusion": "action_required",
         "actor": {"login": "other-user"}},
        {"id": 33333, "conclusion": "success",
         "actor": {"login": "Copilot"}},
    ]}
    with tempfile.TemporaryDirectory() as td:
        mock, log = _mock_gh(td, runs)
        _run_approve(mock)
        posts = _posts(log)
        assert any("11111" in p for p in posts), (
            f"Should rerun action_required+Copilot run 11111; posts: {posts}"
        )
        assert not any("22222" in p for p in posts), (
            f"Should NOT rerun non-Copilot run 22222; posts: {posts}"
        )
        assert not any("33333" in p for p in posts), (
            f"Should NOT rerun non-action_required run 33333; posts: {posts}"
        )


# [pr_diff] fail_to_pass
def test_approve_sh_handles_empty_results():
    """Script must exit 0 and make no API calls when no runs match."""
    assert APPROVE_SH.exists(), f"{APPROVE_SH} does not exist"
    runs = {"workflow_runs": [
        {"id": 44444, "conclusion": "success",
         "actor": {"login": "other-user"}},
    ]}
    with tempfile.TemporaryDirectory() as td:
        mock, log = _mock_gh(td, runs)
        result = _run_approve(mock)
        assert result.returncode == 0, (
            f"Should exit 0 when no runs match; got {result.returncode}\n"
            f"stderr: {result.stderr}"
        )
        assert not _posts(log), (
            f"Should not call rerun when no runs match; posts: {_posts(log)}"
        )


# ---------------------------------------------------------------------------
# Config/documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_md_approve_in_allowed_tools():
    """SKILL.md must list approve.sh in allowed-tools frontmatter."""
    content = SKILL_MD.read_text()
    assert "approve.sh" in content, "SKILL.md should reference approve.sh"
    in_frontmatter = False
    in_allowed_tools = False
    found = False
    for line in content.splitlines():
        if line.strip() == "---":
            if in_frontmatter:
                break
            in_frontmatter = True
            continue
        if in_frontmatter and "allowed-tools" in line:
            in_allowed_tools = True
        if in_allowed_tools and "approve.sh" in line:
            found = True
            break
    assert found, (
        "approve.sh must be listed in the allowed-tools section of SKILL.md frontmatter"
    )


# [pr_diff] fail_to_pass
def test_skill_md_documents_approve_workflow():
    """SKILL.md must document how to use the approve workflow script."""
    content = SKILL_MD.read_text()
    content_lower = content.lower()
    assert "approv" in content_lower, "SKILL.md should document workflow approval"
    assert "approve.sh" in content, "SKILL.md should show the approve.sh command"
    has_repo_param = (
        "<owner>" in content or "owner/repo" in content.lower() or "repo" in content
    )
    has_pr_param = "pr_number" in content or "pr number" in content.lower()
    assert has_repo_param and has_pr_param, (
        "SKILL.md should document both repo and PR number parameters for approve.sh"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) -- CI checks that must pass on base and gold
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_bash_syntax_copilot():
    """All shell scripts in .claude/skills/copilot have valid bash syntax (pass_to_pass)."""
    skill_dir = Path(REPO) / ".claude" / "skills" / "copilot"
    for script in skill_dir.glob("*.sh"):
        r = subprocess.run(
            ["bash", "-n", str(script)],
            capture_output=True, text=True, timeout=10,
        )
        assert r.returncode == 0, f"Syntax error in {script}:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_claude():
    """Ruff linting passes on .claude directory (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "pip", "install", "ruff==0.15.5", "-q"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        ["ruff", "check", ".claude/", "--output-format=concise"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_bash_syntax_all_claude():
    """All shell scripts in .claude have valid bash syntax (pass_to_pass)."""
    claude_dir = Path(REPO) / ".claude"
    for script in claude_dir.rglob("*.sh"):
        r = subprocess.run(
            ["bash", "-n", str(script)],
            capture_output=True, text=True, timeout=10,
        )
        assert r.returncode == 0, f"Syntax error in {script}:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format_claude():
    """Ruff format check passes on .claude directory (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "pip", "install", "ruff==0.15.5", "-q"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        ["ruff", "format", f"{REPO}/.claude/", "--check"],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_mlflow_typo_claude():
    """No MLflow typos in .claude directory (pass_to_pass)."""
    claude_dir = Path(REPO) / ".claude"
    files_to_check = list(claude_dir.rglob("*"))
    if files_to_check:
        r = subprocess.run(
            ["bash", f"{REPO}/dev/mlflow-typo.sh"]
            + [str(f) for f in files_to_check if f.is_file()],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, (
            f"MLflow typo check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"
        )


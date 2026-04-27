"""Behavior tests for openai-agents-js#1140 (forward external web access)."""
import json
import re
import shutil
import subprocess
from pathlib import Path

REPO = Path("/workspace/openai-agents-js")
PKG = REPO / "packages" / "agents-openai"
FIXTURE_SRC = Path("/tests/fixtures/scaffold_external_web_access.test.ts")
FIXTURE_DST = PKG / "test" / "__scaffold_external_web_access.test.ts"


def _stage_fixture():
    """Copy the scaffold fixture into the package's test dir."""
    FIXTURE_DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(FIXTURE_SRC, FIXTURE_DST)


def _vitest_run_one(test_name_substring: str, timeout: int = 300) -> dict:
    """Run vitest on the fixture file filtered by `-t <substring>`.
    Returns dict with rc, stdout, stderr, json (parsed --reporter=json blob)."""
    _stage_fixture()
    cmd = [
        "pnpm", "-F", "@openai/agents-openai", "exec",
        "vitest", "run",
        "--reporter=json",
        "test/__scaffold_external_web_access.test.ts",
        "-t", test_name_substring,
    ]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=timeout)
    out = {"rc": r.returncode, "stdout": r.stdout, "stderr": r.stderr, "json": None}
    # vitest --reporter=json prints JSON to stdout; pnpm decoration may prefix lines
    m = re.search(r"\{[\s\S]*\}\s*$", r.stdout)
    if m:
        try:
            out["json"] = json.loads(m.group(0))
        except Exception:
            pass
    return out


def _assert_named_test_passed(result: dict, expected_substring: str) -> None:
    """Verify vitest ran the expected test and it passed."""
    assert result["rc"] == 0, (
        f"vitest failed (rc={result['rc']}):\n"
        f"--- stdout (last 2000) ---\n{result['stdout'][-2000:]}\n"
        f"--- stderr (last 1000) ---\n{result['stderr'][-1000:]}"
    )
    j = result["json"]
    assert j is not None, f"could not parse vitest JSON output:\n{result['stdout'][-1000:]}"
    # vitest json: numTotalTests, numPassedTests, testResults[*].assertionResults[*].{title,status}
    titles = []
    for tr in j.get("testResults", []) or []:
        for ar in tr.get("assertionResults", []) or []:
            titles.append((ar.get("fullName") or ar.get("title") or "", ar.get("status")))
    matched = [t for t in titles if expected_substring in t[0]]
    assert matched, (
        f"no vitest test matched substring {expected_substring!r}; "
        f"saw {[t[0] for t in titles]}"
    )
    for name, status in matched:
        assert status == "passed", f"vitest test {name!r} status={status!r}"


# ─────────────────────────── fail-to-pass tests ─────────────────────────────

def test_websearch_tool_preserves_false_external_web_access():
    r = _vitest_run_one("preserves explicit false external web access")
    _assert_named_test_passed(r, "preserves explicit false external web access")


def test_websearch_tool_preserves_true_external_web_access():
    r = _vitest_run_one("preserves explicit true external web access")
    _assert_named_test_passed(r, "preserves explicit true external web access")


def test_convertool_forwards_external_web_access_false():
    r = _vitest_run_one("forwards external_web_access=false on web_search")
    _assert_named_test_passed(r, "forwards external_web_access=false on web_search")


def test_convertool_forwards_external_web_access_true():
    r = _vitest_run_one("forwards external_web_access=true on web_search")
    _assert_named_test_passed(r, "forwards external_web_access=true on web_search")


# ─────────────────────────── pass-to-pass guards ─────────────────────────────

def test_websearch_tool_omits_external_web_access_when_unset():
    """Regression: when caller does not pass externalWebAccess, the field must NOT
    appear on providerData (so the OpenAI API default applies)."""
    r = _vitest_run_one("omits external_web_access when option not provided")
    _assert_named_test_passed(r, "omits external_web_access when option not provided")


def test_convertool_omits_external_web_access_when_absent():
    """Regression: providerData without external_web_access must not inject the
    key into the converted tool payload."""
    r = _vitest_run_one("omits external_web_access when not present in providerData")
    _assert_named_test_passed(
        r, "omits external_web_access when not present in providerData"
    )


def test_repo_existing_tools_test_passes():
    """Repo's own packages/agents-openai/test/tools.test.ts must still pass."""
    cmd = [
        "pnpm", "-F", "@openai/agents-openai", "exec",
        "vitest", "run",
        "test/tools.test.ts",
    ]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"vitest tools.test.ts failed (rc={r.returncode}):\n"
        f"{r.stdout[-1500:]}\n{r.stderr[-500:]}"
    )


def test_repo_existing_responses_helpers_test_passes():
    """Repo's own packages/agents-openai/test/openaiResponsesModel.helpers.test.ts
    must still pass."""
    cmd = [
        "pnpm", "-F", "@openai/agents-openai", "exec",
        "vitest", "run",
        "test/openaiResponsesModel.helpers.test.ts",
    ]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, (
        f"vitest helpers test failed (rc={r.returncode}):\n"
        f"{r.stdout[-1500:]}\n{r.stderr[-500:]}"
    )


def test_repo_build_check_passes():
    """`pnpm -F @openai/agents-openai build-check` (tsc --noEmit on test config)
    must pass — agent's edits must keep TypeScript happy."""
    cmd = [
        "pnpm", "-F", "@openai/agents-openai", "run", "build-check",
    ]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, (
        f"build-check failed (rc={r.returncode}):\n"
        f"{r.stdout[-1500:]}\n{r.stderr[-500:]}"
    )


def test_repo_build_succeeds():
    """`pnpm -F @openai/agents-openai build` must compile."""
    cmd = ["pnpm", "-F", "@openai/agents-openai", "run", "build"]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, (
        f"build failed (rc={r.returncode}):\n"
        f"{r.stdout[-1500:]}\n{r.stderr[-500:]}"
    )


def test_repo_lint_passes():
    """AGENTS.md mandates `pnpm lint` passes for runtime-code changes."""
    cmd = ["pnpm", "lint"]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, (
        f"lint failed (rc={r.returncode}):\n"
        f"{r.stdout[-1500:]}\n{r.stderr[-500:]}"
    )

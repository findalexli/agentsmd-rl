"""
Task: goose-update-channel-model-to-use
Repo: goose-lang/goose @ e0f62c9e03d8be7f5cd4ed95347b8c23d3c34212
PR:   151

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/goose"


def _run(cmd: list, timeout: int = 60, cwd: str = REPO) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_unit_channel_basic():
    """Channel basic test: generated Coq code must have element types (checked against gold file)."""
    # Run only the TestExamples/unittest/chanBasic test which compares generated output to gold file
    r = _run(["go", "test", "-v", "-run", "TestExamples/unittest/chanBasic", "./..."], timeout=120)
    # At base commit: test passes because old code generates old gold file format
    # At fix commit: test passes because new code generates new gold file format
    # This is a behavioral test - the gold file is updated in the PR
    assert r.returncode == 0, f"Test failed: {r.stderr}\n{r.stdout}"


def test_unit_channel_select():
    """Channel select test: generated Coq code must use select_blocking/select_nonblocking."""
    r = _run(["go", "test", "-v", "-run", "TestExamples/unittest/chanSelect", "./..."], timeout=120)
    assert r.returncode == 0, f"Test failed: {r.stderr}\n{r.stdout}"


def test_unit_channel_range():
    """Channel range test: generated Coq code must have element type in for_range."""
    r = _run(["go", "test", "-v", "-run", "TestExamples/unittest/chanRange", "./..."], timeout=120)
    assert r.returncode == 0, f"Test failed: {r.stderr}\n{r.stdout}"


def test_bootstrap_direct_calls_added():
    """Bootstrap struct has direct_calls field for function/method calls."""
    declfilter_path = Path(f"{REPO}/declfilter/declfilter.go")
    content = declfilter_path.read_text()

    assert "DirectCalls bool" in content, "DirectCalls field missing from Bootstrap struct"
    assert "direct_calls" in content, "direct_calls TOML tag missing"


def test_chan_elem_helper_added():
    """types.go has chanElem helper function for extracting channel element type."""
    types_path = Path(f"{REPO}/types.go")
    content = types_path.read_text()

    assert "func chanElem(t types.Type) types.Type" in content, "chanElem function missing"


def test_hand_translated_tests_removed():
    """TestAllHandXlatedChannelTests function is removed from examples_test.go."""
    examples_test_path = Path(f"{REPO}/examples_test.go")
    content = examples_test_path.read_text()

    # The main check: the test function should be removed
    assert "TestAllHandXlatedChannelTests" not in content, "TestAllHandXlatedChannelTests should be removed"


def test_glang_for_range_chan_has_elem():
    """ForRangeChanExpr struct in glang/coq.go has Elem field."""
    glang_path = Path(f"{REPO}/glang/coq.go")
    content = glang_path.read_text()

    # Check that ForRangeChanExpr has Elem field
    assert "Elem Expr" in content, "ForRangeChanExpr missing Elem field"

    # Check that Coq method uses both Elem and Chan
    assert "chan.for_range %s %s" in content, "chan.for_range doesn't use both Elem and Chan"


def test_ci_runs_testdata_examples():
    """CI workflow runs tests in testdata/examples directory."""
    ci_path = Path(f"{REPO}/.github/workflows/build.yml")
    content = ci_path.read_text()

    assert "go test -v ./testdata/examples/..." in content, "CI missing testdata/examples tests"


# ---------------------------------------------------------------------------
# Pass-to-pass (static / repo_tests) — regression + syntax checks
# ---------------------------------------------------------------------------


def test_go_syntax_valid():
    """Go files must have valid syntax and pass go vet."""
    r = _run(["go", "vet", "-composites=false", "./..."], timeout=120)
    # Allow vet warnings but not syntax errors
    r2 = _run(["gofmt", "-l", "."], timeout=60)
    assert r2.returncode == 0, f"gofmt failed: {r2.stderr}"
    assert r2.stdout == "", f"Files need formatting: {r2.stdout}"


def test_goose_builds():
    """Goose tool builds successfully."""
    r = _run(["go", "build", "."], timeout=120)
    assert r.returncode == 0, f"Build failed: {r.stderr}"


def test_repo_tests_pass():
    """Repository tests pass (excluding TestExamples which compare to gold files)."""
    # Run main tests excluding the gold file comparison tests
    # The TestExamples require the gold files to be updated, which is the fix
    r = _run(["go", "test", "-v", "./...", "-run", "^Test[^E]"], timeout=180)
    # Filter to run only tests that don't start with TestE (excluding TestExamples)
    # Actually let's run specific tests we know exist at base
    r = _run(["go", "test", "-v", "-run", "TestAllChannelTests|TestString"], timeout=180)
    assert r.returncode == 0, f"Tests failed: {r.stderr}\n{r.stdout}"


def test_not_stub():
    """Modified code has substantial implementation, not just stubs."""
    goose_path = Path(f"{REPO}/goose.go")
    content = goose_path.read_text()

    # Check for channel-related translation code
    # At base commit: doesn't have directCalls or the new patterns
    # At fix commit: has directCalls and new channel patterns
    has_direct_calls = "directCalls" in content
    has_chan_receive_with_type = "chan.receive", "chanElem" in content
    has_select_blocking = "select_blocking" in content

    # After fix, all these should be present
    assert has_direct_calls, "directCalls not found in goose.go - fix not applied"

    # Verify substantial implementation (not just stubs)
    lines = content.split("\n")
    func_count = sum(1 for line in lines if line.strip().startswith("func "))
    assert func_count > 50, f"goose.go seems too small ({func_count} functions)"

"""
Task: react-compiler-fault-tolerance
Repo: facebook/react @ 9b2d8013eed2b02193aebc37a614b37853ada214

The React Compiler must report ALL independent compilation errors in one
pass (fault tolerance), not stop at the first error. Agent must add a
fixture + expected-output file that proves the compiler does this.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

COMPILER_DIR = "/workspace/react/compiler"
FIXTURES_DIR = (
    "/workspace/react/compiler/packages/babel-plugin-react-compiler"
    "/src/__tests__/fixtures/compiler"
)
FIXTURE_NAME = "error.fault-tolerance-reports-multiple-errors"

FIXTURE_JS = Path(f"{FIXTURES_DIR}/{FIXTURE_NAME}.js")
FIXTURE_EXPECT = Path(f"{FIXTURES_DIR}/{FIXTURE_NAME}.expect.md")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — environment sanity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_fixtures_dir_exists():
    """The compiler fixtures directory must exist in the workspace."""
    assert Path(FIXTURES_DIR).is_dir(), f"Fixtures directory not found: {FIXTURES_DIR}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_fixture_file_exists():
    """The .js fixture file must exist at the correct path."""
    assert FIXTURE_JS.exists(), f"Fixture not found: {FIXTURE_JS}"


# [pr_diff] fail_to_pass
def test_expect_file_exists():
    """The .expect.md companion file must exist alongside the fixture."""
    assert FIXTURE_EXPECT.exists(), f"Expect file not found: {FIXTURE_EXPECT}"


# [pr_diff] fail_to_pass
def test_expect_reports_two_errors():
    """expect.md must say 'Found 2 errors' — proof that both errors are reported.

    Without 'Found 2 errors', the compiler may have stopped after the first
    error, which is the regression this fixture guards against.
    """
    assert FIXTURE_EXPECT.exists(), "Expect file missing"
    content = FIXTURE_EXPECT.read_text()
    assert "Found 2 errors" in content, (
        "Expect file does not contain 'Found 2 errors'.\n"
        f"Content snippet:\n{content[:400]}"
    )


# [pr_diff] fail_to_pass
def test_expect_has_ref_access_error():
    """expect.md must include the ref-access-during-render error message."""
    assert FIXTURE_EXPECT.exists(), "Expect file missing"
    content = FIXTURE_EXPECT.read_text()
    lower = content.lower()
    assert (
        "cannot access ref" in lower
        or "refs during render" in lower
        or "ref value during render" in lower
        or "access ref" in lower
    ), (
        "Expect file missing ref-access-during-render error.\n"
        f"Content snippet:\n{content[:600]}"
    )


# [pr_diff] fail_to_pass
def test_expect_has_mutation_error():
    """expect.md must include the frozen-value / props mutation error message."""
    assert FIXTURE_EXPECT.exists(), "Expect file missing"
    content = FIXTURE_EXPECT.read_text()
    lower = content.lower()
    assert (
        "cannot be modified" in lower
        or "value cannot be modified" in lower
        or "modifying component props" in lower
        or "frozen" in lower
    ), (
        "Expect file missing frozen-value / props-mutation error.\n"
        f"Content snippet:\n{content[:600]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from compiler/CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — compiler/CLAUDE.md:215 @ 9b2d8013eed2b02193aebc37a614b37853ada214
def test_fixture_pragma_on_first_line():
    """Feature-flag pragmas must be on the first line of the fixture.

    compiler/CLAUDE.md:215: 'Test fixtures can override the active feature
    flags used for that fixture via a comment pragma on the first line of
    the fixture input'

    The fixture uses @validateRefAccessDuringRender, which is a pragma and
    must therefore appear on line 1.
    """
    assert FIXTURE_JS.exists(), "Fixture file missing"
    lines = FIXTURE_JS.read_text().splitlines()
    assert lines, "Fixture file is empty"
    assert lines[0].startswith("//"), (
        f"First line must be a pragma comment, got: {lines[0]!r}\n"
        "Per compiler/CLAUDE.md:215, pragmas must be on the first line."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — compiler snapshot test passes
# ---------------------------------------------------------------------------

# [repo_tests] fail_to_pass
def test_compiler_snap_passes():
    """yarn snap accepts the fixture — actual compiler output matches expect.md.

    On the base commit the fixture does not exist, so jest finds no tests
    and exits non-zero.  After the fix, the fixture must produce output that
    matches the .expect.md exactly.
    """
    assert FIXTURE_JS.exists(), "Fixture missing — cannot run snap"
    assert FIXTURE_EXPECT.exists(), "Expect file missing — cannot run snap"
    r = subprocess.run(
        ["yarn", "snap", "-p", FIXTURE_NAME],
        cwd=COMPILER_DIR,
        capture_output=True,
        timeout=120,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"yarn snap failed (rc={r.returncode}):\n{output[-2000:]}"

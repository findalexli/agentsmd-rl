"""Behavioral checks for vitess versioned-comment tokenizer changes.

Each test compiles and runs vitess sqlparser code via `go test`. The Go test
files (ast_funcs_test.go, comments_test.go, token_test.go, parse_test.go)
are part of the repository checkout, so we inject Go test snippets and run
the full suite to discriminate base vs gold behavior.

We also add a few targeted Go tests as ad-hoc files that we copy in at test
time. They live under tests/_inject/ on the host and are written into the
go/vt/sqlparser/ directory before each `go test` invocation.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/vitess")
SQLPARSER = REPO / "go" / "vt" / "sqlparser"
GO_TEST_TIMEOUT = 600  # seconds — sqlparser package takes ~30-90s on cold runs


def _run_go_test(run_pattern: str, *, package: str = "./go/vt/sqlparser/...",
                 timeout: int = GO_TEST_TIMEOUT) -> subprocess.CompletedProcess:
    """Run `go test -run <pattern>` for the given package and return result."""
    cmd = ["go", "test", "-count=1", "-run", run_pattern, package]
    return subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "GOFLAGS": "-mod=mod"},
    )


# ---------------------------------------------------------------------------
# Fail-to-pass tests: behaviors that change with the fix.
# ---------------------------------------------------------------------------

def test_versioned_comment_no_space_before_close():
    """`/*!80100 42*/` (no space before `*/`) must parse to `select 42 ...`.

    Base impl bundles a nested Tokenizer with a trailing-space-stripping
    extractor; the closing token positions diverge. Fixed impl scans inline.
    Use a tiny inline-injected Go test for tight scoping.
    """
    inject = SQLPARSER / "f2p_no_space_close_test.go"
    inject.write_text(
        'package sqlparser\n\n'
        'import (\n'
        '\t"testing"\n\n'
        '\t"github.com/stretchr/testify/assert"\n'
        '\t"github.com/stretchr/testify/require"\n'
        ')\n\n'
        'func TestF2P_VersionedNoSpaceBeforeClose(t *testing.T) {\n'
        '\tparser, err := New(Options{MySQLServerVersion: "8.1.20"})\n'
        '\trequire.NoError(t, err)\n'
        '\tstmt, err := parser.Parse("SELECT /*!80100 42*/ FROM dual")\n'
        '\trequire.NoError(t, err)\n'
        '\tassert.Equal(t, "select 42 from dual", String(stmt))\n'
        '}\n'
    )
    try:
        r = _run_go_test("^TestF2P_VersionedNoSpaceBeforeClose$",
                         package="./go/vt/sqlparser/")
        assert r.returncode == 0, (
            f"Versioned-comment without trailing space did not parse correctly:\n"
            f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-2000:]}"
        )
    finally:
        inject.unlink(missing_ok=True)


def test_versioned_comment_unclosed_emits_lex_error():
    """Unclosed versioned comment (`SELECT /*!80100 1 + 2`) must produce a
    parse error at position 22. Base behavior either does not report an error
    or reports a different position via the nested-tokenizer path."""
    inject = SQLPARSER / "f2p_unclosed_test.go"
    inject.write_text(
        'package sqlparser\n\n'
        'import (\n'
        '\t"testing"\n\n'
        '\t"github.com/stretchr/testify/assert"\n'
        '\t"github.com/stretchr/testify/require"\n'
        ')\n\n'
        'func TestF2P_VersionedUnclosed(t *testing.T) {\n'
        '\tparser, err := New(Options{MySQLServerVersion: "8.1.20"})\n'
        '\trequire.NoError(t, err)\n'
        '\t_, err = parser.Parse("SELECT /*!80100 1 + 2")\n'
        '\trequire.Error(t, err)\n'
        '\tassert.EqualError(t, err, "syntax error at position 22")\n'
        '}\n'
    )
    try:
        r = _run_go_test("^TestF2P_VersionedUnclosed$",
                         package="./go/vt/sqlparser/")
        assert r.returncode == 0, (
            f"Unclosed versioned comment did not surface 'syntax error at position 22':\n"
            f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-2000:]}"
        )
    finally:
        inject.unlink(missing_ok=True)


def test_versioned_comment_nested_regular_comment():
    """`/*!80100 1 /* a comment */ + 2 */` (one level of nested regular comment)
    must parse to `select 1 + 2 from dual`. Base impl does not support nested
    comments inside versioned comments (treats first `*/` as closing the outer)."""
    inject = SQLPARSER / "f2p_nested_regular_test.go"
    inject.write_text(
        'package sqlparser\n\n'
        'import (\n'
        '\t"testing"\n\n'
        '\t"github.com/stretchr/testify/assert"\n'
        '\t"github.com/stretchr/testify/require"\n'
        ')\n\n'
        'func TestF2P_VersionedNestedRegularComment(t *testing.T) {\n'
        '\tparser, err := New(Options{MySQLServerVersion: "8.1.20"})\n'
        '\trequire.NoError(t, err)\n'
        '\tstmt, err := parser.Parse("SELECT /*!80100 1 /* a comment */ + 2 */")\n'
        '\trequire.NoError(t, err)\n'
        '\tassert.Equal(t, "select 1 + 2 from dual", String(stmt))\n'
        '}\n'
    )
    try:
        r = _run_go_test("^TestF2P_VersionedNestedRegularComment$",
                         package="./go/vt/sqlparser/")
        assert r.returncode == 0, (
            f"Nested regular comment inside versioned comment did not parse correctly:\n"
            f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-2000:]}"
        )
    finally:
        inject.unlink(missing_ok=True)


def test_versioned_comment_nested_versioned_in_skipped():
    """`/*!90000 1 /*!99999 nested */ + 2 */ 42`: the OUTER versioned comment
    is skipped (parser version 8.1.20 < 90000), but the inner `/*!99999...*/`
    must be tracked as one level of nesting so the outer's `*/` is not eaten
    early. Result must be `select 42 from dual`. Base impl mishandles nesting."""
    inject = SQLPARSER / "f2p_nested_versioned_skipped_test.go"
    inject.write_text(
        'package sqlparser\n\n'
        'import (\n'
        '\t"testing"\n\n'
        '\t"github.com/stretchr/testify/assert"\n'
        '\t"github.com/stretchr/testify/require"\n'
        ')\n\n'
        'func TestF2P_VersionedNestedInsideSkipped(t *testing.T) {\n'
        '\tparser, err := New(Options{MySQLServerVersion: "8.1.20"})\n'
        '\trequire.NoError(t, err)\n'
        '\tstmt, err := parser.Parse("SELECT /*!90000 1 /*!99999 nested */ + 2 */ 42")\n'
        '\trequire.NoError(t, err)\n'
        '\tassert.Equal(t, "select 42 from dual", String(stmt))\n'
        '}\n'
    )
    try:
        r = _run_go_test("^TestF2P_VersionedNestedInsideSkipped$",
                         package="./go/vt/sqlparser/")
        assert r.returncode == 0, (
            f"Nested versioned comment inside skipped block did not parse correctly:\n"
            f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-2000:]}"
        )
    finally:
        inject.unlink(missing_ok=True)


def test_versioned_comment_short_digits_are_content():
    """`/*!8010*/` has fewer than 5 digits, so MySQL treats them as comment
    content (not a version). Result: `select 8010 from dual`. Base impl
    discards the content because the inner tokenizer drops it differently."""
    inject = SQLPARSER / "f2p_short_digits_test.go"
    inject.write_text(
        'package sqlparser\n\n'
        'import (\n'
        '\t"testing"\n\n'
        '\t"github.com/stretchr/testify/assert"\n'
        '\t"github.com/stretchr/testify/require"\n'
        ')\n\n'
        'func TestF2P_VersionedShortDigitsAreContent(t *testing.T) {\n'
        '\tparser, err := New(Options{MySQLServerVersion: "8.1.20"})\n'
        '\trequire.NoError(t, err)\n'
        '\tstmt, err := parser.Parse("SELECT /*!8010*/ FROM dual")\n'
        '\trequire.NoError(t, err)\n'
        '\tassert.Equal(t, "select 8010 from dual", String(stmt))\n'
        '}\n'
    )
    try:
        r = _run_go_test("^TestF2P_VersionedShortDigitsAreContent$",
                         package="./go/vt/sqlparser/")
        assert r.returncode == 0, (
            f"Short-digit versioned comment did not parse digits as content:\n"
            f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-2000:]}"
        )
    finally:
        inject.unlink(missing_ok=True)


def test_versioned_comment_no_digits_treated_as_content():
    """`/*!2*/` (single digit, no version) was previously parsed as
    `select 1 from dual` (digit silently swallowed by nested-tokenizer mode).
    Per MySQL spec the `2` should be content, leading to `select 1 2`, which
    is a syntax error. Base parses cleanly; fixed impl errors."""
    inject = SQLPARSER / "f2p_one_digit_content_test.go"
    inject.write_text(
        'package sqlparser\n\n'
        'import (\n'
        '\t"testing"\n\n'
        '\t"github.com/stretchr/testify/assert"\n'
        '\t"github.com/stretchr/testify/require"\n'
        ')\n\n'
        'func TestF2P_VersionedOneDigitIsError(t *testing.T) {\n'
        '\tparser, err := New(Options{MySQLServerVersion: "8.1.20"})\n'
        '\trequire.NoError(t, err)\n'
        '\t_, err = parser.Parse("select 1/*!2*/;")\n'
        '\trequire.Error(t, err, "expected syntax error since `2` becomes content next to `1`")\n'
        '\tassert.Contains(t, err.Error(), "syntax error")\n'
        '}\n'
    )
    try:
        r = _run_go_test("^TestF2P_VersionedOneDigitIsError$",
                         package="./go/vt/sqlparser/")
        assert r.returncode == 0, (
            f"`select 1/*!2*/` did not raise a syntax error as expected:\n"
            f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-2000:]}"
        )
    finally:
        inject.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Pass-to-pass tests: behaviors that should still work after the fix.
# ---------------------------------------------------------------------------

def test_p2p_sqlparser_package_tests():
    """Run the full sqlparser unit test suite. After the fix this must pass;
    on base it also passes (since none of the existing tests target the new
    behavior). This is the standard repo-CI guard."""
    r = subprocess.run(
        ["go", "test", "-count=1", "-timeout=300s", "./go/vt/sqlparser/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=900,
    )
    assert r.returncode == 0, (
        f"sqlparser package tests failed:\n"
        f"STDOUT (tail):\n{r.stdout[-2500:]}\n\nSTDERR (tail):\n{r.stderr[-1500:]}"
    )


def test_p2p_go_vet_clean():
    """`go vet ./go/vt/sqlparser/...` is part of vitess CI. The fix must keep
    the package vet-clean."""
    r = subprocess.run(
        ["bash", "-lc", "go vet ./go/vt/sqlparser/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"go vet failed:\n{r.stderr[-1500:]}"


def test_p2p_gofumpt_check():
    """`gofumpt -l .` in the sqlparser package must report no unformatted files.
    The repo's AGENTS.md mandates gofumpt formatting on all changed Go files."""
    r = subprocess.run(
        ["bash", "-lc", "gofumpt -l ."],
        cwd=SQLPARSER,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"gofumpt failed:\n{r.stderr[-1500:]}"
    assert r.stdout.strip() == "", (
        f"gofumpt found unformatted files:\n{r.stdout[-1500:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_unit_test_record_test_results_in_launchable():
    """pass_to_pass | CI job 'Unit Test' → step 'Record test results in launchable'"""
    r = subprocess.run(
        ["bash", "-lc", 'launchable record tests --build "$GITHUB_RUN_ID" go-test . || true'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Record test results in launchable' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_test_slowest_tests():
    """pass_to_pass | CI job 'Unit Test' → step 'Slowest Tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'echo \'## Slowest Tests\' >> "$GITHUB_STEP_SUMMARY"\necho \'```\' >> "$GITHUB_STEP_SUMMARY"\ngo tool gotestsum tool slowest --num 20 --jsonfile report.json | tee -a "$GITHUB_STEP_SUMMARY"\necho \'```\' >> "$GITHUB_STEP_SUMMARY"'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Slowest Tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_end_to_end_test_run_make_minimaltools():
    """pass_to_pass | CI job 'End-to-End Test' → step 'Run make minimaltools'"""
    r = subprocess.run(
        ["bash", "-lc", 'make minimaltools'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run make minimaltools' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_end_to_end_test_build():
    """pass_to_pass | CI job 'End-to-End Test' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", 'NOVTADMINBUILD=1 make build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_run_upgrade_downgrade_test___q_run_query_serving_tests_vtgate_n_1_vttab():
    """pass_to_pass | CI job 'Run Upgrade Downgrade Test - Query Serving' → step 'Run query serving tests (vtgate=N-1, vttablet=N, vtctld=N)'"""
    r = subprocess.run(
        ["bash", "-lc", 'go run test.go -skip-build -keep-data=false -docker=false -print-log -follow -tag upgrade_downgrade_query_serving_queries'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run query serving tests (vtgate=N-1, vttablet=N, vtctld=N)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_run_upgrade_downgrade_test___r_run_reparent_tests_vtctl_n_vttablet_n_1():
    """pass_to_pass | CI job 'Run Upgrade Downgrade Test - Reparent New VTTablet' → step 'Run reparent tests (vtctl=N, vttablet=N+1)'"""
    r = subprocess.run(
        ["bash", "-lc", 'go run test.go -skip-build -keep-data=false -docker=false -print-log -follow -tag upgrade_downgrade_reparent'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run reparent tests (vtctl=N, vttablet=N+1)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_run_semi_sync_upgrade_downgrad_run_semi_sync_tests():
    """pass_to_pass | CI job 'Run Semi Sync Upgrade Downgrade Test' → step 'Run semi sync tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'go test -v -count=1 -run="" ./go/test/endtoend/reparent/semisync'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run semi sync tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_run_endtoend_tests_on_vitess_t_run_cluster_endtoend_test():
    """pass_to_pass | CI job 'Run endtoend tests on Vitess Tester' → step 'Run cluster endtoend test'"""
    r = subprocess.run(
        ["bash", "-lc", 'make build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run cluster endtoend test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_run_endtoend_tests_on_vitess_t_record_test_results_in_launchable_if_pr():
    """pass_to_pass | CI job 'Run endtoend tests on Vitess Tester' → step 'Record test results in launchable if PR is not a draft'"""
    r = subprocess.run(
        ["bash", "-lc", '# send recorded tests to launchable\nlaunchable record tests --build "$GITHUB_RUN_ID" go-test . || true'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Record test results in launchable if PR is not a draft' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_run_endtoend_tests_on_vitess_t_print_test_output():
    """pass_to_pass | CI job 'Run endtoend tests on Vitess Tester' → step 'Print test output'"""
    r = subprocess.run(
        ["bash", "-lc", '# print test output\ncat report*.xml'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Print test output' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_run_upgrade_downgrade_test___o_run_online_ddl_tests_primary_n_replica_n():
    """pass_to_pass | CI job 'Run Upgrade Downgrade Test - Online DDL flow' → step 'Run Online DDL tests (primary=N, replica=N-1)'"""
    r = subprocess.run(
        ["bash", "-lc", 'go run test.go -skip-build -keep-data=false -docker=false -print-log -follow -tag upgrade_downgrade_onlineddl_flow'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Online DDL tests (primary=N, replica=N-1)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
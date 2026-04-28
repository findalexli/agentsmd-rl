import os
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO = Path("/workspace/remix")
PKG = REPO / "packages" / "route-pattern"
MATCHERS_DIR = PKG / "src" / "lib" / "matchers"
ORACLE_PATH = MATCHERS_DIR / "_oracle.test.ts"
TRIE_TS = MATCHERS_DIR / "trie.ts"


def _run_node_test(test_file: Path, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            "node",
            "--disable-warning=ExperimentalWarning",
            "--test",
            str(test_file.relative_to(REPO)),
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _write_oracle(body: str) -> None:
    code = (
        "import * as assert from 'node:assert/strict'\n"
        "import { test } from 'node:test'\n"
        "import { TrieMatcher } from './trie.ts'\n\n"
        + textwrap.dedent(body).strip()
        + "\n"
    )
    ORACLE_PATH.write_text(code)


@pytest.fixture(autouse=True)
def cleanup_oracle():
    yield
    try:
        ORACLE_PATH.unlink()
    except FileNotFoundError:
        pass


# ---------- fail_to_pass: behavioral tests ----------

def test_pathname_only_static_matches():
    """Pathname-only static pattern (no hostname) matches across hostnames."""
    _write_oracle("""
        test('static', () => {
          let m = new TrieMatcher<null>()
          m.add('users', null)
          let match = m.match('https://example.com/users')
          assert.ok(match, 'expected pathname-only pattern to match')
          assert.deepEqual(match.params, {})
          assert.equal(match.url.pathname, '/users')
        })
    """)
    r = _run_node_test(ORACLE_PATH)
    assert r.returncode == 0, f"Test failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"


def test_pathname_only_nested_static_matches():
    """Multi-segment pathname-only pattern matches."""
    _write_oracle("""
        test('nested', () => {
          let m = new TrieMatcher<null>()
          m.add('api/v1/users', null)
          let match = m.match('https://example.com/api/v1/users')
          assert.ok(match)
          assert.deepEqual(match.params, {})
        })
    """)
    r = _run_node_test(ORACLE_PATH)
    assert r.returncode == 0, f"Test failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"


def test_pathname_only_variable_matches():
    """Pathname-only pattern with named parameter matches and captures the param."""
    _write_oracle("""
        test('variable', () => {
          let m = new TrieMatcher<null>()
          m.add('users/:id', null)
          let match = m.match('https://example.com/users/123')
          assert.ok(match)
          assert.deepEqual(match.params, { id: '123' })
        })
    """)
    r = _run_node_test(ORACLE_PATH)
    assert r.returncode == 0, f"Test failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"


def test_pathname_only_wildcard_matches():
    """Pathname-only pattern with wildcard matches and captures remainder."""
    _write_oracle("""
        test('wildcard', () => {
          let m = new TrieMatcher<null>()
          m.add('files/*path', null)
          let match = m.match('https://example.com/files/docs/readme.txt')
          assert.ok(match)
          assert.deepEqual(match.params, { path: 'docs/readme.txt' })
        })
    """)
    r = _run_node_test(ORACLE_PATH)
    assert r.returncode == 0, f"Test failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"


def test_pathname_only_matches_across_hostnames():
    """The same pathname-only pattern matches the same path under multiple hostnames."""
    _write_oracle("""
        test('cross-host', () => {
          let m = new TrieMatcher<null>()
          m.add('api/users', null)
          assert.ok(m.match('https://example.com/api/users'))
          assert.ok(m.match('https://other.com/api/users'))
          assert.ok(m.match('http://localhost/api/users'))
        })
    """)
    r = _run_node_test(ORACLE_PATH)
    assert r.returncode == 0, f"Test failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"


def test_match_returns_null_when_no_match():
    """match() returns null (not undefined) when there is no matching pattern."""
    _write_oracle("""
        test('null on miss', () => {
          let m = new TrieMatcher<null>()
          let res = m.match('https://example.com/users')
          assert.strictEqual(res, null, 'match() must return null, not undefined, on miss')
        })

        test('null on hostname mismatch', () => {
          let m = new TrieMatcher<null>()
          m.add('://example.com/users', null)
          let res = m.match('https://other.com/users')
          assert.strictEqual(res, null)
        })
    """)
    r = _run_node_test(ORACLE_PATH)
    assert r.returncode == 0, f"Test failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"


def test_explicit_hostname_does_not_match_different_host():
    """A pattern with an explicit hostname must not match a different hostname."""
    _write_oracle("""
        test('hostname mismatch', () => {
          let m = new TrieMatcher<null>()
          m.add('://example.com/users', null)
          let match = m.match('https://other.com/users')
          assert.equal(match, null)
        })

        test('static hostname stays scoped', () => {
          let m = new TrieMatcher<null>()
          m.add('://example.com/users', null)
          let direct = m.match('https://example.com/users')
          assert.ok(direct, 'should still match the declared hostname')
        })
    """)
    r = _run_node_test(ORACLE_PATH)
    assert r.returncode == 0, f"Test failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"


# ---------- pass_to_pass: existing repo tests still pass ----------

def test_existing_trie_tests_pass():
    """Existing TrieMatcher tests under packages/route-pattern still pass."""
    r = subprocess.run(
        [
            "node",
            "--disable-warning=ExperimentalWarning",
            "--test",
            "packages/route-pattern/src/lib/matchers/trie.test.ts",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, f"Existing trie tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"


def test_existing_array_matcher_tests_pass():
    """Sibling ArrayMatcher tests still pass — guards against regressions in the matchers module."""
    r = subprocess.run(
        [
            "node",
            "--disable-warning=ExperimentalWarning",
            "--test",
            "packages/route-pattern/src/lib/matchers/array.test.ts",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, f"Array matcher tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"


# ---------- agent_config: programmatic style rules from AGENTS.md ----------

def test_no_var_declarations_in_trie():
    """AGENTS.md (root): 'never use var'. trie.ts must not introduce var declarations."""
    src = TRIE_TS.read_text()
    import re
    for m in re.finditer(r"(?m)^\s*var\s+\w", src):
        pytest.fail(f"trie.ts contains a `var` declaration: {m.group(0)!r}")


def test_no_typescript_accessibility_modifiers_in_trie():
    """AGENTS.md (root): no TypeScript accessibility modifiers on class members."""
    src = TRIE_TS.read_text()
    import re
    for kw in ("public", "private", "protected"):
        pattern = r"(?m)^\s+" + kw + r"\s+\w"
        m = re.search(pattern, src)
        if m:
            pytest.fail(f"trie.ts uses TypeScript accessibility modifier `{kw}`: {m.group(0)!r}")


# === CI-mined tests (scoped to affected package) ===
def test_ci_check_lint():
    """pass_to_pass | CI job 'check' -> step 'Lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_check_typecheck():
    """pass_to_pass | CI job 'check' -> step 'Typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter @remix-run/route-pattern typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_check_check_change_files():
    """pass_to_pass | CI job 'check' -> step 'Check change files'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm changes:validate'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check change files' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_build_build_packages():
    """pass_to_pass | CI job 'build' -> step 'Build packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter @remix-run/route-pattern build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' -> step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter @remix-run/route-pattern test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

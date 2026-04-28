import subprocess
import os

REPO = "/workspace/remix"


def _run_ts(script: str) -> subprocess.CompletedProcess:
    cwd = os.path.join(REPO, "packages/route-pattern")
    return subprocess.run(
        ["tsx", "-e", script],
        capture_output=True, text=True, timeout=60, cwd=cwd,
    )


# === fail_to_pass tests ===

def test_pathname_only_pattern_matches():
    """Pathname-only patterns (no hostname) match URLs with any hostname."""
    script = """\
import { TrieMatcher } from './src/lib/matchers/trie.ts'
const m = new TrieMatcher()
m.add('users/:id', 'test-data')
const result = m.match('https://example.com/users/123')
if (!result) { console.log('FAIL: match() returned', result); process.exit(1) }
if (result.params.id !== '123') { console.log('FAIL: expected id=123, got', JSON.stringify(result.params)); process.exit(1) }
if (result.data !== 'test-data') { console.log('FAIL: expected data=test-data, got', result.data); process.exit(1) }
console.log('PASS')
"""
    r = _run_ts(script)
    assert r.returncode == 0, f"Test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"


def test_pathname_only_with_variable_matches():
    """Pathname-only patterns with variable segments match correctly."""
    script = """\
import { TrieMatcher } from './src/lib/matchers/trie.ts'
const m = new TrieMatcher()
m.add('api/v1/users/:id', 'user-info')
const result = m.match('https://other.com/api/v1/users/42')
if (!result) { console.log('FAIL: match() returned', result); process.exit(1) }
if (result.params.id !== '42') { console.log('FAIL: expected id=42, got', JSON.stringify(result.params)); process.exit(1) }
if (result.data !== 'user-info') { console.log('FAIL: expected data=user-info, got', result.data); process.exit(1) }
console.log('PASS')
"""
    r = _run_ts(script)
    assert r.returncode == 0, f"Test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"


def test_pathname_only_wildcard_matches():
    """Pathname-only patterns with wildcard segments match correctly."""
    script = """\
import { TrieMatcher } from './src/lib/matchers/trie.ts'
const m = new TrieMatcher()
m.add('files/*path', 'file-data')
const result = m.match('http://localhost/files/docs/readme.txt')
if (!result) { console.log('FAIL: match() returned', result); process.exit(1) }
if (result.params.path !== 'docs/readme.txt') { console.log('FAIL: expected path=docs/readme.txt, got', JSON.stringify(result.params)); process.exit(1) }
if (result.data !== 'file-data') { console.log('FAIL: expected data=file-data, got', result.data); process.exit(1) }
console.log('PASS')
"""
    r = _run_ts(script)
    assert r.returncode == 0, f"Test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"


def test_match_returns_null_for_no_match():
    """match() returns null (not undefined) when no route matches."""
    script = """\
import { TrieMatcher } from './src/lib/matchers/trie.ts'
const m = new TrieMatcher()
m.add('://example.com/users', 'data1')
const result = m.match('https://other.com/users')
if (result !== null) { console.log('FAIL: expected null, got', result, 'type:', typeof result); process.exit(1) }
console.log('PASS')
"""
    r = _run_ts(script)
    assert r.returncode == 0, f"Test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"


# === pass_to_pass tests ===

def test_trie_matcher_importable():
    """TrieMatcher can be imported from its source file."""
    script = """\
import { TrieMatcher } from './src/lib/matchers/trie.ts'
console.log('OK')
"""
    r = _run_ts(script)
    assert r.returncode == 0, f"Import failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"


def test_ci_check_lint():
    """pass_to_pass | CI job 'check' -> step 'Lint' (scoped to route-pattern)."""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm eslint packages/route-pattern/ --max-warnings=0'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_check_typecheck():
    """pass_to_pass | CI job 'check' -> step 'Typecheck' (scoped to route-pattern)."""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter @remix-run/route-pattern typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_check_check_change_files():
    """pass_to_pass | CI job 'check' -> step 'Check change files'."""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm changes:validate'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check change files' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_build_build_packages():
    """pass_to_pass | CI job 'build' -> step 'Build packages' (scoped to route-pattern)."""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter @remix-run/route-pattern build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' -> step 'Run tests' (scoped to route-pattern trie tests)."""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter @remix-run/route-pattern vitest run src/lib/matchers/trie.test.ts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

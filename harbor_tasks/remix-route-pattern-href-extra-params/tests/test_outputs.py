"""Tests for remix-run/remix#11017: route-pattern href types allow extra params."""

import subprocess
import pathlib

REPO = pathlib.Path("/workspace/remix")
PKG = REPO / "packages" / "route-pattern"

TYPE_TEST_FILE = PKG / "extra_params_type_check.ts"
TYPE_TEST_FILE_2 = PKG / "extra_params_optional_routes_check.ts"


def _write_type_test_file():
    """Write a .ts file that passes extra params to href() as object literals."""
    content = """\
import { RoutePattern } from './src/index.ts'

// Object literals with extra properties — should NOT cause TS2353 errors
let pattern1 = new RoutePattern('/posts/:id')
let r1 = pattern1.href({ id: '123', extra: 'stuff' })

let r2 = pattern1.href({ id: '123', page: '2', sort: 'desc' })

let pattern2 = new RoutePattern('/files/*path')
let r3 = pattern2.href({ path: 'docs/readme.md', mode: 'fast' })

let pattern3 = new RoutePattern('/:lang/users/:userId/:lang/posts/:postId')
let r4 = pattern3.href({ lang: 'en', userId: '42', postId: '123' })
"""
    TYPE_TEST_FILE.write_text(content)


def _write_type_test_file_2():
    """Write a .ts file testing extra params on routes with optional segments."""
    content = """\
import { RoutePattern } from './src/index.ts'

// Optional segments with extra properties — should NOT cause TS2353 errors
let pattern1 = new RoutePattern('(/:locale)(/:page)')
let r1 = pattern1.href({ locale: 'en', page: '1', sort: 'asc' })

let pattern2 = new RoutePattern('/posts(/:id)')
let r2 = pattern2.href({ id: '123', extra: 'stuff' })

let pattern3 = new RoutePattern('(/:locale)/posts/:id')
let r3 = pattern3.href({ locale: 'en', id: '42', tag: 'featured' })
"""
    TYPE_TEST_FILE_2.write_text(content)


def test_typecheck_allows_extra_params_in_href():
    """TypeScript typecheck passes when extra params are passed to href().

    On the base commit, passing object literals with extra properties to
    RoutePattern.href() causes TS2353 (excess property) errors. After the
    fix, the HrefParams type includes Record<string, unknown>, allowing
    any additional string-keyed properties.
    """
    _write_type_test_file()

    r = subprocess.run(
        ["npx", "tsgo", "--noEmit", "-p", "tsconfig.json"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Clean up
    TYPE_TEST_FILE.unlink(missing_ok=True)

    assert r.returncode == 0, (
        f"tsgo typecheck failed (exit {r.returncode}). "
        f"Expected no TS2353 excess-property errors.\n"
        f"stderr: {r.stderr[-1000:]}\nstdout: {r.stdout[-1000:]}"
    )


def test_typecheck_extra_params_on_optional_routes():
    """Extra properties on routes with optional segments don't cause TS2353.

    On the base commit, optional routes like (/:locale)(/:page) also produce
    TS2353 errors when extra properties are passed. After the fix, all
    HrefParams variants include Record<string, unknown>, so extra properties
    are allowed regardless of whether the route has optional segments.
    """
    _write_type_test_file_2()

    r = subprocess.run(
        ["npx", "tsgo", "--noEmit", "-p", "tsconfig.json"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=120,
    )
    TYPE_TEST_FILE_2.unlink(missing_ok=True)

    assert r.returncode == 0, (
        f"tsgo typecheck failed (exit {r.returncode}). "
        f"Expected no TS2353 errors on optional-route extra params.\n"
        f"stderr: {r.stderr[-1000:]}\nstdout: {r.stdout[-1000:]}"
    )


def test_route_pattern_tests_pass():
    """Existing route-pattern test suite passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--disable-warning=ExperimentalWarning", "--test"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"Test suite failed (exit {r.returncode}).\n"
        f"stderr: {r.stderr[-1000:]}"
    )


def test_package_typecheck_passes():
    """tsgo --noEmit passes on the route-pattern package (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsgo", "--noEmit", "-p", "tsconfig.json"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"Package typecheck failed (exit {r.returncode}).\n"
        f"stderr: {r.stderr[-1000:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_format_format():
    """pass_to_pass | CI job 'format' → step 'Format'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm format'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Format' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_lint():
    """pass_to_pass | CI job 'check' → step 'Lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_typecheck():
    """pass_to_pass | CI job 'check' → step 'Typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_check_change_files():
    """pass_to_pass | CI job 'check' → step 'Check change files'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm changes:validate'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check change files' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_build_packages():
    """pass_to_pass | CI job 'build' → step 'Build packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
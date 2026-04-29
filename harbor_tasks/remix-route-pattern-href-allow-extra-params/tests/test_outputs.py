"""Behavioral tests for the route-pattern href types fix (remix-run/remix#11017).

The PR loosens HrefParams so passing extra (unrelated) keys to RoutePattern.href
typechecks. The runtime already accepted extra keys; only the type was strict.
We exercise the type system by injecting a fixture file into the package and
running the package's own typecheck script (`pnpm --filter ... run typecheck`,
which calls `tsgo --noEmit`).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path("/workspace/remix")
PKG = REPO / "packages" / "route-pattern"
HREF_TS = PKG / "src" / "lib" / "types" / "href.ts"
FIXTURE_DEST = PKG / "src" / "lib" / "types" / "_href_type_fixture.ts"

# Type-fixture contents. Lives only in this module; copied into the package
# at test time and removed afterwards. Each non-`@ts-expect-error` `let`
# declaration must typecheck once HrefParams permits keys that aren't named
# in the route pattern; the `@ts-expect-error` lines must REMAIN errors so
# the fix doesn't accidentally drop the required-param constraint.
_FIXTURE_TS = """\
import { RoutePattern } from '../route-pattern.ts'

let pattern1 = new RoutePattern('/posts/:id')

let r1: string = pattern1.href({ id: '123', page: '2', sort: 'desc' })

let r2: string = pattern1.href({ id: 1, extra: 'stuff' })

// @ts-expect-error - missing required param 'id'
let r3: string = pattern1.href({})

// @ts-expect-error - missing required param 'id'
let r4: string = pattern1.href({ extra: 'only' })

let pattern2 = new RoutePattern('/files/*path')
let r5: string = pattern2.href({ path: 'docs', other: 'thing' })
let r6: string = pattern2.href({ path: 123, other: 'thing' })

let pattern3 = new RoutePattern('/users/:userId/posts/:postId')
let r7: string = pattern3.href({ userId: 'me', postId: '7', irrelevant: true })

export { r1, r2, r3, r4, r5, r6, r7 }
"""


def _run_typecheck(timeout: int = 240) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["pnpm", "--filter", "@remix-run/route-pattern", "run", "typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _run_node_tests(timeout: int = 240) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["pnpm", "--filter", "@remix-run/route-pattern", "run", "test"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _ensure_fixture_absent() -> None:
    if FIXTURE_DEST.exists():
        FIXTURE_DEST.unlink()


def _install_fixture() -> None:
    FIXTURE_DEST.write_text(_FIXTURE_TS)


def test_typecheck_baseline_passes():
    """pass_to_pass: package typecheck passes on its own (no fixture)."""
    _ensure_fixture_absent()
    r = _run_typecheck()
    assert r.returncode == 0, (
        f"baseline typecheck failed:\nstdout:\n{r.stdout[-1500:]}\nstderr:\n{r.stderr[-500:]}"
    )


def test_runtime_tests_pass():
    """pass_to_pass: route-pattern's node:test suite passes."""
    _ensure_fixture_absent()
    r = _run_node_tests()
    assert r.returncode == 0, (
        f"node tests failed:\nstdout:\n{r.stdout[-1500:]}\nstderr:\n{r.stderr[-500:]}"
    )


def test_extra_params_typecheck():
    """fail_to_pass: passing keys not declared by the route pattern must
    typecheck. We inject a fixture using `pattern.href({ id, extra })` shapes
    and require the package's typecheck to succeed.
    """
    _install_fixture()
    try:
        r = _run_typecheck()
    finally:
        _ensure_fixture_absent()
    assert r.returncode == 0, (
        "extra-params fixture failed typecheck — the HrefParams type still "
        "rejects keys that are not declared by the route pattern.\n"
        f"stdout:\n{r.stdout[-1500:]}\nstderr:\n{r.stderr[-500:]}"
    )


def test_required_params_still_required():
    """fail_to_pass: the fix must not silently make required params optional.
    The fixture asserts `// @ts-expect-error` on calls missing required params;
    if the fix is too loose (e.g. `Record<string, unknown>` only), those
    directives would be unused and tsgo reports TS2578.
    """
    _install_fixture()
    try:
        r = _run_typecheck()
    finally:
        _ensure_fixture_absent()
    combined = (r.stdout or "") + (r.stderr or "")
    assert "TS2578" not in combined, (
        "Type fix is too loose: a `@ts-expect-error` directive guarding a "
        "missing required param became unused (TS2578). Required params "
        "must remain required.\n" + combined[-1500:]
    )
    assert r.returncode == 0, (
        f"typecheck still failing:\nstdout:\n{r.stdout[-1500:]}\nstderr:\n{r.stderr[-500:]}"
    )


def test_href_ts_modified():
    """fail_to_pass: sanity guard that href.ts has been edited away from the
    buggy intersection. The base shape was
    `Record<RequiredParams<...>, ParamValue> & Partial<...>` with no
    index-signature widening.
    """
    src = HREF_TS.read_text()
    pre_fix_signature = (
        "Record<RequiredParams<T>, ParamValue> &\n"
        "  Partial<Record<OptionalParams<T>, ParamValue | null | undefined>>"
    )
    assert pre_fix_signature not in src, (
        "href.ts still contains the original strict HrefParams definition unchanged"
    )

# CI-mined pass_to_pass: format and lint at the monorepo level validates that the
# fix conforms to repo-wide code-style rules.
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

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_works_with_number_params():
    """fail_to_pass | PR added test 'works with number params' in 'packages/route-pattern/src/lib/route-pattern.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/route-pattern/src/lib/route-pattern.test.ts" -t "works with number params" 2>&1 || npx vitest run "packages/route-pattern/src/lib/route-pattern.test.ts" -t "works with number params" 2>&1 || pnpm jest "packages/route-pattern/src/lib/route-pattern.test.ts" -t "works with number params" 2>&1 || npx jest "packages/route-pattern/src/lib/route-pattern.test.ts" -t "works with number params" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'works with number params' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_ignores_unrelated_params():
    """fail_to_pass | PR added test 'ignores unrelated params' in 'packages/route-pattern/src/lib/route-pattern.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/route-pattern/src/lib/route-pattern.test.ts" -t "ignores unrelated params" 2>&1 || npx vitest run "packages/route-pattern/src/lib/route-pattern.test.ts" -t "ignores unrelated params" 2>&1 || pnpm jest "packages/route-pattern/src/lib/route-pattern.test.ts" -t "ignores unrelated params" 2>&1 || npx jest "packages/route-pattern/src/lib/route-pattern.test.ts" -t "ignores unrelated params" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'ignores unrelated params' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_supports_wildcard_with_number_param():
    """fail_to_pass | PR added test 'supports wildcard with number param' in 'packages/route-pattern/src/lib/route-pattern.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/route-pattern/src/lib/route-pattern.test.ts" -t "supports wildcard with number param" 2>&1 || npx vitest run "packages/route-pattern/src/lib/route-pattern.test.ts" -t "supports wildcard with number param" 2>&1 || pnpm jest "packages/route-pattern/src/lib/route-pattern.test.ts" -t "supports wildcard with number param" 2>&1 || npx jest "packages/route-pattern/src/lib/route-pattern.test.ts" -t "supports wildcard with number param" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'supports wildcard with number param' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_supports_repeated_params():
    """fail_to_pass | PR added test 'supports repeated params' in 'packages/route-pattern/src/lib/route-pattern.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/route-pattern/src/lib/route-pattern.test.ts" -t "supports repeated params" 2>&1 || npx vitest run "packages/route-pattern/src/lib/route-pattern.test.ts" -t "supports repeated params" 2>&1 || pnpm jest "packages/route-pattern/src/lib/route-pattern.test.ts" -t "supports repeated params" 2>&1 || npx jest "packages/route-pattern/src/lib/route-pattern.test.ts" -t "supports repeated params" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'supports repeated params' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_handles_optional_locale_and_page_on_home_route():
    """fail_to_pass | PR added test 'handles optional locale and page on home route' in 'packages/route-pattern/src/lib/route-pattern.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/route-pattern/src/lib/route-pattern.test.ts" -t "handles optional locale and page on home route" 2>&1 || npx vitest run "packages/route-pattern/src/lib/route-pattern.test.ts" -t "handles optional locale and page on home route" 2>&1 || pnpm jest "packages/route-pattern/src/lib/route-pattern.test.ts" -t "handles optional locale and page on home route" 2>&1 || npx jest "packages/route-pattern/src/lib/route-pattern.test.ts" -t "handles optional locale and page on home route" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'handles optional locale and page on home route' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_throws_for_unnamed_wildcard():
    """fail_to_pass | PR added test 'throws for unnamed wildcard' in 'packages/route-pattern/src/lib/route-pattern.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/route-pattern/src/lib/route-pattern.test.ts" -t "throws for unnamed wildcard" 2>&1 || npx vitest run "packages/route-pattern/src/lib/route-pattern.test.ts" -t "throws for unnamed wildcard" 2>&1 || pnpm jest "packages/route-pattern/src/lib/route-pattern.test.ts" -t "throws for unnamed wildcard" 2>&1 || npx jest "packages/route-pattern/src/lib/route-pattern.test.ts" -t "throws for unnamed wildcard" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'throws for unnamed wildcard' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

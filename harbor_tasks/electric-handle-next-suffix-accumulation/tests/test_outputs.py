"""Verifier for the `electric-handle-next-suffix-accumulation` task.

The task asks the agent to fix a bug in `@electric-sql/client` where the
ShapeStream client mutated the shape handle by appending `-next` whenever a
409 response arrived without an `electric-handle` header.  Repeated 409s
caused `handle-next-next-next-…` URLs that grew unboundedly and eventually
tripped HTTP 414 / 5xx errors on production proxies.

The fail-to-pass tests below drive the client through several 409 responses
that lack the handle header and assert the *behavioral* invariants of a
correct fix: retries must be unique, must not embed `-next`, and must not
embed the literal string `undefined` in the URL.

The pass-to-pass tests run the repo's own vitest unit suite (and the
TypeScript compiler) so we catch regressions in unrelated functionality.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/electric")
PKG = REPO / "packages" / "typescript-client"
TEST_DIR = PKG / "test"

# Marker we drop on disk to flag the f2p test as installed.  Cleaned up by
# `_install_f2p_test` itself when the function reruns.
F2P_TEST = TEST_DIR / "_taskforge_handle_no_next.test.ts"
F2P_CONFIG = PKG / "_taskforge_f2p.config.ts"


F2P_TEST_BODY = r"""
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { ShapeStream } from '../src'
import { expiredShapesCache } from '../src/expired-shapes-cache'

describe(`taskforge regression: handle -next suffix accumulation`, () => {
  const shapeUrl = `https://example.com/v1/shape`
  let aborter: AbortController
  let fetchMock: ReturnType<
    typeof vi.fn<
      (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>
    >
  >

  beforeEach(() => {
    localStorage.clear()
    expiredShapesCache.clear()
    aborter = new AbortController()
    fetchMock = vi.fn<
      (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>
    >()
    vi.clearAllMocks()
  })

  afterEach(() => aborter.abort())

  it(`does not append -next to the handle when 409 lacks handle header (initial handle present)`, async () => {
    let requestCount = 0
    const capturedUrls: string[] = []
    const maxRequests = 8

    fetchMock.mockImplementation((input: RequestInfo | URL) => {
      requestCount++
      capturedUrls.push(input.toString())

      if (requestCount >= maxRequests) {
        aborter.abort()
        return Promise.resolve(
          new Response(JSON.stringify([]), {
            status: 200,
            headers: {
              'electric-handle': `final-handle`,
              'electric-offset': `0_0`,
              'electric-schema': `{}`,
              'electric-cursor': `cursor-1`,
            },
          })
        )
      }

      return Promise.resolve(new Response(`[]`, { status: 409 }))
    })

    const stream = new ShapeStream({
      url: shapeUrl,
      params: { table: `test` },
      handle: `original-handle`,
      signal: aborter.signal,
      fetchClient: fetchMock,
      subscribe: false,
    })

    stream.subscribe(() => {})

    await new Promise((resolve) => setTimeout(resolve, 500))

    for (const urlStr of capturedUrls) {
      expect(urlStr, `URL contains "-next": ${urlStr}`).not.toContain(`-next`)
    }

    const urlsAfterFirst = capturedUrls.slice(1)
    for (const urlStr of urlsAfterFirst) {
      const url = new URL(urlStr)
      const hasCacheBuster = url.searchParams.has(`cache-buster`)
      const hasExpiredHandle = url.searchParams.has(`expired_handle`)
      expect(
        hasCacheBuster || hasExpiredHandle,
        `Retry URL lacks cache-buster and expired_handle: ${urlStr}`
      ).toBe(true)
    }

    const uniqueUrls = new Set(capturedUrls)
    expect(
      uniqueUrls.size,
      `Expected ${capturedUrls.length} unique URLs but got ${uniqueUrls.size}`
    ).toBe(capturedUrls.length)
  })

  it(`does not embed the string "undefined" or "-next" when 409 lacks handle header (no initial handle)`, async () => {
    let requestCount = 0
    const capturedUrls: string[] = []
    const maxRequests = 8

    fetchMock.mockImplementation((input: RequestInfo | URL) => {
      requestCount++
      capturedUrls.push(input.toString())

      if (requestCount >= maxRequests) {
        aborter.abort()
        return Promise.resolve(
          new Response(JSON.stringify([]), {
            status: 200,
            headers: {
              'electric-handle': `final-handle`,
              'electric-offset': `0_0`,
              'electric-schema': `{}`,
              'electric-cursor': `cursor-1`,
            },
          })
        )
      }

      return Promise.resolve(new Response(`[]`, { status: 409 }))
    })

    const stream = new ShapeStream({
      url: shapeUrl,
      params: { table: `test` },
      signal: aborter.signal,
      fetchClient: fetchMock,
      subscribe: false,
    })

    stream.subscribe(() => {})

    await new Promise((resolve) => setTimeout(resolve, 500))

    for (const urlStr of capturedUrls) {
      expect(urlStr, `URL contains "undefined": ${urlStr}`).not.toContain(
        `undefined`
      )
      expect(urlStr, `URL contains "-next": ${urlStr}`).not.toContain(`-next`)
    }

    const uniqueUrls = new Set(capturedUrls)
    expect(
      uniqueUrls.size,
      `Expected ${capturedUrls.length} unique URLs but got ${uniqueUrls.size}`
    ).toBe(capturedUrls.length)
  })
})
""".lstrip()


F2P_CONFIG_BODY = textwrap.dedent("""\
    import { defineConfig } from 'vitest/config'

    export default defineConfig({
      test: {
        setupFiles: [`vitest-localstorage-mock`],
        include: [`test/_taskforge_handle_no_next.test.ts`],
        testTimeout: 30000,
        environment: `jsdom`,
      },
    })
""")


def _install_f2p_test() -> None:
    """Drop the f2p test file and a one-off vitest config into the package."""
    F2P_TEST.write_text(F2P_TEST_BODY)
    F2P_CONFIG.write_text(F2P_CONFIG_BODY)


def _run_vitest(config_path: str, timeout: int = 240) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["pnpm", "exec", "vitest", "run", "--config", config_path],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "CI": "true"},
    )


def test_handle_no_next_suffix_on_repeated_409s():
    """f2p — Repeated 409s without handle header must not produce ``-next``,
    must not embed ``undefined``, and must produce unique retry URLs.

    At base, ``client.ts`` line ~890 sets
    ``newShapeHandle = e.headers[SHAPE_HANDLE_HEADER] || `${this.#syncState.handle!}-next`,``
    which makes every retry URL contain ``-next`` and identical, so this test
    fails.  After the fix, retries are tagged with a random cache-buster query
    param and the handle is reset rather than mutated.
    """
    _install_f2p_test()
    result = _run_vitest(str(F2P_CONFIG))
    assert result.returncode == 0, (
        f"f2p vitest failed (exit {result.returncode}).\n"
        f"--- stdout ---\n{result.stdout[-4000:]}\n"
        f"--- stderr ---\n{result.stderr[-2000:]}"
    )


def test_repo_unit_suite_passes():
    """p2p — The repo's own unit-test suite (10 files, ~295 tests) must pass.

    This guards against regressions in the rest of the client introduced by
    the agent's edit.  Runs vitest with ``vitest.unit.config.ts`` exactly the
    way upstream CI does.
    """
    result = subprocess.run(
        [
            "pnpm",
            "exec",
            "vitest",
            "run",
            "--config",
            "vitest.unit.config.ts",
        ],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CI": "true"},
    )
    assert result.returncode == 0, (
        f"repo unit suite failed (exit {result.returncode}).\n"
        f"--- stdout ---\n{result.stdout[-4000:]}\n"
        f"--- stderr ---\n{result.stderr[-2000:]}"
    )


def test_typecheck_passes():
    """p2p — ``tsc --noEmit`` against the package's ``tsconfig.json`` must
    succeed.  Catches type errors introduced by the fix.
    """
    result = subprocess.run(
        ["pnpm", "exec", "tsc", "-p", "tsconfig.json", "--noEmit"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "true"},
    )
    assert result.returncode == 0, (
        f"typecheck failed (exit {result.returncode}).\n"
        f"--- stdout ---\n{result.stdout[-4000:]}\n"
        f"--- stderr ---\n{result.stderr[-2000:]}"
    )

# === PR-added f2p tests (taskforge.test_patch_miner) ===
# Each test runs the full test file with the upstream Vitest unit config and
# extracts the number of passing tests from the summary line.  The PR adds new
# tests to these files, so the count at gold is strictly greater than at base.
# This avoids asserting on gold-patch-specific test-name literals.

def _run_vitest_file(test_file: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["pnpm", "exec", "vitest", "run", "--config", "vitest.unit.config.ts",
         test_file],
        cwd=PKG, capture_output=True, text=True, timeout=300,
        env={**os.environ, "CI": "true"},
    )


def _get_passed_count(result: subprocess.CompletedProcess) -> int:
    # Strip ANSI escape codes so the regex works on plain text.
    clean = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout)
    m = re.search(r"Tests\s+(\d+)\s+passed", clean)
    assert m is not None, f"could not find test count in vitest output:\n{result.stdout[-2000:]}"
    return int(m.group(1))


def test_pr_added_should_use_cache_buster_instead_of_handle_mutati():
    """f2p | PR added tests in expired-shapes-cache.test.ts — at base 13 tests, at gold 15."""
    r = _run_vitest_file("test/expired-shapes-cache.test.ts")
    assert r.returncode == 0, (
        f"expired-shapes-cache tests failed (exit {r.returncode}).\n"
        f"--- stdout ---\n{r.stdout[-3000:]}\n--- stderr ---\n{r.stderr[-1000:]}")
    count = _get_passed_count(r)
    assert count > 13, (
        f"Expected > 13 tests in expired-shapes-cache but saw {count}. "
        f"PR test patch may not have been applied.")


def test_pr_added_should_use_cache_buster_on_409_without_handle_he():
    """f2p | Duplicate of above — each check entry must have 1:1 test function."""
    r = _run_vitest_file("test/expired-shapes-cache.test.ts")
    assert r.returncode == 0, (
        f"expired-shapes-cache tests failed (exit {r.returncode}).\n"
        f"--- stdout ---\n{r.stdout[-3000:]}\n--- stderr ---\n{r.stderr[-1000:]}")
    count = _get_passed_count(r)
    assert count > 13, (
        f"Expected > 13 tests in expired-shapes-cache but saw {count}. "
        f"PR test patch may not have been applied.")


def test_pr_added_markMustRefetch_without_handle_resets_to_Initial():
    """f2p | PR added tests in shape-stream-state.test.ts — at base 200 tests, at gold 203."""
    r = _run_vitest_file("test/shape-stream-state.test.ts")
    assert r.returncode == 0, (
        f"shape-stream-state tests failed (exit {r.returncode}).\n"
        f"--- stdout ---\n{r.stdout[-3000:]}\n--- stderr ---\n{r.stderr[-1000:]}")
    count = _get_passed_count(r)
    assert count > 200, (
        f"Expected > 200 tests in shape-stream-state but saw {count}. "
        f"PR test patch may not have been applied.")


def test_pr_added_InitialState_without_handle_omits_handle_from_UR():
    """f2p | Duplicate of above — each check entry must have 1:1 test function."""
    r = _run_vitest_file("test/shape-stream-state.test.ts")
    assert r.returncode == 0, (
        f"shape-stream-state tests failed (exit {r.returncode}).\n"
        f"--- stdout ---\n{r.stdout[-3000:]}\n--- stderr ---\n{r.stderr[-1000:]}")
    count = _get_passed_count(r)
    assert count > 200, (
        f"Expected > 200 tests in shape-stream-state but saw {count}. "
        f"PR test patch may not have been applied.")

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_derive_build_variables_from_th_determine_the_ref_to_check_out():
    """pass_to_pass | CI job 'Derive build variables from the source code' → step 'Determine the ref to check out'"""
    r = subprocess.run(
        ["bash", "-lc", 'if [ -n "$INPUT_RELEASE_TAG" ]; then\n  ref="refs/tags/$INPUT_RELEASE_TAG"\n  is_release=true\nelif [ -n "$EVENT_RELEASE_TAG" ]; then\n  ref="refs/tags/$EVENT_RELEASE_TAG"\n  is_release=true\nelse\n  ref="$COMMIT_SHA"\n  is_release=false\nfi\n\necho "git_ref=$ref" >> $GITHUB_OUTPUT\necho "is_release=$is_release" >> $GITHUB_OUTPUT'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Determine the ref to check out' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_derive_build_variables_from_th_determine_short_commit_sha_and_electric():
    """pass_to_pass | CI job 'Derive build variables from the source code' → step 'Determine short_commit_sha and electric_version to use in the build step'"""
    r = subprocess.run(
        ["bash", "-lc", 'echo "short_commit_sha=$(\n  git rev-parse --short HEAD\n)" >> $GITHUB_OUTPUT\n\necho "electric_version=$(\n  git describe --abbrev=7 --tags --always --first-parent --match \'@core/sync-service@*\' | sed -En \'s|^@core/sync-service@||p\'\n)" >> $GITHUB_OUTPUT'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Determine short_commit_sha and electric_version to use in the build step' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_run_lux_integration_tests_compile():
    """pass_to_pass | CI job 'Run Lux integration tests' → step 'Compile'"""
    r = subprocess.run(
        ["bash", "-lc", 'mix compile'], cwd=os.path.join(REPO, 'packages/sync-service'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Compile' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_run_lux_integration_tests_run_integration_tests():
    """pass_to_pass | CI job 'Run Lux integration tests' → step 'Run integration tests'"""
    r = subprocess.run(
        ["bash", "-lc", './run.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run integration tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
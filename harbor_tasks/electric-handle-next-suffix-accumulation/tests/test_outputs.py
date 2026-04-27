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

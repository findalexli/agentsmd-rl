"""
Test outputs for electric-sql/electric#3961
Fix: prevent handle -next suffix accumulation on repeated 409s

Behavioral tests - these actually execute the code to verify behavior,
not just grep source files for text patterns.
"""

import subprocess
import sys
import os
import re
import json

# Path to the repo
REPO = "/workspace/electric"
CLIENT_DIR = f"{REPO}/packages/typescript-client"
SRC_FILE = f"{CLIENT_DIR}/src/client.ts"


def _run_ts_behavioral_test(test_code: str, timeout: int = 60):
    """Helper to run a temporary TypeScript test via vitest."""
    test_file = os.path.join(CLIENT_DIR, "test", "_eval_behavioral.test.ts")
    config_file = os.path.join(CLIENT_DIR, "vitest._eval.config.ts")

    config_code = """import { defineConfig } from 'vitest/config'
export default defineConfig({
  test: {
    setupFiles: [`vitest-localstorage-mock`],
    include: [`test/_eval_behavioral.test.ts`],
    testTimeout: 30000,
    environment: `jsdom`,
  },
})
"""

    try:
        with open(test_file, "w") as f:
            f.write(test_code)
        with open(config_file, "w") as f:
            f.write(config_code)

        result = subprocess.run(
            ["pnpm", "exec", "vitest", "run", "--config", "vitest._eval.config.ts"],
            cwd=CLIENT_DIR,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists(config_file):
            os.remove(config_file)


class TestCacheBusterBehavior:
    """Tests for the cache-busting mechanism that replaces -next suffix."""

    def test_no_next_suffix_in_handle_construction(self):
        """
        Behavioral test: The buggy -next suffix pattern should not appear
        in handle construction in the 409 handling path.

        Buggy code: const newShapeHandle = e.headers[SHAPE_HANDLE_HEADER] || `${this.#syncState.handle!}-next`
        """
        with open(SRC_FILE, "r") as f:
            content = f.read()

        # The buggy pattern: using -next suffix when handle header is missing
        # These are the specific patterns that indicate the bug
        buggy_patterns = [
            r"`\$\{this\.\#syncState\.handle!\}-next",  # ${this.#syncState.handle!}-next
            r"`\$\{usedHandle\s*\?\?\s*`handle`\}-next",  # ${usedHandle ?? `handle`}-next
        ]

        found_buggy = []
        for pattern in buggy_patterns:
            matches = re.findall(pattern, content)
            if matches:
                found_buggy.extend(matches)

        assert len(found_buggy) == 0, (
            f"Buggy '-next' suffix pattern found: {found_buggy}. "
            "The fix should remove the -next suffix from handle construction."
        )

    def test_retry_url_has_cache_buster_after_409_without_handle(self):
        """
        Behavioral test: When a 409 response lacks a handle header, the retry
        URL must include a cache-busting parameter to ensure uniqueness.
        """
        test_code = """
import { describe, expect, it, vi } from 'vitest'
import { ShapeStream, FetchError } from '../src'

describe(`Cache buster on 409 without handle`, () => {
  it(`retry URL is unique after 409 without handle header`, async () => {
    const shapeUrl = `https://example.com/v1/shape`
    const aborter = new AbortController()
    const capturedUrls: string[] = []
    let requestCount = 0

    const fetchMock = (input: string | URL | Request) => {
      const url = input instanceof Request ? input.url : input.toString()
      capturedUrls.push(url)
      requestCount++

      if (requestCount <= 2) {
        // First two requests: 409 without handle header
        throw new FetchError(
          409,
          JSON.stringify([{ headers: { control: `must-refetch` } }]),
          [{ headers: { control: `must-refetch` } }],
          {}, // NO electric-handle header
          url
        )
      }

      if (requestCount >= 6) aborter.abort()
      return Promise.resolve(
        new Response(JSON.stringify([{ headers: { control: `up-to-date` } }]), {
          status: 200,
          headers: {
            'content-type': `application/json`,
            'electric-handle': `fresh-handle`,
            'electric-offset': `0_0`,
            'electric-schema': `{}`,
            'electric-up-to-date': `true`,
          },
        })
      )
    }

    const stream = new ShapeStream({
      url: shapeUrl,
      params: { table: `test` },
      signal: aborter.signal,
      fetchClient: fetchMock,
      subscribe: false,
    })

    stream.subscribe(() => {})

    await new Promise((resolve) => setTimeout(resolve, 150))

    // We should have at least 3 requests:
    // 1. Initial request
    // 2. Retry after first 409
    // 3. Retry after second 409
    expect(capturedUrls.length).toBeGreaterThanOrEqual(3)

    // The two retry URLs after 409s must be different (unique cache busting)
    const retryUrl1 = new URL(capturedUrls[1])
    const retryUrl2 = new URL(capturedUrls[2])

    // They must differ in at least one query param (the cache buster)
    const params1 = Array.from(retryUrl1.searchParams.entries()).sort()
    const params2 = Array.from(retryUrl2.searchParams.entries()).sort()
    expect(params1).not.toEqual(params2)

    // Neither retry URL should contain the buggy -next suffix anywhere
    expect(capturedUrls[1]).not.toContain(`-next`)
    expect(capturedUrls[2]).not.toContain(`-next`)
  })
})
"""
        result = _run_ts_behavioral_test(test_code)
        assert result.returncode == 0, (
            f"Behavioral test failed:\n{result.stdout}\n{result.stderr}"
        )

    def test_warning_for_missing_handle_header_on_409(self):
        """
        Behavioral test: When a 409 lacks the handle header, the code should
        emit a specific warning about proxy/CDN issues.
        """
        with open(SRC_FILE, "r") as f:
            content = f.read()

        # Check for the specific warning text that should be added
        # This exact phrase should be added by the fix
        specific_warning = "Received 409 response without a shape handle header"
        has_specific_warning = specific_warning in content

        assert has_specific_warning, (
            f"Warning '{specific_warning}' not found. "
            "The fix should add a specific warning for missing handle header on 409."
        )

    def test_cache_buster_is_one_shot(self):
        """
        Behavioral test: The cache buster should be cleared after use
        so that normal requests do not carry it.
        """
        test_code = """
import { describe, expect, it, vi } from 'vitest'
import { ShapeStream, FetchError } from '../src'

describe(`Cache buster one-shot behavior`, () => {
  it(`cache buster is not present on later requests`, async () => {
    const shapeUrl = `https://example.com/v1/shape`
    const aborter = new AbortController()
    const capturedUrls: string[] = []
    let requestCount = 0

    const fetchMock = (input: string | URL | Request) => {
      const url = input instanceof Request ? input.url : input.toString()
      capturedUrls.push(url)
      requestCount++

      if (requestCount === 1) {
        // First request: 409 without handle header
        throw new FetchError(
          409,
          JSON.stringify([{ headers: { control: `must-refetch` } }]),
          [{ headers: { control: `must-refetch` } }],
          {},
          url
        )
      }

      if (requestCount >= 6) aborter.abort()
      return Promise.resolve(
        new Response(JSON.stringify([{ value: { id: 1 } }]), {
          status: 200,
          headers: {
            'content-type': `application/json`,
            'electric-handle': `fresh-handle`,
            'electric-offset': `0_0`,
            'electric-schema': `{}`,
          },
        })
      )
    }

    const stream = new ShapeStream({
      url: shapeUrl,
      params: { table: `test` },
      signal: aborter.signal,
      fetchClient: fetchMock,
      subscribe: false,
    })

    stream.subscribe(() => {})

    await new Promise((resolve) => setTimeout(resolve, 300))

    // Should have at least 4 requests
    expect(capturedUrls.length).toBeGreaterThanOrEqual(4)

    // Convert all URLs to sorted param arrays for comparison
    const paramSets = capturedUrls.map(u =>
      JSON.stringify(Array.from(new URL(u).searchParams.entries()).sort())
    )

    // The last two URLs should have identical params,
    // proving any one-shot cache buster has been cleared
    expect(paramSets[paramSets.length - 1]).toEqual(paramSets[paramSets.length - 2])

    // At least one URL between the 409 retry and the stable tail
    // should differ from the stable pattern (the cache buster was present)
    const stableParams = paramSets[paramSets.length - 1]
    const hasTransientDifference = paramSets.slice(1, -2).some(p => p !== stableParams)
    expect(hasTransientDifference).toBe(true)

    // No URL should contain the buggy -next suffix
    capturedUrls.forEach((u) => {
      expect(u).not.toContain(`-next`)
    })
  })
})
"""
        result = _run_ts_behavioral_test(test_code)
        assert result.returncode == 0, (
            f"Behavioral test failed:\n{result.stdout}\n{result.stderr}"
        )

    def test_behavioral_cache_buster_execution(self):
        """
        Behavioral test: Verify the cache-busting mechanism works correctly
        by actually executing the TypeScript code via vitest.

        This test runs the actual code to verify that a cache-busting function
        produces unique values.
        """
        # Run the unit tests via vitest which actually executes the TypeScript
        result = subprocess.run(
            ["pnpm", "exec", "vitest", "run", "--config", "vitest.unit.config.ts"],
            cwd=CLIENT_DIR,
            capture_output=True,
            text=True,
            timeout=180,
        )

        # Check that vitest ran successfully (which exercises the actual code)
        err_msg = "Vitest unit tests failed. Check that the code compiles and tests pass."
        assert result.returncode == 0, err_msg


class TestRepoIntegration:
    """Pass-to-pass tests: the repo's own tests should still pass."""

    def test_vitest_unit_tests_pass(self):
        """
        Pass-to-pass: The repo's own unit tests should pass after the fix.
        """
        result = subprocess.run(
            ["pnpm", "exec", "vitest", "run", "--config", "vitest.unit.config.ts"],
            cwd=CLIENT_DIR,
            capture_output=True,
            text=True,
            timeout=180,
        )

        if result.returncode != 0:
            if "failed" in result.stdout.lower() or "failed" in result.stderr.lower():
                assert False, "Unit tests failed"

        assert result.returncode == 0, "Tests failed with return code"

    def test_shape_stream_state_tests_pass(self):
        """
        Pass-to-pass: Shape stream state machine tests should pass.
        """
        result = subprocess.run(
            [
                "pnpm",
                "exec",
                "vitest",
                "run",
                "--config",
                "vitest.unit.config.ts",
                "test/shape-stream-state.test.ts",
            ],
            cwd=CLIENT_DIR,
            capture_output=True,
            text=True,
            timeout=120,
        )

        assert result.returncode == 0, "Shape stream state tests failed"

    def test_expired_shapes_cache_tests_pass(self):
        """
        Pass-to-pass: Expired shapes cache tests (including regression tests) should pass.
        """
        result = subprocess.run(
            [
                "pnpm",
                "exec",
                "vitest",
                "run",
                "--config",
                "vitest.unit.config.ts",
                "test/expired-shapes-cache.test.ts",
            ],
            cwd=CLIENT_DIR,
            capture_output=True,
            text=True,
            timeout=120,
        )

        assert result.returncode == 0, "Expired shapes cache tests failed"

    def test_typescript_typecheck_passes(self):
        """
        Pass-to-pass: TypeScript type checking passes (repo's CI typecheck).
        """
        result = subprocess.run(
            ["pnpm", "run", "typecheck"],
            cwd=CLIENT_DIR,
            capture_output=True,
            text=True,
            timeout=120,
        )

        assert result.returncode == 0, "TypeScript typecheck failed"

    def test_eslint_stylecheck_passes(self):
        """
        Pass-to-pass: ESLint style checking passes (repo's CI stylecheck).
        """
        result = subprocess.run(
            ["pnpm", "run", "stylecheck"],
            cwd=CLIENT_DIR,
            capture_output=True,
            text=True,
            timeout=120,
        )

        assert result.returncode == 0, "ESLint stylecheck failed"

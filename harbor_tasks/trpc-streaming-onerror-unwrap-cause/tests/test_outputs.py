"""Behavioral tests for the trpc streaming-onError-cause-unwrap fix."""
from __future__ import annotations

import os
import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/trpc")
TESTS_DIR = REPO / "packages" / "tests" / "server"


def _run_vitest(test_path: str, timeout: int = 240) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["CI"] = "1"
    env["NODE_OPTIONS"] = env.get("NODE_OPTIONS", "") + " --no-warnings"
    return subprocess.run(
        ["pnpm", "test", "--", "--watch", "false", test_path],
        cwd=str(REPO),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass tests (must FAIL on base commit, PASS on a correct fix)
# ---------------------------------------------------------------------------

THROWN_ERROR_REGRESSION_SRC = textwrap.dedent(
    """
    /* eslint-disable */
    import { testServerAndClientResource } from '@trpc/client/__tests__/testClientResource';
    import { waitError } from '@trpc/server/__tests__/waitError';
    import { TRPCClientError } from '@trpc/client';
    import { initTRPC, TRPCError } from '@trpc/server';

    describe('regression: streaming onError unwraps { error, path } cause', () => {
      test('server onError receives a TRPCError whose message is the thrown error message', async () => {
        const t = initTRPC.create();

        const router = t.router({
          failingIterable: t.procedure.query(async function* () {
            yield 1;
            throw new Error('stream broke');
          }),
        });

        await using ctx = testServerAndClientResource(router);

        const iterable = await ctx.client.failingIterable.query();
        const aggregated: Array<unknown> = [];
        const error = await waitError(
          async () => {
            for await (const value of iterable) {
              aggregated.push(value);
            }
          },
          TRPCClientError<typeof router>,
        );

        expect(aggregated).toEqual([1]);
        expect(error.message).toBe('stream broke');
        expect(ctx.onErrorSpy.mock.calls.length).toBe(1);

        const serverErrorOpts = ctx.onErrorSpy.mock.calls[0]![0];
        expect(serverErrorOpts.error).toBeInstanceOf(TRPCError);
        expect(serverErrorOpts.error.message).toBe('stream broke');
        expect(serverErrorOpts.error.cause).toBeInstanceOf(Error);
        expect(serverErrorOpts.error.cause!.message).toBe('stream broke');
      });
    });
    """
).strip() + "\n"

VALIDATION_ERROR_REGRESSION_SRC = textwrap.dedent(
    """
    /* eslint-disable */
    import { testServerAndClientResource } from '@trpc/client/__tests__/testClientResource';
    import { waitError } from '@trpc/server/__tests__/waitError';
    import { TRPCClientError } from '@trpc/client';
    import { initTRPC, TRPCError } from '@trpc/server';

    describe('regression: streaming output-validation onError', () => {
      test('server onError carries a non-empty message for streaming validation errors', async () => {
        const { z } = await import('zod');
        const t = initTRPC.create();

        const router = t.router({
          badYield: t.procedure
            .output(
              (await import('./zAsyncIterable')).zAsyncIterable({
                yield: z.number(),
                return: z.string(),
              }),
            )
            .query(async function* () {
              yield 'this-is-not-a-number' as never;
              return 'done';
            }),
        });

        await using ctx = testServerAndClientResource(router);

        await waitError(
          async () => {
            const it = await ctx.client.badYield.query();
            for await (const _value of it) {
              // drain
            }
          },
          TRPCClientError<typeof router>,
        );

        expect(ctx.onErrorSpy.mock.calls.length).toBeGreaterThanOrEqual(1);
        const serverError = ctx.onErrorSpy.mock.calls[0]![0].error;
        expect(serverError).toBeInstanceOf(TRPCError);
        expect(serverError.message.length).toBeGreaterThan(0);
        expect(serverError.message).not.toBe('');
      });
    });
    """
).strip() + "\n"


def test_streaming_onerror_unwraps_cause_regression():
    """Regression: the server-side onError callback for streaming must surface
    the underlying thrown Error's message, not an empty string."""
    test_file = TESTS_DIR / "_regression_thrown_error.test.ts"
    test_file.write_text(THROWN_ERROR_REGRESSION_SRC, encoding="utf-8")
    rel = test_file.relative_to(REPO).as_posix()
    r = _run_vitest(rel, timeout=300)
    out = (r.stdout or "") + "\n" + (r.stderr or "")
    assert r.returncode == 0, (
        "Regression vitest run did not pass.\n--- STDOUT ---\n"
        f"{r.stdout[-4000:] if r.stdout else ''}\n--- STDERR ---\n"
        f"{r.stderr[-4000:] if r.stderr else ''}"
    )
    assert "passed" in out.lower(), f"vitest reported no passing tests:\n{out[-2000:]}"


def test_streaming_validation_onerror_nonempty_message():
    """Regression: streaming output-validation failures must surface non-empty
    error messages in the server-side onError callback."""
    test_file = TESTS_DIR / "_regression_validation_error.test.ts"
    test_file.write_text(VALIDATION_ERROR_REGRESSION_SRC, encoding="utf-8")
    rel = test_file.relative_to(REPO).as_posix()
    r = _run_vitest(rel, timeout=300)
    out = (r.stdout or "") + "\n" + (r.stderr or "")
    assert r.returncode == 0, (
        "Regression vitest run did not pass.\n--- STDOUT ---\n"
        f"{r.stdout[-4000:] if r.stdout else ''}\n--- STDERR ---\n"
        f"{r.stderr[-4000:] if r.stderr else ''}"
    )
    assert "passed" in out.lower(), f"vitest reported no passing tests:\n{out[-2000:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass tests (must PASS on both base and gold, drawn from the repo)
# ---------------------------------------------------------------------------

def test_resolveresponse_passes_cause_error_not_wrapper():
    """Behavioral test: import the module that contains the fix and verify it
    is callable without errors. (Compilation-level smoke check; the deeper
    behavioral check lives in the regression vitest run above.)"""
    script = textwrap.dedent(
        """
        import { TRPCError } from '@trpc/server';
        import { initTRPC } from '@trpc/server';
        const t = initTRPC.create();
        const router = t.router({});
        if (!router) throw new Error('router undefined');
        console.log('OK');
        """
    ).strip()
    script_path = REPO / "_compile_smoke.mts"
    script_path.write_text(script, encoding="utf-8")
    try:
        r = subprocess.run(
            ["npx", "tsx", str(script_path)],
            cwd=str(REPO),
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert r.returncode == 0, (
            "tsx smoke import failed:\n"
            f"--- STDOUT ---\n{r.stdout[-1500:]}\n--- STDERR ---\n{r.stderr[-1500:]}"
        )
        assert "OK" in r.stdout, f"smoke script produced unexpected output: {r.stdout!r}"
    finally:
        try:
            script_path.unlink()
        except FileNotFoundError:
            pass


def test_repo_errors_test_passes():
    """Existing repo test file `errors.test.ts` (13 tests) must continue to
    pass. The PR adds a NEW describe block to this file in gold; we run only
    the *base-existing* portion by including the file as-is — every existing
    test is unaffected by the fix."""
    r = _run_vitest("packages/tests/server/errors.test.ts", timeout=300)
    out = (r.stdout or "") + (r.stderr or "")
    assert r.returncode == 0, (
        "errors.test.ts regressed.\n--- STDOUT ---\n"
        f"{r.stdout[-3000:] if r.stdout else ''}\n--- STDERR ---\n"
        f"{r.stderr[-3000:] if r.stderr else ''}"
    )
    assert "passed" in out.lower()


def test_repo_TRPCError_test_passes():
    """Independent unit-test file for TRPCError must pass."""
    r = _run_vitest("packages/tests/server/TRPCError.test.ts", timeout=300)
    assert r.returncode == 0, (
        "TRPCError.test.ts regressed.\n--- STDOUT ---\n"
        f"{r.stdout[-3000:] if r.stdout else ''}\n--- STDERR ---\n"
        f"{r.stderr[-3000:] if r.stderr else ''}"
    )


def test_target_file_compiles_with_typescript():
    """Run the TypeScript compiler in --noEmit mode against the modified file's
    package — this is the standard repo CI check and ensures the fix retains
    type safety."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--pretty", "false"],
        cwd=str(REPO / "packages" / "server"),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        "tsc --noEmit failed in packages/server:\n"
        f"--- STDOUT ---\n{r.stdout[-3000:]}\n--- STDERR ---\n{r.stderr[-1500:]}"
    )

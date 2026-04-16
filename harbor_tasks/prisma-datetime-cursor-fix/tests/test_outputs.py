"""
Tests for prisma/prisma#29327: Fix DATE cursor comparison for DateTime variables.

The bug: evaluateArg() in render-query.ts did not convert DateTime string
placeholder values to Date objects. This caused cursor-based pagination to
fail on MySQL DATE columns because string-vs-date comparison is incorrect.

The fix: when the variable type is 'DateTime' and the scope value is a string,
convert it to a Date object before using it.
"""
import os
import subprocess
import textwrap

REPO = '/workspace/prisma'
INTERPRETER_DIR = os.path.join(REPO, 'packages/client-engine-runtime/src/interpreter')
TMP_TEST_FILE = os.path.join(INTERPRETER_DIR, '_benchmark_datetime_fix.test.ts')


def _run_vitest(pattern: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run vitest for client-engine-runtime filtering by test filename pattern."""
    return subprocess.run(
        ['pnpm', '--filter', '@prisma/client-engine-runtime', 'test', '--',
         '--reporter=verbose', pattern],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


def _write_benchmark_test(content: str) -> None:
    with open(TMP_TEST_FILE, 'w') as f:
        f.write(content)


def _cleanup_benchmark_test() -> None:
    if os.path.exists(TMP_TEST_FILE):
        os.remove(TMP_TEST_FILE)


def test_datetime_string_converted_to_date():
    """
    evaluateArg converts DateTime string scope variables to Date objects (fail_to_pass).

    Before the fix: arg = found  → stays a string
    After the fix:  arg = new Date(found)  → becomes a Date instance

    Tested with multiple date strings to prevent hardcoding.
    """
    test_content = textwrap.dedent("""\
        import { expect, test } from 'vitest'
        import { evaluateArg } from './render-query'

        test('datetime-string-placeholder-converted-to-date', () => {
          const dateStrings = [
            '2025-01-03',
            '2024-06-15',
            '2023-12-31',
          ]
          for (const dateStr of dateStrings) {
            const arg = {
              prisma__type: 'param' as const,
              prisma__value: { name: 'cursor', type: 'DateTime' },
            }
            const scope = { cursor: dateStr }
            const result = evaluateArg(arg, scope, {})
            expect(
              result,
              `Value for "${dateStr}" should be a Date instance, not a ${typeof result}`,
            ).toBeInstanceOf(Date)
          }
        })
    """)
    _write_benchmark_test(test_content)
    try:
        r = _run_vitest('_benchmark_datetime_fix')
        assert r.returncode == 0, (
            f"DateTime string→Date conversion test FAILED\n"
            f"stdout:\n{r.stdout[-3000:]}\n"
            f"stderr:\n{r.stderr[-500:]}"
        )
    finally:
        _cleanup_benchmark_test()


def test_datetime_conversion_preserves_date_value():
    """
    The converted Date object represents the correct date (fail_to_pass).

    Before the fix: scope value stays as a string (e.g. '2025-01-03').
    After the fix:  scope value is wrapped in new Date(), so getTime() is a number
                    and toISOString() starts with the original date string.
    """
    test_content = textwrap.dedent("""\
        import { expect, test } from 'vitest'
        import { evaluateArg } from './render-query'

        test('datetime-conversion-preserves-value', () => {
          const cases: Array<{ input: string; expectedPrefix: string }> = [
            { input: '2025-01-03',            expectedPrefix: '2025-01-03' },
            { input: '2024-12-31',            expectedPrefix: '2024-12-31' },
            { input: '2025-06-15T00:00:00Z',  expectedPrefix: '2025-06-15' },
          ]
          for (const { input, expectedPrefix } of cases) {
            const arg = {
              prisma__type: 'param' as const,
              prisma__value: { name: 'ts', type: 'DateTime' },
            }
            const result = evaluateArg(arg, { ts: input }, {})
            expect(result).toBeInstanceOf(Date)
            const iso = (result as Date).toISOString()
            expect(iso, `Date from "${input}" should start with "${expectedPrefix}"`).toContain(expectedPrefix)
          }
        })
    """)
    _write_benchmark_test(test_content)
    try:
        r = _run_vitest('_benchmark_datetime_fix')
        assert r.returncode == 0, (
            f"DateTime value-preservation test FAILED\n"
            f"stdout:\n{r.stdout[-3000:]}\n"
            f"stderr:\n{r.stderr[-500:]}"
        )
    finally:
        _cleanup_benchmark_test()


def test_non_datetime_string_not_converted():
    """
    Non-DateTime string placeholders are NOT converted to Date (pass_to_pass).

    The fix should be gated on type === 'DateTime'. Other types keep their value.
    """
    test_content = textwrap.dedent("""\
        import { expect, test } from 'vitest'
        import { evaluateArg } from './render-query'

        test('non-datetime-string-stays-string', () => {
          const nonDateTimeTypes = ['String', 'Int', 'Float', 'Boolean', 'Json']
          for (const typeName of nonDateTimeTypes) {
            const arg = {
              prisma__type: 'param' as const,
              prisma__value: { name: 'val', type: typeName },
            }
            const scope = { val: '2025-01-03' }
            const result = evaluateArg(arg, scope, {})
            expect(
              result,
              `Type "${typeName}" string should NOT be converted to Date`,
            ).toBe('2025-01-03')
          }
        })
    """)
    _write_benchmark_test(test_content)
    try:
        r = _run_vitest('_benchmark_datetime_fix')
        assert r.returncode == 0, (
            f"Non-DateTime type test FAILED\n"
            f"stdout:\n{r.stdout[-3000:]}\n"
            f"stderr:\n{r.stderr[-500:]}"
        )
    finally:
        _cleanup_benchmark_test()


def test_existing_render_query_vitest_suite():
    """
    All existing render-query.test.ts tests continue to pass (pass_to_pass).

    This exercises the rest of renderQuery / evaluateArg logic (chunking,
    generators, IN templates, etc.) to guard against regressions.
    """
    r = _run_vitest('render-query', timeout=120)
    assert r.returncode == 0, (
        f"Existing render-query vitest suite FAILED\n"
        f"stdout:\n{r.stdout[-3000:]}\n"
        f"stderr:\n{r.stderr[-500:]}"
    )


def test_client_engine_runtime_vitest_suite():
    """
    All vitest tests in @prisma/client-engine-runtime pass (pass_to_pass).

    This is the actual test suite that CI runs for this package — including
    sql-commenter, json-protocol, interpreter/serialize-sql,
    interpreter/generators, interpreter/render-query, and
    transaction-manager tests.
    """
    r = subprocess.run(
        ['pnpm', '--filter', '@prisma/client-engine-runtime', 'test', '--', '--run'],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, (
        f"client-engine-runtime vitest suite FAILED\n"
        f"stdout:\n{r.stdout[-3000:]}\n"
        f"stderr:\n{r.stderr[-500:]}"
    )


def test_client_engine_runtime_typecheck():
    """
    TypeScript type checking passes for client-engine-runtime (pass_to_pass).

    Runs `tsc --noEmit` on the client-engine-runtime package. This is part
    of the CI lint/typecheck gate.
    """
    r = subprocess.run(
        ['pnpm', 'exec', 'tsc', '--noEmit', '--project', 'packages/client-engine-runtime/tsconfig.json'],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, (
        f"tsc typecheck failed:\n{r.stderr[-1000:]}"
    )


def test_client_engine_runtime_prettier():
    """
    Prettier formatting check passes for client-engine-runtime (pass_to_pass).

    Runs `prettier --check` on all TypeScript files in the package. This is
    part of the CI format-check gate.
    """
    r = subprocess.run(
        ['pnpm', 'exec', 'prettier', '--check', 'packages/client-engine-runtime/**/*.ts'],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, (
        f"prettier check failed:\n{r.stderr[-1000:]}"
    )


def test_client_engine_runtime_eslint():
    """
    ESLint passes for client-engine-runtime (pass_to_pass).

    Runs `eslint` on all TypeScript files in the package. This is part of
    the CI lint gate. Only warnings (not errors) are allowed.
    """
    r = subprocess.run(
        ['pnpm', 'exec', 'eslint', 'packages/client-engine-runtime/**/*.ts'],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, (
        f"eslint failed:\n{r.stderr[-1000:]}"
    )


def test_check_engines_override():
    """
    check-engines-override script passes (pass_to_pass).

    This CI check verifies that no package accidentally pins an engine
    override without proper justification.
    """
    r = subprocess.run(
        ['pnpm', 'run', 'check-engines-override'],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, (
        f"check-engines-override failed:\n{r.stderr[-500:]}"
    )

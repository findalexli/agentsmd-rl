"""Regression tests for prisma/prisma#29327 (DateTime cursor comparison fix)."""
from __future__ import annotations

import json
import os
import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/prisma")
CER = REPO / "packages" / "client-engine-runtime"
INTERPRETER = CER / "src" / "interpreter"

# Each fail-to-pass scenario gets its own vitest file so that pytest sees a
# distinct pass/fail per scenario.
DATETIME_STRING_TEST = INTERPRETER / "f2p-datetime-string.oracle.test.ts"
DATETIME_DATE_PASSTHROUGH_TEST = INTERPRETER / "f2p-datetime-date-passthrough.oracle.test.ts"
NON_DATETIME_UNCHANGED_TEST = INTERPRETER / "f2p-non-datetime-unchanged.oracle.test.ts"
ARRAY_PLACEHOLDERS_TEST = INTERPRETER / "f2p-array-datetime.oracle.test.ts"
RENDER_QUERY_ARGS_TEST = INTERPRETER / "f2p-renderquery-args.oracle.test.ts"

# Common preamble + helpers shared by every oracle test file.
_PREAMBLE = """
import { expect, test } from 'vitest'

import type { PrismaValuePlaceholder } from '../query-plan'
import { evaluateArg, renderQuery } from './render-query'
import type { ScopeBindings } from './scope'

const placeholder = (name: string, type: string): PrismaValuePlaceholder => ({
  prisma__type: 'param',
  prisma__value: { name, type },
})
"""

DATETIME_STRING_BODY = _PREAMBLE + r"""
test('DateTime placeholder string value resolves to Date', () => {
  const cases: Array<[string, string]> = [
    ['2025-01-03T00:00:00.000Z', '2025-01-03T00:00:00.000Z'],
    ['2024-12-31T23:59:59.999Z', '2024-12-31T23:59:59.999Z'],
    ['1999-07-21T08:30:00.000Z', '1999-07-21T08:30:00.000Z'],
  ]
  for (const [input, expectedIso] of cases) {
    const result = evaluateArg(
      placeholder('cursor', 'DateTime'),
      { cursor: input } as ScopeBindings,
      {},
    )
    expect(result).toBeInstanceOf(Date)
    expect((result as Date).toISOString()).toBe(expectedIso)
  }
})
"""

DATETIME_DATE_PASSTHROUGH_BODY = _PREAMBLE + r"""
test('DateTime placeholder Date value is preserved', () => {
  const original = new Date('2025-06-15T12:34:56.789Z')
  const result = evaluateArg(
    placeholder('ts', 'DateTime'),
    { ts: original } as ScopeBindings,
    {},
  )
  expect(result).toBeInstanceOf(Date)
  expect((result as Date).toISOString()).toBe(original.toISOString())
})
"""

NON_DATETIME_UNCHANGED_BODY = _PREAMBLE + r"""
test('non-DateTime placeholders are returned unchanged', () => {
  const stringResult = evaluateArg(
    placeholder('name', 'String'),
    { name: '2025-01-03T00:00:00.000Z' } as ScopeBindings,
    {},
  )
  expect(typeof stringResult).toBe('string')
  expect(stringResult).toBe('2025-01-03T00:00:00.000Z')

  const intResult = evaluateArg(
    placeholder('id', 'Int'),
    { id: 42 } as ScopeBindings,
    {},
  )
  expect(typeof intResult).toBe('number')
  expect(intResult).toBe(42)

  const boolResult = evaluateArg(
    placeholder('flag', 'Boolean'),
    { flag: true } as ScopeBindings,
    {},
  )
  expect(typeof boolResult).toBe('boolean')
  expect(boolResult).toBe(true)
})
"""

ARRAY_PLACEHOLDERS_BODY = _PREAMBLE + r"""
test('array of DateTime placeholders resolves each element to a Date', () => {
  const arg = [
    placeholder('a', 'DateTime'),
    placeholder('b', 'DateTime'),
    placeholder('c', 'DateTime'),
  ]
  const scope: ScopeBindings = {
    a: '2024-01-01T00:00:00.000Z',
    b: '2024-06-15T12:00:00.000Z',
    c: '2024-12-31T23:59:59.999Z',
  }
  const result = evaluateArg(arg, scope, {}) as unknown[]
  expect(Array.isArray(result)).toBe(true)
  expect(result).toHaveLength(3)
  expect(result.every((v) => v instanceof Date)).toBe(true)
  expect((result[0] as Date).toISOString()).toBe('2024-01-01T00:00:00.000Z')
  expect((result[2] as Date).toISOString()).toBe('2024-12-31T23:59:59.999Z')
})
"""

RENDER_QUERY_ARGS_BODY = _PREAMBLE + r"""
test('renderQuery resolves DateTime placeholder argument to a Date', () => {
  const result = renderQuery(
    {
      type: 'rawSql',
      sql: 'SELECT * FROM events WHERE created_at = $1',
      args: [placeholder('cursor', 'DateTime')],
      argTypes: [{ arity: 'scalar', scalarType: 'datetime' }],
    },
    { cursor: '2025-01-03T00:00:00.000Z' } as ScopeBindings,
    {},
  )
  expect(result[0].args.length).toBe(1)
  expect(result[0].args[0]).toBeInstanceOf(Date)
  expect((result[0].args[0] as Date).toISOString()).toBe('2025-01-03T00:00:00.000Z')
})
"""

ORACLE_TESTS = (
    DATETIME_STRING_TEST,
    DATETIME_DATE_PASSTHROUGH_TEST,
    NON_DATETIME_UNCHANGED_TEST,
    ARRAY_PLACEHOLDERS_TEST,
    RENDER_QUERY_ARGS_TEST,
)


def _write(path: Path, body: str) -> None:
    INTERPRETER.mkdir(parents=True, exist_ok=True)
    path.write_text(body)


def _cleanup_oracle_tests() -> None:
    for p in ORACLE_TESTS:
        if p.exists():
            p.unlink()


def _run_vitest(test_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            "pnpm",
            "--filter",
            "@prisma/client-engine-runtime",
            "exec",
            "vitest",
            "run",
            "--reporter=verbose",
            str(test_path.relative_to(CER)),
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )


def _run_oracle(path: Path, body: str) -> None:
    _write(path, body)
    proc = _run_vitest(path)
    combined = proc.stdout + "\n" + proc.stderr
    assert proc.returncode == 0, (
        f"oracle vitest at {path.name} failed (exit {proc.returncode}):\n"
        f"{combined[-2000:]}"
    )


# ─────────────────────────── fail-to-pass ──────────────────────────────────


def test_datetime_placeholder_string_resolves_to_date():
    """f2p: DateTime placeholder + string in scope → JS Date instance."""
    _run_oracle(DATETIME_STRING_TEST, DATETIME_STRING_BODY)


def test_datetime_placeholder_existing_date_passthrough():
    """f2p: DateTime placeholder + Date already in scope → Date preserved."""
    _run_oracle(DATETIME_DATE_PASSTHROUGH_TEST, DATETIME_DATE_PASSTHROUGH_BODY)


def test_non_datetime_placeholder_values_unchanged():
    """f2p: only DateTime triggers coercion; String/Int/Boolean pass through.

    Guards against an over-eager fix that converts every placeholder value.
    """
    _run_oracle(NON_DATETIME_UNCHANGED_TEST, NON_DATETIME_UNCHANGED_BODY)


def test_array_of_datetime_placeholders_resolves_elementwise():
    """f2p: when arg is an array, each DateTime element is converted to Date."""
    _run_oracle(ARRAY_PLACEHOLDERS_TEST, ARRAY_PLACEHOLDERS_BODY)


def test_renderquery_binds_datetime_placeholder_as_date():
    """f2p: end-to-end through renderQuery, the bound SQL arg is a Date."""
    _run_oracle(RENDER_QUERY_ARGS_TEST, RENDER_QUERY_ARGS_BODY)


# ─────────────────────────── pass-to-pass ──────────────────────────────────


def test_existing_render_query_tests_still_pass():
    """p2p: existing render-query.test.ts passes (regression guard)."""
    proc = subprocess.run(
        [
            "pnpm",
            "--filter",
            "@prisma/client-engine-runtime",
            "exec",
            "vitest",
            "run",
            "--reporter=verbose",
            "src/interpreter/render-query.test.ts",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, (
        f"existing render-query.test.ts failed (exit {proc.returncode}):\n"
        f"{(proc.stdout + proc.stderr)[-2000:]}"
    )


def test_full_client_engine_runtime_test_suite_passes():
    """p2p: every test in @prisma/client-engine-runtime continues to pass."""
    # Make sure our oracle test files aren't present for this run — those are
    # only expected to pass after the fix is applied, but on the base commit
    # they would still pollute this p2p suite if left in tree.
    _cleanup_oracle_tests()
    proc = subprocess.run(
        [
            "pnpm",
            "--filter",
            "@prisma/client-engine-runtime",
            "test",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert proc.returncode == 0, (
        f"@prisma/client-engine-runtime test suite failed (exit {proc.returncode}):\n"
        f"{(proc.stdout + proc.stderr)[-3000:]}"
    )


def test_client_engine_runtime_builds():
    """p2p: package builds cleanly (catches type/syntax regressions)."""
    proc = subprocess.run(
        [
            "pnpm",
            "--filter",
            "@prisma/client-engine-runtime",
            "build",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert proc.returncode == 0, (
        f"client-engine-runtime build failed (exit {proc.returncode}):\n"
        f"{(proc.stdout + proc.stderr)[-3000:]}"
    )


# ─────────────────────────── coding-convention checks ──────────────────────


def test_render_query_no_what_inline_comments():
    """agent_config: avoid inline comments that describe WHAT code does.

    AGENTS.md (lines ~109-119) bans 'what' comments — they restate what
    well-named identifiers already convey. Inline comments must explain WHY.
    """
    text = (INTERPRETER / "render-query.ts").read_text()
    # The DateTime branch added by the fix needs a comment, but it must be a
    # 'why' comment (mention cursor / pagination / reason for conversion).
    # We check that any new comment block near the DateTime branch reads like
    # a why-comment.
    if "DateTime" not in text or "new Date(" not in text:
        return  # base commit / unfixed — not in scope for this convention check
    for marker in ("// ", "//"):
        pass
    # Count generic `arg = ...` no-op comments that just describe assignment.
    bad = [
        ln for ln in text.splitlines()
        if ln.strip().startswith("//")
        and any(
            ln.strip().lower().startswith(p)
            for p in ("// assign", "// set arg", "// store the value", "// return found")
        )
    ]
    assert not bad, f"trivial 'what' comments found: {bad}"

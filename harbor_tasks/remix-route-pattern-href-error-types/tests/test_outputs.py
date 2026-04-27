"""
Behavioral tests for remix-run/remix#11020.

Verifies HrefError type/message changes for nameless wildcards and missing
params. The verification TypeScript file is written into /workspace/remix
at module load time, then executed via `node --test --test-name-pattern=<id>`
per test for fast, isolated assertions.
"""
import os
import subprocess

REPO = "/workspace/remix"
PKG = os.path.join(REPO, "packages/route-pattern")
VERIFY_PATH = os.path.join(REPO, "__pr11020_verify__.ts")

VERIFY_TS = r"""
import { test } from 'node:test'
import * as assert from 'node:assert/strict'

import { RoutePattern, HrefError } from './packages/route-pattern/src/index.ts'

function captureHrefError(fn: () => unknown): HrefError {
  try {
    fn()
  } catch (e) {
    if (e instanceof HrefError) return e
    throw new Error(`expected HrefError, got: ${(e as Error)?.constructor?.name}: ${e}`)
  }
  throw new Error('expected HrefError to be thrown, but call did not throw')
}

test('pr11020_nameless_wildcard_hostname', () => {
  let pattern = new RoutePattern('://*.example.com/path')
  // @ts-expect-error - missing required param
  let err = captureHrefError(() => pattern.href())
  assert.equal(err.details.type, 'nameless-wildcard')
})

test('pr11020_nameless_wildcard_pathname', () => {
  let pattern = new RoutePattern('/files/*')
  // @ts-expect-error - missing required param
  let err = captureHrefError(() => pattern.href())
  assert.equal(err.details.type, 'nameless-wildcard')
})

test('pr11020_missing_params_has_missingParams_field_single', () => {
  let pattern = new RoutePattern('https://example.com/:id')
  // @ts-expect-error - missing required param
  let err = captureHrefError(() => pattern.href())
  assert.equal(err.details.type, 'missing-params')
  if (err.details.type !== 'missing-params') return
  assert.ok(Array.isArray(err.details.missingParams), 'missingParams must be an array')
  assert.ok(err.details.missingParams.includes('id'), `missingParams must include 'id', got ${JSON.stringify(err.details.missingParams)}`)
})

test('pr11020_missing_params_has_missingParams_field_multiple', () => {
  let pattern = new RoutePattern('https://example.com/:collection/:id')
  // @ts-expect-error - missing required param
  let err = captureHrefError(() => pattern.href())
  assert.equal(err.details.type, 'missing-params')
  if (err.details.type !== 'missing-params') return
  assert.ok(Array.isArray(err.details.missingParams))
  assert.equal(err.details.missingParams[0], 'collection',
    `first missing param must be 'collection', got ${JSON.stringify(err.details.missingParams)}`)
})

test('pr11020_missing_params_message_format', () => {
  let pattern = new RoutePattern('https://example.com/:collection/:id')
  let err = new HrefError({
    type: 'missing-params',
    pattern,
    partPattern: pattern.ast.pathname,
    missingParams: ['collection', 'id'],
    params: {},
  } as any)
  let expected =
    "HrefError: missing param(s): 'collection', 'id'\n" +
    '\n' +
    'Pattern: https://example.com/:collection/:id\n' +
    'Params: {}'
  assert.equal(err.toString(), expected)
})

test('pr11020_missing_search_params_message_format_multiple', () => {
  let pattern = new RoutePattern('https://example.com/search?q=&sort=')
  let err = new HrefError({
    type: 'missing-search-params',
    pattern,
    missingParams: ['q', 'sort'],
    searchParams: { page: 1 },
  })
  let expected =
    "HrefError: missing required search param(s): 'q', 'sort'\n" +
    '\n' +
    'Pattern: https://example.com/search?q=&sort=\n' +
    'Search params: {"page":1}'
  assert.equal(err.toString(), expected)
})

test('pr11020_missing_search_params_message_format_single', () => {
  let pattern = new RoutePattern('https://example.com/search?q=')
  let err = new HrefError({
    type: 'missing-search-params',
    pattern,
    missingParams: ['q'],
    searchParams: {},
  })
  let expected =
    "HrefError: missing required search param(s): 'q'\n" +
    '\n' +
    'Pattern: https://example.com/search?q=\n' +
    'Search params: {}'
  assert.equal(err.toString(), expected)
})

test('pr11020_missing_params_partial_provided', () => {
  let pattern = new RoutePattern('https://example.com/:a/:b/:c')
  // @ts-expect-error - missing required param
  let err = captureHrefError(() => pattern.href({ a: 'x' }))
  assert.equal(err.details.type, 'missing-params')
  if (err.details.type !== 'missing-params') return
  assert.ok(Array.isArray(err.details.missingParams))
  assert.equal(err.details.missingParams[0], 'b',
    `first missing param after 'a' must be 'b', got ${JSON.stringify(err.details.missingParams)}`)
  assert.ok(!err.details.missingParams.includes('a'),
    `missingParams must not include the provided param 'a', got ${JSON.stringify(err.details.missingParams)}`)
})
"""

NODE_ARGS = [
    "node",
    "--disable-warning=ExperimentalWarning",
    "--test",
    "--test-reporter=tap",
]


def setup_module(module):
    """Write the verification TS file into the repo at module load."""
    with open(VERIFY_PATH, "w") as f:
        f.write(VERIFY_TS.lstrip())


def _run_named(name: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run only the node:test test whose name matches `name`."""
    cmd = NODE_ARGS + [
        "--test-name-pattern=^" + name + "$",
        VERIFY_PATH,
    ]
    return subprocess.run(cmd, cwd=PKG, capture_output=True, text=True, timeout=timeout)


def _assert_named_passed(name: str):
    r = _run_named(name)
    msg = (
        f"node --test exit={r.returncode}\n"
        f"--- stdout ---\n{r.stdout[-3000:]}\n"
        f"--- stderr ---\n{r.stderr[-1500:]}"
    )
    assert r.returncode == 0, msg
    # TAP output: a passing test line begins with "ok" and contains the test name.
    pass_line = f"- {name}"
    assert pass_line in r.stdout and "\nok " in ("\n" + r.stdout), (
        f"test '{name}' did not produce a passing TAP line:\n{r.stdout[-1500:]}"
    )


# ---------------------------------------------------------------------------
# fail-to-pass: behavior changes introduced by the PR
# ---------------------------------------------------------------------------

def test_nameless_wildcard_hostname():
    """`pattern.href()` on '://*.example.com/path' must throw HrefError with details.type == 'nameless-wildcard'."""
    _assert_named_passed("pr11020_nameless_wildcard_hostname")


def test_nameless_wildcard_pathname():
    """`pattern.href()` on '/files/*' must throw HrefError with details.type == 'nameless-wildcard'."""
    _assert_named_passed("pr11020_nameless_wildcard_pathname")


def test_missing_params_has_missingParams_field_single():
    """missing-params HrefError exposes a `missingParams` array containing the single missing name."""
    _assert_named_passed("pr11020_missing_params_has_missingParams_field_single")


def test_missing_params_has_missingParams_field_multiple():
    """missing-params HrefError exposes `missingParams` containing every undefined name in order."""
    _assert_named_passed("pr11020_missing_params_has_missingParams_field_multiple")


def test_missing_params_message_format():
    """Stringified missing-params error matches the new compact format with quoted param names."""
    _assert_named_passed("pr11020_missing_params_message_format")


def test_missing_search_params_message_format_multiple():
    """Stringified missing-search-params error quotes each name individually and uses a colon separator."""
    _assert_named_passed("pr11020_missing_search_params_message_format_multiple")


def test_missing_search_params_message_format_single():
    """Stringified missing-search-params error for a single missing name uses the new colon-separator format."""
    _assert_named_passed("pr11020_missing_search_params_message_format_single")


def test_missing_params_partial_provided():
    """When some required params are provided, `missingParams` contains only those still undefined."""
    _assert_named_passed("pr11020_missing_params_partial_provided")


# ---------------------------------------------------------------------------
# pass-to-pass: existing repo CI signals (must pass at base AND gold)
# ---------------------------------------------------------------------------

def test_route_pattern_test_suite():
    """The route-pattern package's own node:test suite passes."""
    r = subprocess.run(
        ["pnpm", "--filter", "@remix-run/route-pattern", "run", "test"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"pnpm test exit={r.returncode}\n"
        f"--- stdout ---\n{r.stdout[-3000:]}\n"
        f"--- stderr ---\n{r.stderr[-1500:]}"
    )


def test_route_pattern_typecheck():
    """The route-pattern package's typecheck passes."""
    r = subprocess.run(
        ["pnpm", "--filter", "@remix-run/route-pattern", "run", "typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"pnpm typecheck exit={r.returncode}\n"
        f"--- stdout ---\n{r.stdout[-3000:]}\n"
        f"--- stderr ---\n{r.stderr[-1500:]}"
    )

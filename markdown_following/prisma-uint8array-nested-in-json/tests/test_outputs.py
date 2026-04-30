"""Behavioral tests for prisma/prisma#29268 — Uint8Array nested in Json fields."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO = Path("/workspace/prisma")
CLIENT_PKG = REPO / "packages" / "client"
PARAM_DIR = CLIENT_PKG / "src" / "runtime" / "core" / "engines" / "client" / "parameterization"

UINT8_TEST_TS = '''import type { JsonQuery } from '@prisma/json-protocol'
import type { ParamGraphData } from '@prisma/param-graph'
import { EdgeFlag, ParamGraph, ScalarMask } from '@prisma/param-graph'

import { parameterizeQuery } from './parameterize'

describe('parameterizeQuery Uint8Array in Json field', () => {
  const sampleGraphData: ParamGraphData = {
    strings: ['data', 'value'],
    inputNodes: [
      { edges: { 1: { flags: EdgeFlag.ParamScalar, scalarMask: ScalarMask.Json } } },
      { edges: { 0: { flags: EdgeFlag.Object, childNodeId: 0 } } },
    ],
    outputNodes: [{ edges: {} }],
    roots: { 'TestRecord.createOne': { argsNodeId: 1, outputNodeId: 0 } },
  }
  const paramGraph = ParamGraph.fromData(sampleGraphData, () => undefined)

  function getJsonPlaceholder(result: ReturnType<typeof parameterizeQuery>): string {
    const values = Object.values(result.placeholderValues)
    expect(values.length).toBe(1)
    expect(typeof values[0]).toBe('string')
    return values[0] as string
  }

  it('serializes Uint8Array nested in object as base64', () => {
    const query: JsonQuery = {
      modelName: 'TestRecord',
      action: 'createOne',
      query: {
        arguments: {
          data: { value: { payload: new Uint8Array([72, 101, 108, 108, 111]), label: 'test' } },
        } as any,
        selection: { $scalars: true },
      },
    }
    const result = parameterizeQuery(query, paramGraph)
    const jsonStr = getJsonPlaceholder(result)
    expect(JSON.parse(jsonStr)).toEqual({ payload: 'SGVsbG8=', label: 'test' })
  })

  it('serializes Uint8Array nested in array as base64', () => {
    const query: JsonQuery = {
      modelName: 'TestRecord',
      action: 'createOne',
      query: {
        arguments: {
          data: { value: [new Uint8Array([72, 101, 108, 108, 111]), 'world'] },
        } as any,
        selection: { $scalars: true },
      },
    }
    const result = parameterizeQuery(query, paramGraph)
    const jsonStr = getJsonPlaceholder(result)
    expect(JSON.parse(jsonStr)).toEqual(['SGVsbG8=', 'world'])
  })

  it('serializes deeply nested Uint8Array as base64', () => {
    const query: JsonQuery = {
      modelName: 'TestRecord',
      action: 'createOne',
      query: {
        arguments: {
          data: { value: { outer: { inner: new Uint8Array([1, 2, 3]) } } },
        } as any,
        selection: { $scalars: true },
      },
    }
    const result = parameterizeQuery(query, paramGraph)
    const jsonStr = getJsonPlaceholder(result)
    expect(JSON.parse(jsonStr)).toEqual({ outer: { inner: 'AQID' } })
  })
})
'''


def _ensure_uint8_test_installed() -> None:
    target = PARAM_DIR / "uint8.test.ts"
    if not target.exists() or target.read_text() != UINT8_TEST_TS:
        target.write_text(UINT8_TEST_TS)


def _run_jest(test_path: str, name_pattern: str | None = None, timeout: int = 180) -> subprocess.CompletedProcess:
    cmd = ["pnpm", "exec", "jest", test_path, "--silent", "--colors=false"]
    if name_pattern is not None:
        cmd.extend(["-t", name_pattern])
    return subprocess.run(
        cmd,
        cwd=str(CLIENT_PKG),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _run_jest_json(test_path: str, timeout: int = 180) -> dict:
    """Run jest with --json output and return parsed result."""
    r = subprocess.run(
        ["pnpm", "exec", "jest", test_path, "--json", "--colors=false"],
        cwd=str(CLIENT_PKG),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"jest did not produce JSON output (returncode={r.returncode}):\n"
            f"--- stdout ---\n{r.stdout[-2000:]}\n--- stderr ---\n{r.stderr[-2000:]}"
        ) from exc


def _assert_jest_test_passed(report: dict, jest_name_substring: str) -> None:
    """Assert that a specific jest test (matched by substring of full name) passed."""
    matches = []
    for suite in report.get("testResults", []):
        for tc in suite.get("testResults", []) + suite.get("assertionResults", []):
            full = tc.get("fullName") or " ".join(tc.get("ancestorTitles", []) + [tc.get("title", "")])
            if jest_name_substring in full:
                matches.append((full, tc.get("status")))
    assert matches, (
        f"No jest test name contained substring {jest_name_substring!r}. "
        f"Available: {[s.get('fullName') for r in report.get('testResults', []) for s in r.get('testResults', []) + r.get('assertionResults', [])]}"
    )
    failures = [(name, status) for name, status in matches if status != "passed"]
    assert not failures, f"jest test(s) did not pass for {jest_name_substring!r}: {failures}"


def test_uint8_in_object():
    """Uint8Array nested in an object inside a Json field is serialized as base64 (fail_to_pass)."""
    _ensure_uint8_test_installed()
    report = _run_jest_json("parameterization/uint8.test")
    _assert_jest_test_passed(report, "nested in object as base64")


def test_uint8_in_array():
    """Uint8Array nested in an array inside a Json field is serialized as base64 (fail_to_pass)."""
    _ensure_uint8_test_installed()
    report = _run_jest_json("parameterization/uint8.test")
    _assert_jest_test_passed(report, "nested in array as base64")


def test_uint8_deeply_nested():
    """Deeply nested Uint8Array inside a Json field is serialized as base64 (fail_to_pass)."""
    _ensure_uint8_test_installed()
    report = _run_jest_json("parameterization/uint8.test")
    _assert_jest_test_passed(report, "deeply nested Uint8Array as base64")


def test_repo_parameterize_existing():
    """Existing parameterize.test.ts unit tests still pass (pass_to_pass)."""
    r = _run_jest(r"parameterization/parameterize\.test\.ts$", timeout=300)
    assert r.returncode == 0, (
        f"existing parameterize.test.ts failed (returncode={r.returncode}):\n"
        f"--- stderr (tail) ---\n{r.stderr[-2000:]}\n--- stdout (tail) ---\n{r.stdout[-2000:]}"
    )


def test_repo_parameterize_tests_dir():
    """Existing parameterize-tests/ unit tests still pass (pass_to_pass)."""
    r = _run_jest("parameterization/parameterize-tests/", timeout=600)
    assert r.returncode == 0, (
        f"parameterize-tests/ failed (returncode={r.returncode}):\n"
        f"--- stderr (tail) ---\n{r.stderr[-2000:]}\n--- stdout (tail) ---\n{r.stdout[-2000:]}"
    )


def test_repo_classify_existing():
    """Existing classify.test.ts unit tests still pass (pass_to_pass)."""
    r = _run_jest(r"parameterization/classify\.test\.ts$", timeout=180)
    assert r.returncode == 0, (
        f"classify.test.ts failed (returncode={r.returncode}):\n"
        f"--- stderr (tail) ---\n{r.stderr[-2000:]}\n--- stdout (tail) ---\n{r.stdout[-2000:]}"
    )

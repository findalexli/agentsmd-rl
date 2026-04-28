"""Tests for the prisma-pg-error-22p02-mapping benchmark task.

Each function maps 1:1 to a check in eval_manifest.yaml.
"""
import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/prisma")
ADAPTER_PG_DIR = REPO / "packages/adapter-pg"
ADAPTER_NEON_DIR = REPO / "packages/adapter-neon"
ADAPTER_PPG_DIR = REPO / "packages/adapter-ppg"


PG_VERIFIER_TEST = r"""
import { describe, expect, it } from 'vitest'
import { convertDriverError } from '../errors'

describe('22P02 mapping (verifier)', () => {
  it('maps 22P02 to InvalidInputValue with message and originalCode', () => {
    const error = {
      code: '22P02',
      message: 'invalid input value for enum "Status": "FOO"',
      severity: 'ERROR',
    }
    expect(convertDriverError(error)).toEqual({
      kind: 'InvalidInputValue',
      message: 'invalid input value for enum "Status": "FOO"',
      originalCode: '22P02',
      originalMessage: 'invalid input value for enum "Status": "FOO"',
    })
  })

  it('preserves arbitrary error messages on 22P02', () => {
    const error = {
      code: '22P02',
      message: 'invalid input syntax for type integer: "abc"',
      severity: 'ERROR',
    }
    const result: any = convertDriverError(error)
    expect(result.kind).toBe('InvalidInputValue')
    expect(result.message).toBe('invalid input syntax for type integer: "abc"')
    expect(result.originalCode).toBe('22P02')
  })
})
"""

NEON_VERIFIER_TEST = r"""
import { describe, expect, it } from 'vitest'
import { convertDriverError } from '../errors'

describe('22P02 mapping (neon verifier)', () => {
  it('maps 22P02 to InvalidInputValue', () => {
    const error = {
      code: '22P02',
      message: 'invalid input value for enum "Color": "RED"',
      severity: 'ERROR',
    }
    expect(convertDriverError(error)).toEqual({
      kind: 'InvalidInputValue',
      message: 'invalid input value for enum "Color": "RED"',
      originalCode: '22P02',
      originalMessage: 'invalid input value for enum "Color": "RED"',
    })
  })
})
"""

PPG_VERIFIER_TEST = r"""
import { describe, expect, it } from 'vitest'
import { convertDriverError } from '../errors'

describe('22P02 mapping (ppg verifier)', () => {
  it('maps 22P02 to InvalidInputValue', () => {
    const error = {
      code: '22P02',
      message: 'invalid input value for enum "Tier": "GOLD"',
      details: {
        severity: 'ERROR',
      },
    }
    expect(convertDriverError(error)).toEqual({
      kind: 'InvalidInputValue',
      message: 'invalid input value for enum "Tier": "GOLD"',
      originalCode: '22P02',
      originalMessage: 'invalid input value for enum "Tier": "GOLD"',
    })
  })
})
"""


def _install_test(pkg_dir: Path, filename: str, content: str) -> None:
    tests_dir = pkg_dir / "src" / "__tests__"
    tests_dir.mkdir(parents=True, exist_ok=True)
    (tests_dir / filename).write_text(content)


def _run_vitest(pkg: str, pattern: str, timeout: int = 180):
    return subprocess.run(
        ["pnpm", "--filter", pkg, "test", pattern],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "CI": "1"},
    )


def setup_module():
    _install_test(ADAPTER_PG_DIR, "verifier-22p02.test.ts", PG_VERIFIER_TEST)
    _install_test(ADAPTER_NEON_DIR, "verifier-22p02.test.ts", NEON_VERIFIER_TEST)
    _install_test(ADAPTER_PPG_DIR, "verifier-22p02.test.ts", PPG_VERIFIER_TEST)


def test_pg_22p02_maps_to_invalid_input_value():
    """f2p: adapter-pg convertDriverError maps 22P02 → InvalidInputValue."""
    r = _run_vitest("@prisma/adapter-pg", "verifier-22p02")
    assert r.returncode == 0, (
        f"adapter-pg 22P02 verifier failed:\nSTDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-1000:]}"
    )


def test_neon_22p02_maps_to_invalid_input_value():
    """f2p: adapter-neon convertDriverError maps 22P02 → InvalidInputValue."""
    r = _run_vitest("@prisma/adapter-neon", "verifier-22p02")
    assert r.returncode == 0, (
        f"adapter-neon 22P02 verifier failed:\nSTDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-1000:]}"
    )


def test_ppg_22p02_maps_to_invalid_input_value():
    """f2p: adapter-ppg convertDriverError maps 22P02 → InvalidInputValue."""
    r = _run_vitest("@prisma/adapter-ppg", "verifier-22p02")
    assert r.returncode == 0, (
        f"adapter-ppg 22P02 verifier failed:\nSTDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-1000:]}"
    )


def test_existing_adapter_pg_unit_tests_pass():
    """p2p: existing adapter-pg unit tests still pass."""
    r = _run_vitest("@prisma/adapter-pg", "errors.test.ts")
    assert r.returncode == 0, (
        f"adapter-pg upstream errors.test.ts failed:\nSTDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-1000:]}"
    )


def test_existing_adapter_neon_unit_tests_pass():
    """p2p: existing adapter-neon unit tests still pass."""
    r = _run_vitest("@prisma/adapter-neon", "neon.test.ts")
    assert r.returncode == 0, (
        f"adapter-neon upstream tests failed:\nSTDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-1000:]}"
    )

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_should_handle_InvalidInputValue_22P02():
    """fail_to_pass | PR added test 'should handle InvalidInputValue (22P02)' in 'packages/adapter-pg/src/__tests__/errors.test.ts'"""
    r = _run_vitest("@prisma/adapter-pg", "errors.test.ts")
    assert r.returncode == 0, (
        f"PR-added test run failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
    combined = r.stdout + r.stderr
    # nop has 23 tests in errors.test.ts; gold adds 1 PR test → 24
    assert "24 passed" in combined, (
        "PR-added test was not detected — expected 24 passing tests "
        "(23 base + 1 PR-added) but vitest summary does not show 24 passed.\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

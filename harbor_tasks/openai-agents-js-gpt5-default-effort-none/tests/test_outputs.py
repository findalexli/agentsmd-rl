"""Behavioral tests for openai-agents-js PR #876.

Each ``test_*`` function maps 1:1 to a check id in ``eval_manifest.yaml``.

Tests run via ``subprocess`` against the cloned repository at
``/workspace/openai-agents-js``. The oracle vitest file at
``/tests/_oracle.test.ts`` is copied into the agents-core test directory
on demand (and removed afterwards) so that pass-to-pass checks like the
package's own build-check / vitest suite operate on a clean tree.
"""

from __future__ import annotations

import contextlib
import os
import subprocess
from pathlib import Path

import pytest  # noqa: F401  (autouse fixtures wouldn't load otherwise)

REPO = Path("/workspace/openai-agents-js")
PKG = REPO / "packages" / "agents-core"
ORACLE_DST = PKG / "test" / "_oracle.test.ts"

# Oracle vitest file source. Kept inline (rather than as a sibling file in
# /tests/) so the agent never sees it during development.
ORACLE_TS = """\
import { beforeEach, describe, expect, test, vi } from 'vitest';
import {
  getDefaultModelSettings,
  gpt5ReasoningSettingsRequired,
} from '../src/defaultModel';
import { loadEnv } from '../src/config';
import type { ModelSettingsReasoningEffort } from '../src/model';

vi.mock('../src/config', () => ({
  loadEnv: vi.fn(),
}));
const mockedLoadEnv = vi.mocked(loadEnv);
beforeEach(() => {
  mockedLoadEnv.mockReset();
  mockedLoadEnv.mockReturnValue({});
});

describe('oracle:getDefaultModelSettings', () => {
  test('oracle gpt-5.1 returns effort none with verbosity low', () => {
    expect(getDefaultModelSettings('gpt-5.1')).toEqual({
      reasoning: { effort: 'none' },
      text: { verbosity: 'low' },
    });
  });

  test('oracle gpt-5.2 returns effort none with verbosity low', () => {
    expect(getDefaultModelSettings('gpt-5.2')).toEqual({
      reasoning: { effort: 'none' },
      text: { verbosity: 'low' },
    });
  });

  test('oracle gpt-5.2-codex still returns effort low', () => {
    expect(getDefaultModelSettings('gpt-5.2-codex')).toEqual({
      reasoning: { effort: 'low' },
      text: { verbosity: 'low' },
    });
  });

  test('oracle other gpt-5 variants keep effort low', () => {
    expect(getDefaultModelSettings('gpt-5-mini')).toEqual({
      reasoning: { effort: 'low' },
      text: { verbosity: 'low' },
    });
    expect(getDefaultModelSettings('gpt-5-nano')).toEqual({
      reasoning: { effort: 'low' },
      text: { verbosity: 'low' },
    });
    expect(getDefaultModelSettings('gpt-5')).toEqual({
      reasoning: { effort: 'low' },
      text: { verbosity: 'low' },
    });
  });

  test('oracle non gpt-5 returns empty settings', () => {
    expect(getDefaultModelSettings('gpt-4o')).toEqual({});
  });
});

describe('oracle:gpt5ReasoningSettingsRequired', () => {
  test('oracle dotted gpt-5 variants are detected', () => {
    expect(gpt5ReasoningSettingsRequired('gpt-5.1')).toBe(true);
    expect(gpt5ReasoningSettingsRequired('gpt-5.2')).toBe(true);
    expect(gpt5ReasoningSettingsRequired('gpt-5.2-codex')).toBe(true);
  });
});

describe('oracle:ModelSettingsReasoningEffort type', () => {
  test('oracle xhigh is assignable to ModelSettingsReasoningEffort', () => {
    const a: ModelSettingsReasoningEffort = 'xhigh';
    const b: ModelSettingsReasoningEffort = 'none';
    expect(a).toBe('xhigh');
    expect(b).toBe('none');
  });
});
"""


def _run(cmd, cwd=REPO, timeout=600):
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "CI": "1", "NODE_ENV": "test"},
    )


def _safe_unlink(p: Path) -> None:
    try:
        p.unlink()
    except FileNotFoundError:
        pass


@contextlib.contextmanager
def _with_oracle():
    ORACLE_DST.write_text(ORACLE_TS, encoding="utf-8")
    try:
        yield
    finally:
        _safe_unlink(ORACLE_DST)


def _vitest_oracle(name_pattern: str, timeout: int = 240) -> subprocess.CompletedProcess:
    """Run vitest on the oracle file (copied in for the duration), filtered by test name.

    The repo's root ``vitest.config.ts`` defines ``projects: ['packages/*']``,
    so vitest must be invoked from the repo root with a path-relative test
    file argument.
    """
    with _with_oracle():
        return _run(
            [
                "pnpm",
                "exec",
                "vitest",
                "run",
                "packages/agents-core/test/_oracle.test.ts",
                "-t",
                name_pattern,
            ],
            timeout=timeout,
        )


def _format(r: subprocess.CompletedProcess) -> str:
    return f"stdout:\n{r.stdout[-3000:]}\nstderr:\n{r.stderr[-3000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass: behavioral oracle tests that fail at the base commit.
# ---------------------------------------------------------------------------


def test_gpt51_default_effort_is_none():
    r = _vitest_oracle("oracle gpt-5.1 returns effort none with verbosity low")
    assert r.returncode == 0, f"gpt-5.1 default settings did not match expected.\n{_format(r)}"


def test_gpt52_default_effort_is_none():
    r = _vitest_oracle("oracle gpt-5.2 returns effort none with verbosity low")
    assert r.returncode == 0, f"gpt-5.2 default settings did not match expected.\n{_format(r)}"


def test_xhigh_is_assignable_to_reasoning_effort_type():
    """Type-level check: 'xhigh' must be a valid ModelSettingsReasoningEffort.

    Drop the oracle test file (which uses ``const a: ModelSettingsReasoningEffort
    = 'xhigh'``) into the test tree, then run the package's ``build-check``
    (``tsc --noEmit -p ./tsconfig.test.json``). This fails at the base commit
    because the type union does not yet include ``'xhigh'``; it must succeed
    after the fix.
    """
    _safe_unlink(ORACLE_DST)
    with _with_oracle():
        r = _run(
            ["pnpm", "-F", "@openai/agents-core", "build-check"],
            timeout=300,
        )
    assert r.returncode == 0, (
        f"'xhigh' is not assignable to ModelSettingsReasoningEffort "
        f"(tsc rejected the oracle test).\n{_format(r)}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass: behavioral non-regression tests that already pass at base
# and must keep passing after the fix.
# ---------------------------------------------------------------------------


def test_gpt52_codex_keeps_effort_low():
    """gpt-5.2-codex must still default to effort 'low' (not 'none')."""
    r = _vitest_oracle("oracle gpt-5.2-codex still returns effort low")
    assert r.returncode == 0, f"gpt-5.2-codex defaults regressed.\n{_format(r)}"


def test_other_gpt5_models_keep_effort_low():
    """gpt-5, gpt-5-mini, gpt-5-nano must still default to effort 'low'."""
    r = _vitest_oracle("oracle other gpt-5 variants keep effort low")
    assert r.returncode == 0, f"non-supported gpt-5 variants regressed.\n{_format(r)}"


def test_dotted_gpt5_detected_as_reasoning_required():
    """gpt5ReasoningSettingsRequired must be true for dotted gpt-5 names."""
    r = _vitest_oracle("oracle dotted gpt-5 variants are detected")
    assert r.returncode == 0, f"dotted gpt-5 detection regressed.\n{_format(r)}"


def test_non_gpt5_returns_empty_settings():
    """Non gpt-5 models still return ``{}``."""
    r = _vitest_oracle("oracle non gpt-5 returns empty settings")
    assert r.returncode == 0, f"non gpt-5 default settings regressed.\n{_format(r)}"


# ---------------------------------------------------------------------------
# Pass-to-pass: repo-defined CI checks (clean tree, oracle NOT present).
# ---------------------------------------------------------------------------


def test_repo_existing_default_model_tests_pass():
    """The package's own ``defaultModel.test.ts`` keeps passing."""
    _safe_unlink(ORACLE_DST)
    r = _run(
        [
            "pnpm",
            "exec",
            "vitest",
            "run",
            "packages/agents-core/test/defaultModel.test.ts",
        ],
        timeout=240,
    )
    assert r.returncode == 0, f"existing defaultModel tests failed.\n{_format(r)}"


def test_agents_core_build_check():
    """``pnpm -F @openai/agents-core build-check`` (tsc --noEmit) passes."""
    _safe_unlink(ORACLE_DST)
    r = _run(
        ["pnpm", "-F", "@openai/agents-core", "build-check"],
        timeout=300,
    )
    assert r.returncode == 0, f"agents-core build-check failed.\n{_format(r)}"

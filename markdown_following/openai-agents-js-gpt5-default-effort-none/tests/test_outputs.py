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

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_build_all_packages():
    """pass_to_pass | CI job 'test' → step 'Build all packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build all packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_check_generated_declarations():
    """pass_to_pass | CI job 'test' → step 'Check generated declarations'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm -r -F "@openai/*" dist:check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check generated declarations' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_linter():
    """pass_to_pass | CI job 'test' → step 'Run linter'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run linter' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_type_check_docs_scripts():
    """pass_to_pass | CI job 'test' → step 'Type-check docs scripts'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm docs:scripts:check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Type-check docs scripts' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_compile_examples():
    """pass_to_pass | CI job 'test' → step 'Compile examples'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm -r build-check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Compile examples' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_returns_reasoning_defaults_for_GPT_5_2_models():
    """fail_to_pass | PR added test 'returns reasoning defaults for GPT-5.2 models' in 'packages/agents-core/test/defaultModel.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns reasoning defaults for GPT-5.2 models" 2>&1 || npx vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns reasoning defaults for GPT-5.2 models" 2>&1 || pnpm jest "packages/agents-core/test/defaultModel.test.ts" -t "returns reasoning defaults for GPT-5.2 models" 2>&1 || npx jest "packages/agents-core/test/defaultModel.test.ts" -t "returns reasoning defaults for GPT-5.2 models" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'returns reasoning defaults for GPT-5.2 models' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_returns_reasoning_defaults_for_GPT_5_2_codex_mod():
    """fail_to_pass | PR added test 'returns reasoning defaults for GPT-5.2 codex models' in 'packages/agents-core/test/defaultModel.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns reasoning defaults for GPT-5.2 codex models" 2>&1 || npx vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns reasoning defaults for GPT-5.2 codex models" 2>&1 || pnpm jest "packages/agents-core/test/defaultModel.test.ts" -t "returns reasoning defaults for GPT-5.2 codex models" 2>&1 || npx jest "packages/agents-core/test/defaultModel.test.ts" -t "returns reasoning defaults for GPT-5.2 codex models" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'returns reasoning defaults for GPT-5.2 codex models' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_returns_reasoning_defaults_for_GPT_5_1_models():
    """fail_to_pass | PR added test 'returns reasoning defaults for GPT-5.1 models' in 'packages/agents-core/test/defaultModel.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns reasoning defaults for GPT-5.1 models" 2>&1 || npx vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns reasoning defaults for GPT-5.1 models" 2>&1 || pnpm jest "packages/agents-core/test/defaultModel.test.ts" -t "returns reasoning defaults for GPT-5.1 models" 2>&1 || npx jest "packages/agents-core/test/defaultModel.test.ts" -t "returns reasoning defaults for GPT-5.1 models" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'returns reasoning defaults for GPT-5.1 models' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_returns_reasoning_defaults_for_other_GPT_5_model():
    """fail_to_pass | PR added test 'returns reasoning defaults for other GPT-5 models' in 'packages/agents-core/test/defaultModel.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns reasoning defaults for other GPT-5 models" 2>&1 || npx vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns reasoning defaults for other GPT-5 models" 2>&1 || pnpm jest "packages/agents-core/test/defaultModel.test.ts" -t "returns reasoning defaults for other GPT-5 models" 2>&1 || npx jest "packages/agents-core/test/defaultModel.test.ts" -t "returns reasoning defaults for other GPT-5 models" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'returns reasoning defaults for other GPT-5 models' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_detects_GPT_5_models_while_ignoring_chat_latest():
    """fail_to_pass | PR added test 'detects GPT-5 models while ignoring chat latest' in 'packages/agents-core/test/defaultModel.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-core/test/defaultModel.test.ts" -t "detects GPT-5 models while ignoring chat latest" 2>&1 || npx vitest run "packages/agents-core/test/defaultModel.test.ts" -t "detects GPT-5 models while ignoring chat latest" 2>&1 || pnpm jest "packages/agents-core/test/defaultModel.test.ts" -t "detects GPT-5 models while ignoring chat latest" 2>&1 || npx jest "packages/agents-core/test/defaultModel.test.ts" -t "detects GPT-5 models while ignoring chat latest" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'detects GPT-5 models while ignoring chat latest' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === Execution-mined f2p tests (taskforge.exec_f2p_miner) ===
# Source: dual-pass exec at base vs gold inside the task's docker image
# Test command: pnpm test
# 1 fail→pass + 50 pass→pass test name(s) discovered.

def test_exec_f2p_openai_agents_core_test_defaultmodel_test_ts_10_tests(_run_cmd=None):
    # Discovered f2p (failed at base, passed at gold): ' @openai/agents-core  test/defaultModel.test.ts (10 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff


def test_exec_p2p_openai_agents_test_index_test_ts_3_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents  test/index.test.ts (3 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_test_metadata_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents  test/metadata.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_agent_test_ts_25_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/agent.test.ts (25 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_agentscenarios_test_ts_43_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/agentScenarios.test.ts (43 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_createspans_test_ts_6_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/createSpans.test.ts (6 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_errors_test_ts_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/errors.test.ts (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_extensions_handofffilters_test_ts_3_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/extensions/handoffFilters.test.ts (3 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_extensions_handoffprompt_test_ts_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/extensions/handoffPrompt.test.ts (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_guardrail_test_ts_7_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/guardrail.test.ts (7 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_handoff_test_ts_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/handoff.test.ts (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_handoffs_test_ts_7_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/handoffs.test.ts (7 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_helpers_message_test_ts_4_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/helpers/message.test.ts (4 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_hitlmemorysessionscenario_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/hitlMemorySessionScenario.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_index_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/index.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_items_test_ts_8_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/items.test.ts (8 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_lifecycle_test_ts_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/lifecycle.test.ts (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_mcp_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/mcp.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_mcpcache_test_ts_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/mcpCache.test.ts (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_mcptoolfilter_integration_test_ts_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/mcpToolFilter.integration.test.ts (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_mcptoolfilter_test_ts_10_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/mcpToolFilter.test.ts (10 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_memorysession_test_ts_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/memorySession.test.ts (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_metadata_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/metadata.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_model_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/model.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_providers_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/providers.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_result_test_ts_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/result.test.ts (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_run_stream_test_ts_32_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/run.stream.test.ts (32 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_run_test_ts_81_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/run.test.ts (81 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_run_utils_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/run.utils.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runcontext_test_ts_3_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runContext.test.ts (3 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runstate_test_ts_22_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runState.test.ts (22 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_conversation_test_ts_4_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/conversation.test.ts (4 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_guardrails_test_ts_8_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/guardrails.test.ts (8 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_items_helpers_test_ts_4_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/items.helpers.test.ts (4 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_mcpapprovals_test_ts_3_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/mcpApprovals.test.ts (3 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_modeloutputs_test_ts_14_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/modelOutputs.test.ts (14 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_modelsettings_test_ts_7_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/modelSettings.test.ts (7 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_sessionpersistence_extended_test_ts_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/sessionPersistence.extended.test.ts (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_sessionpersistence_test_ts_23_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/sessionPersistence.test.ts (23 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_toolexecution_test_ts_53_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/toolExecution.test.ts (53 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_toolusetracker_test_ts_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/toolUseTracker.test.ts (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_tracing_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/tracing.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_turnresolution_test_ts_15_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/turnResolution.test.ts (15 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_shims_browser_shims_test_ts_6_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/shims/browser-shims.test.ts (6 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_shims_mcp_server_browser_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/shims/mcp-server/browser.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_shims_mcp_server_node_test_ts_10_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/shims/mcp-server/node.test.ts (10 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_tool_test_ts_22_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/tool.test.ts (22 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_tracing_test_ts_19_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/tracing.test.ts (19 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_usage_test_ts_9_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/usage.test.ts (9 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_utils_applydiff_test_ts_31_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/utils/applyDiff.test.ts (31 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_utils_base64_test_ts_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/utils/base64.test.ts (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff


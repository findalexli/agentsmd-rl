"""
Behavior tests for the segmented assistant output recovery fix
in openai/openai-agents-js#1117.

These tests run vitest against the openai-agents-js workspace at
/workspace/openai-agents-js, using a regression test file we drop into
the agents-core test tree at runtime so the agent's source
modifications are exercised through the public API.
"""
import json
import os
import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/openai-agents-js")
AGENTS_CORE = REPO / "packages" / "agents-core"
SCRATCH_TEST_DIR = AGENTS_CORE / "test" / "_segmented_regression"
SCRATCH_TEST_FILE = SCRATCH_TEST_DIR / "segmented.test.ts"


# Vitest source for the regression scenarios. We deliberately import only
# the public surface that exists at the base commit (`getOutputText` and
# `getLastTextFromOutputMessage`) and drive the deeper paths through
# `Agent.asTool`, so the tests do not depend on a specific new function
# name introduced by the agent's fix.
F2P_VITEST_SRC = r"""
import { describe, it, expect, vi } from 'vitest';
import {
  getOutputText,
  getLastTextFromOutputMessage,
} from '../../src/utils/messages';
import { Agent } from '../../src/agent';
import { Runner } from '../../src/run';
import { RunContext } from '../../src/runContext';
import { setDefaultModelProvider } from '../../src/providers';
import { FakeModelProvider } from '../stubs';
import type { ModelResponse } from '../../src/model';
import type { ResponseOutputItem } from '../../src/types';
import { Usage } from '../../src/usage';

describe('segmented assistant output recovery', () => {
  it('seg-plain-text concatenates multi-segment plain text in order', () => {
    const response: ModelResponse = {
      usage: new Usage(),
      output: [
        {
          type: 'message',
          role: 'assistant',
          status: 'completed',
          content: [
            { type: 'output_text', text: 'first ' },
            { type: 'output_text', text: 'second' },
          ],
        } as any,
      ],
    };
    expect(getOutputText(response)).toBe('first second');
  });

  it('seg-structured-json concatenates split structured JSON output', () => {
    const response: ModelResponse = {
      usage: new Usage(),
      output: [
        {
          type: 'message',
          role: 'assistant',
          status: 'completed',
          content: [
            { type: 'output_text', text: '{"answer":"str' },
            { type: 'output_text', text: 'uctured"}' },
          ],
        } as any,
      ],
    };
    expect(getOutputText(response)).toBe('{"answer":"structured"}');
  });

  it('seg-skip-non-text skips non output_text segments while concatenating', () => {
    const item: ResponseOutputItem = {
      type: 'message',
      role: 'assistant',
      status: 'completed',
      content: [
        { type: 'output_text', text: 'part1' },
        { type: 'refusal', refusal: 'ignored' },
        { type: 'output_text', text: 'part2' },
      ],
    } as any;
    const response: ModelResponse = {
      usage: new Usage(),
      output: [item],
    };
    expect(getOutputText(response)).toBe('part1part2');
  });

  it('seg-last-preserved getLastTextFromOutputMessage still returns last output_text', () => {
    const item: ResponseOutputItem = {
      type: 'message',
      role: 'assistant',
      status: 'completed',
      content: [
        { type: 'output_text', text: 'a' },
        { type: 'output_text', text: 'b' },
      ],
    } as any;
    expect(getLastTextFromOutputMessage(item)).toBe('b');
  });

  it('seg-as-tool Agent.asTool returns the full concatenated assistant text', async () => {
    setDefaultModelProvider(new FakeModelProvider());
    const agent = new Agent({
      name: 'Segmented Streamer',
      instructions: 'Return segmented output.',
    });
    const runSpy = vi.spyOn(Runner.prototype, 'run').mockResolvedValue({
      rawResponses: [
        {
          output: [
            {
              type: 'message',
              role: 'assistant',
              content: [
                { type: 'output_text', text: 'first ' },
                { type: 'output_text', text: 'second' },
              ],
            },
          ],
        },
      ],
      finalOutput: 'first second',
    } as any);
    const tool = agent.asTool({ toolDescription: 'desc' });
    const output = await tool.invoke(
      new RunContext(),
      JSON.stringify({ input: 'hi' }),
    );
    expect(output).toBe('first second');
    runSpy.mockRestore();
  });
});
"""


def _setup_vitest_files():
    SCRATCH_TEST_DIR.mkdir(parents=True, exist_ok=True)
    SCRATCH_TEST_FILE.write_text(F2P_VITEST_SRC)


def _strip_ansi(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", s)


_VITEST_CACHE = {}


def _run_vitest_segmented_once() -> dict:
    """Run our regression vitest file once and cache the JSON result.

    Returns a dict mapping test-id-prefix (the first token of the it() name,
    e.g. 'seg-plain-text') to True/False (passed/failed).
    """
    if "result" in _VITEST_CACHE:
        return _VITEST_CACHE["result"]
    _setup_vitest_files()
    out_path = REPO / "_seg_vitest_result.json"
    if out_path.exists():
        out_path.unlink()
    r = subprocess.run(
        [
            "pnpm",
            "exec",
            "vitest",
            "run",
            str(SCRATCH_TEST_FILE.relative_to(REPO)),
            "--reporter=json",
            f"--outputFile={out_path}",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=900,
        env={**os.environ, "CI": "1", "NODE_ENV": "test"},
    )
    parsed: dict = {}
    if out_path.exists():
        try:
            data = json.loads(out_path.read_text())
            for tr in data.get("testResults", []):
                for assertion in tr.get("assertionResults", []):
                    title = assertion.get("title", "")
                    status = assertion.get("status", "")
                    tag = title.split(" ", 1)[0] if title else ""
                    if tag:
                        parsed[tag] = status == "passed"
        except Exception as e:
            parsed["_parse_error"] = str(e)
    parsed["_returncode"] = r.returncode
    parsed["_stdout"] = _strip_ansi(r.stdout)[-4000:]
    parsed["_stderr"] = _strip_ansi(r.stderr)[-4000:]
    _VITEST_CACHE["result"] = parsed
    # Remove the scratch test file so later repo-wide vitest runs (e.g. pnpm test)
    # do not pick it up and fail at base.
    if SCRATCH_TEST_FILE.exists():
        SCRATCH_TEST_FILE.unlink()
    return parsed


def _check_seg(tag: str):
    res = _run_vitest_segmented_once()
    if "_parse_error" in res:
        raise AssertionError(
            f"Could not parse vitest JSON output (vitest rc={res.get('_returncode')}):\n"
            f"parse_error={res['_parse_error']}\n"
            f"STDOUT (last 4kB):\n{res.get('_stdout', '')}\n"
            f"STDERR (last 4kB):\n{res.get('_stderr', '')}"
        )
    if tag not in res:
        raise AssertionError(
            f"Vitest never ran the {tag!r} case. rc={res.get('_returncode')}.\n"
            f"Tags seen: {[k for k in res.keys() if not k.startswith('_')]}\n"
            f"STDOUT:\n{res.get('_stdout','')}\n"
            f"STDERR:\n{res.get('_stderr','')}"
        )
    assert res[tag] is True, (
        f"Vitest case {tag!r} failed.\n"
        f"STDOUT:\n{res.get('_stdout','')}\n"
        f"STDERR:\n{res.get('_stderr','')}"
    )


def test_segmented_get_output_text_concatenates():
    """f2p: getOutputText concatenates multi-segment plain text."""
    _check_seg("seg-plain-text")


def test_segmented_get_output_text_concatenates_structured_json():
    """f2p: getOutputText concatenates a split structured JSON output."""
    _check_seg("seg-structured-json")


def test_segmented_skips_non_output_text():
    """f2p: getOutputText skips non-output_text segments while concatenating."""
    _check_seg("seg-skip-non-text")


def test_get_last_text_still_returns_last_segment():
    """p2p: getLastTextFromOutputMessage preserves last-segment behavior."""
    _check_seg("seg-last-preserved")


def test_agent_as_tool_returns_full_segmented_output():
    """f2p: Agent.asTool returns concatenated text for segmented model output."""
    _check_seg("seg-as-tool")


def test_repo_existing_messages_unit_tests_still_pass():
    """p2p: pre-existing utils/messages.test.ts continues to pass."""
    r = subprocess.run(
        [
            "pnpm",
            "exec",
            "vitest",
            "run",
            "packages/agents-core/test/utils/messages.test.ts",
            "--reporter=default",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CI": "1", "NODE_ENV": "test"},
    )
    assert r.returncode == 0, (
        f"Existing messages tests failed:\n"
        f"STDOUT:\n{_strip_ansi(r.stdout)[-3000:]}\n"
        f"STDERR:\n{_strip_ansi(r.stderr)[-3000:]}"
    )


def test_agents_core_typecheck_passes():
    """p2p: agents-core build-check (tsc --noEmit) passes."""
    r = subprocess.run(
        ["pnpm", "-F", "@openai/agents-core", "build-check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CI": "1"},
    )
    assert r.returncode == 0, (
        f"build-check failed:\n"
        f"STDOUT:\n{_strip_ansi(r.stdout)[-3000:]}\n"
        f"STDERR:\n{_strip_ansi(r.stderr)[-3000:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_build_all_packages():
    """pass_to_pass | CI job 'test' → step 'Build all packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build:ci'], cwd=REPO,
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

# === Execution-mined f2p tests (taskforge.exec_f2p_miner) ===
# Source: dual-pass exec at base vs gold inside the task's docker image
# Test command: pnpm test
# 0 fail→pass + 50 pass→pass test name(s) discovered.

def test_exec_p2p_openai_agents_test_index_test_ts_4_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents  test/index.test.ts (4 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_test_metadata_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents  test/metadata.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_agent_test_ts_50_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/agent.test.ts (50 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_agentscenarios_test_ts_50_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/agentScenarios.test.ts (50 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_agenttoolinput_test_ts_17_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/agentToolInput.test.ts (17 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_createspans_test_ts_6_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/createSpans.test.ts (6 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_defaultmodel_test_ts_10_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/defaultModel.test.ts (10 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_errors_test_ts_6_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/errors.test.ts (6 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_events_test_ts_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/events.test.ts (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_extensions_handofffilters_test_ts_3_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/extensions/handoffFilters.test.ts (3 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_extensions_handoffprompt_test_ts_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/extensions/handoffPrompt.test.ts (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_guardrail_test_ts_9_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/guardrail.test.ts (9 tests)'
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

def test_exec_p2p_openai_agents_core_test_items_test_ts_10_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/items.test.ts (10 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_lifecycle_test_ts_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/lifecycle.test.ts (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_logger_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/logger.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_mcp_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/mcp.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_mcpcache_test_ts_9_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/mcpCache.test.ts (9 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_mcpservers_test_ts_13_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/mcpServers.test.ts (13 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_mcptofunctiontool_test_ts_7_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/mcpToFunctionTool.test.ts (7 tests)'
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

def test_exec_p2p_openai_agents_core_test_result_test_ts_17_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/result.test.ts (17 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_retrypolicy_test_ts_37_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/retryPolicy.test.ts (37 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_run_stream_test_ts_40_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/run.stream.test.ts (40 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_run_test_ts_116_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/run.test.ts (116 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_run_utils_test_ts_4_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/run.utils.test.ts (4 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runcontext_test_ts_10_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runContext.test.ts (10 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runstate_test_ts_64_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runState.test.ts (64 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_conversation_test_ts_4_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/conversation.test.ts (4 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_guardrails_test_ts_8_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/guardrails.test.ts (8 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_items_helpers_test_ts_6_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/items.helpers.test.ts (6 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_mcpapprovals_test_ts_9_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/mcpApprovals.test.ts (9 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_modeloutputs_test_ts_50_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/modelOutputs.test.ts (50 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_modelsettings_test_ts_11_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/modelSettings.test.ts (11 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_sessionpersistence_extended_test_ts_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/sessionPersistence.extended.test.ts (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_sessionpersistence_test_ts_31_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/sessionPersistence.test.ts (31 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_toolexecution_test_ts_95_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/toolExecution.test.ts (95 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_toolusetracker_test_ts_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/toolUseTracker.test.ts (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_tracing_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/tracing.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_turnresolution_test_ts_20_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/turnResolution.test.ts (20 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_shims_browser_shims_test_ts_6_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/shims/browser-shims.test.ts (6 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff


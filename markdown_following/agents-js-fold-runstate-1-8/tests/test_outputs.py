"""Tests for openai-agents-js PR #1075 — fold unreleased RunState schema changes into 1.8.

The PR reverts the in-progress schema version: there is no released `1.9` snapshot
format, so unreleased post-tag changes on `main` should fold into `1.8` instead of
introducing a separate, never-shipped `1.9` step.

Tests use ``pnpm exec tsx`` to evaluate TypeScript scripts that import directly
from ``packages/agents-core/src/`` so they reflect the agent's current source
state without any rebuild.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/agents-js")
ENV = {**os.environ, "CI": "1", "NODE_ENV": "test"}


def _run_tsx(script: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Execute a TypeScript snippet via the repo's vendored tsx loader."""
    pnpm = shutil.which("pnpm")
    assert pnpm, "pnpm must be on PATH"
    return subprocess.run(
        [pnpm, "exec", "tsx", "-e", script],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=ENV,
    )


def _last_json_line(stdout: str) -> dict:
    for line in reversed(stdout.strip().splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            return json.loads(line)
    raise AssertionError(f"no JSON object on stdout:\n{stdout!r}")


# -------------------------------------------------------------------
# Fail-to-pass: behavioural change introduced by PR #1075.
# -------------------------------------------------------------------

def test_current_schema_version_is_one_eight():
    """`CURRENT_SCHEMA_VERSION` exported from agents-core equals '1.8'."""
    script = textwrap.dedent(
        """
        import { CURRENT_SCHEMA_VERSION } from './packages/agents-core/src/runState';
        console.log(JSON.stringify({ v: CURRENT_SCHEMA_VERSION }));
        """
    )
    r = _run_tsx(script)
    assert r.returncode == 0, f"tsx failed:\nstdout={r.stdout}\nstderr={r.stderr}"
    payload = _last_json_line(r.stdout)
    assert payload["v"] == "1.8", (
        f"expected CURRENT_SCHEMA_VERSION == '1.8' but got {payload['v']!r}"
    )


def test_serialized_state_uses_one_eight():
    """A freshly serialised RunState stamps `$schemaVersion = '1.8'`."""
    script = textwrap.dedent(
        """
        import { Agent, RunState, RunContext } from './packages/agents-core/src/index';
        async function main() {
          const ctx = new RunContext();
          const agent = new Agent({ name: 'BenchAgent' });
          const state = new RunState(ctx, 'hello', agent, 3);
          const json = JSON.parse(state.toString());
          console.log(JSON.stringify({ schema: json["$schemaVersion"] }));
        }
        main();
        """
    )
    r = _run_tsx(script)
    assert r.returncode == 0, f"tsx failed:\nstdout={r.stdout}\nstderr={r.stderr}"
    payload = _last_json_line(r.stdout)
    assert payload["schema"] == "1.8", (
        f"expected serialised $schemaVersion '1.8' but got {payload['schema']!r}"
    )


def test_deserialize_rejects_one_nine():
    """A persisted state stamped `$schemaVersion: '1.9'` is rejected.

    Before the fix `'1.9'` was an in-progress version listed in
    ``SUPPORTED_SCHEMA_VERSIONS`` and was deserialised normally. The PR drops
    it from the supported set so that ``RunState.fromString`` rejects it via
    the standard unsupported-version error.
    """
    script = textwrap.dedent(
        """
        import { Agent, RunState, RunContext } from './packages/agents-core/src/index';
        async function main() {
          const ctx = new RunContext();
          const agent = new Agent({ name: 'BenchAgent' });
          const state = new RunState(ctx, 'hello', agent, 3);
          const json = JSON.parse(state.toString());
          json["$schemaVersion"] = '1.9';
          const tampered = JSON.stringify(json);
          let rejected = false;
          let message = '';
          try {
            await RunState.fromString(agent, tampered);
          } catch (err: any) {
            rejected = true;
            message = (err && err.message) ? err.message : String(err);
          }
          console.log(JSON.stringify({ rejected, message }));
        }
        main();
        """
    )
    r = _run_tsx(script)
    assert r.returncode == 0, f"tsx failed:\nstdout={r.stdout}\nstderr={r.stderr}"
    payload = _last_json_line(r.stdout)
    assert payload["rejected"], (
        "RunState.fromString should reject $schemaVersion '1.9' but it succeeded"
    )
    msg = payload["message"]
    assert "1.9" in msg and "not supported" in msg.lower(), (
        f"expected 'not supported' error mentioning '1.9' but got: {msg!r}"
    )


def test_one_eight_payloads_still_round_trip():
    """Tool-search payloads stamped '1.8' must continue to deserialize."""
    script = textwrap.dedent(
        """
        import { Agent, RunState, RunContext } from './packages/agents-core/src/index';
        import {
          RunToolSearchCallItem,
          RunToolSearchOutputItem,
        } from './packages/agents-core/src/items';
        async function main() {
          const ctx = new RunContext();
          const agent = new Agent({ name: 'Bench18' });
          const state = new RunState(ctx, 'hello', agent, 2);
          state._generatedItems.push(
            new RunToolSearchCallItem(
              {
                type: 'tool_search_call',
                id: 'ts_call_18',
                callId: 'ts_call_18',
                status: 'completed',
                arguments: { paths: ['crm'], query: 'profile' },
              } as any,
              agent,
            ),
            new RunToolSearchOutputItem(
              {
                type: 'tool_search_output',
                id: 'ts_output_18',
                callId: 'ts_call_18',
                status: 'completed',
                tools: [
                  { type: 'tool_reference', functionName: 'lookup_account', namespace: 'crm' },
                ],
              } as any,
              agent,
            ),
          );
          // Stamp '1.8' explicitly so the assertion is independent of CURRENT_SCHEMA_VERSION.
          const raw = JSON.parse(state.toString());
          raw["$schemaVersion"] = '1.8';
          const restored = await RunState.fromString(agent, JSON.stringify(raw));
          const types = restored._generatedItems.map((item: any) => item.constructor.name);
          console.log(JSON.stringify({ types }));
        }
        main();
        """
    )
    r = _run_tsx(script)
    assert r.returncode == 0, f"tsx failed:\nstdout={r.stdout}\nstderr={r.stderr}"
    payload = _last_json_line(r.stdout)
    assert payload["types"] == ["RunToolSearchCallItem", "RunToolSearchOutputItem"], (
        f"unexpected restored item types: {payload['types']!r}"
    )


# -------------------------------------------------------------------
# Pass-to-pass: existing repo behaviour we expect the fix to preserve.
# -------------------------------------------------------------------

def test_repo_runstate_vitest_passes():
    """The repo's own runState test file passes after the fix."""
    pnpm = shutil.which("pnpm")
    assert pnpm, "pnpm must be on PATH to run repo tests"
    r = subprocess.run(
        [pnpm, "exec", "vitest", "run", "packages/agents-core/test/runState.test.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=900,
        env=ENV,
    )
    assert r.returncode == 0, (
        f"runState.test.ts vitest suite failed:\n"
        f"--- stdout ---\n{r.stdout[-4000:]}\n"
        f"--- stderr ---\n{r.stderr[-2000:]}"
    )


def test_agents_core_build_check_passes():
    """Type-checking agents-core succeeds (catches TS regressions)."""
    pnpm = shutil.which("pnpm")
    assert pnpm, "pnpm must be on PATH"
    r = subprocess.run(
        [pnpm, "-F", "@openai/agents-core", "build-check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env=ENV,
    )
    assert r.returncode == 0, (
        f"agents-core build-check failed:\n"
        f"--- stdout ---\n{r.stdout[-4000:]}\n"
        f"--- stderr ---\n{r.stderr[-2000:]}"
    )

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

def test_exec_p2p_openai_agents_core_test_agenttoolinput_test_ts_12_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/agentToolInput.test.ts (12 tests)'
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

def test_exec_p2p_openai_agents_core_test_run_stream_test_ts_38_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/run.stream.test.ts (38 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_run_test_ts_108_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/run.test.ts (108 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_run_utils_test_ts_3_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/run.utils.test.ts (3 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runcontext_test_ts_10_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runContext.test.ts (10 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runstate_test_ts_63_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runState.test.ts (63 tests)'
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

def test_exec_p2p_openai_agents_core_test_runner_mcpapprovals_test_ts_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/mcpApprovals.test.ts (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_modeloutputs_test_ts_50_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/modelOutputs.test.ts (50 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_modelsettings_test_ts_8_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/modelSettings.test.ts (8 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_sessionpersistence_extended_test_ts_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/sessionPersistence.extended.test.ts (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_sessionpersistence_test_ts_28_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/sessionPersistence.test.ts (28 tests)'
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

def test_exec_p2p_openai_agents_core_test_shims_mcp_server_browser_test_ts_3_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/shims/mcp-server/browser.test.ts (3 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_shims_mcp_server_node_test_ts_11_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/shims/mcp-server/node.test.ts (11 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff


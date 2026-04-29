"""Behavioral tests for openai/openai-agents-js#1129.

Fail-to-pass tests target the computer_call / computer_call_output replay
path: when providerData includes empty pending_safety_checks or
acknowledged_safety_checks arrays, the rebuilt input item must omit those
fields entirely (the live Responses API rejects empty arrays for these
keys on the "computer" tool).

Pass-to-pass tests run the package's existing vitest suite, eslint, and
the TypeScript build-check so semantically correct fixes that break the
non-empty path or the rest of the package surface still fail.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import textwrap
from pathlib import Path

import pytest

REPO = Path("/workspace/openai-agents-js")
PKG = REPO / "packages" / "agents-openai"
ENV = {**os.environ, "CI": "1", "NODE_ENV": "test", "HUSKY": "0"}


def _run_ts_snippet(snippet: str, timeout: int = 180) -> dict:
    """Run a TypeScript snippet (executed under tsx) that calls getInputItems
    and emits a JSON object on stdout.

    The snippet must populate a ``__result`` object before the trailing
    JSON.stringify. We write it to a temporary .ts file inside the repo
    so module resolution mirrors the package's own tests.
    """
    wrapper = (
        "import { getInputItems } from "
        "'./packages/agents-openai/src/openaiResponsesModel';\n"
        "(globalThis as any).__getInputItems = getInputItems;\n"
        + snippet
        + "\nprocess.stdout.write('__JSON_START__' + "
        "JSON.stringify(__result) + '__JSON_END__');\n"
    )

    with tempfile.NamedTemporaryFile(
        suffix=".ts",
        dir=str(REPO),
        delete=False,
    ) as fh:
        fh.write(wrapper.encode("utf-8"))
        tmp_path = Path(fh.name)
    try:
        proc = subprocess.run(
            ["pnpm", "exec", "tsx", str(tmp_path)],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=ENV,
        )
    finally:
        tmp_path.unlink(missing_ok=True)
    out = proc.stdout
    if "__JSON_START__" not in out or "__JSON_END__" not in out:
        raise AssertionError(
            f"tsx snippet did not produce JSON sentinel.\n"
            f"returncode={proc.returncode}\nstdout={out!r}\nstderr={proc.stderr!r}"
        )
    payload = out.split("__JSON_START__", 1)[1].split("__JSON_END__", 1)[0]
    return json.loads(payload)


# ─────────────────────────── fail-to-pass ────────────────────────────

def test_computer_call_omits_empty_pending_safety_checks():
    """Empty pending_safety_checks must be removed entirely from the rebuilt
    computer_call input item — not normalised to []."""
    result = _run_ts_snippet(
        textwrap.dedent(
            """
            const items = (globalThis as any).__getInputItems([
              {
                type: 'computer_call',
                id: 'computer-empty-1',
                callId: 'computer-empty-call-1',
                action: { type: 'wait' },
                status: 'completed',
                providerData: { pending_safety_checks: [] },
              },
            ]);
            const __result = { items };
            """
        )
    )
    items = result["items"]
    assert len(items) == 1
    item = items[0]
    assert item["type"] == "computer_call"
    assert item["id"] == "computer-empty-1"
    assert item["call_id"] == "computer-empty-call-1"
    assert "pending_safety_checks" not in item, (
        f"computer_call must omit empty pending_safety_checks, got: {item!r}"
    )


def test_computer_call_output_omits_empty_acknowledged_safety_checks():
    """Empty acknowledged_safety_checks must be removed entirely from the
    rebuilt computer_call_output input item."""
    result = _run_ts_snippet(
        textwrap.dedent(
            """
            const items = (globalThis as any).__getInputItems([
              {
                type: 'computer_call_result',
                id: 'computer-empty-result-1',
                callId: 'computer-empty-call-1',
                output: { data: 'https://example.com/screenshot.png' },
                providerData: { acknowledged_safety_checks: [] },
              },
            ]);
            const __result = { items };
            """
        )
    )
    items = result["items"]
    assert len(items) == 1
    item = items[0]
    assert item["type"] == "computer_call_output"
    assert item["id"] == "computer-empty-result-1"
    assert item["call_id"] == "computer-empty-call-1"
    assert "acknowledged_safety_checks" not in item, (
        f"computer_call_output must omit empty acknowledged_safety_checks, got: {item!r}"
    )


def test_computer_call_omits_when_provider_data_missing_field():
    """When providerData has no safety-check fields at all, the rebuilt
    items must not synthesise empty arrays."""
    result = _run_ts_snippet(
        textwrap.dedent(
            """
            const items = (globalThis as any).__getInputItems([
              {
                type: 'computer_call',
                id: 'computer-missing-1',
                callId: 'computer-missing-call-1',
                action: { type: 'click', x: 1, y: 2 },
                status: 'completed',
              },
              {
                type: 'computer_call_result',
                id: 'computer-missing-result-1',
                callId: 'computer-missing-call-1',
                output: { data: 'https://example.com/missing.png' },
              },
            ]);
            const __result = { items };
            """
        )
    )
    items = result["items"]
    assert len(items) == 2
    call, output = items
    assert "pending_safety_checks" not in call, (
        f"missing-providerData computer_call must omit pending_safety_checks, got: {call!r}"
    )
    assert "acknowledged_safety_checks" not in output, (
        f"missing-providerData computer_call_output must omit acknowledged_safety_checks, got: {output!r}"
    )


def test_non_empty_safety_checks_are_preserved():
    """Sanity: non-empty safety-check arrays must still pass through to the
    rebuilt input items — the fix must only strip empty ones."""
    result = _run_ts_snippet(
        textwrap.dedent(
            """
            const items = (globalThis as any).__getInputItems([
              {
                type: 'computer_call',
                id: 'computer-keep-1',
                callId: 'computer-keep-call-1',
                action: { type: 'wait' },
                status: 'in_progress',
                providerData: {
                  pending_safety_checks: [
                    { id: 'check-1', code: 'confirm', message: 'Are you sure?' },
                  ],
                },
              },
              {
                type: 'computer_call_result',
                id: 'computer-keep-result-1',
                callId: 'computer-keep-call-1',
                output: { data: 'https://example.com/keep.png' },
                providerData: {
                  acknowledged_safety_checks: [
                    { id: 'check-1', code: 'confirm' },
                  ],
                },
              },
            ]);
            const __result = { items };
            """
        )
    )
    items = result["items"]
    assert len(items) == 2
    call, output = items
    assert call["pending_safety_checks"] == [
        {"id": "check-1", "code": "confirm", "message": "Are you sure?"},
    ], f"non-empty pending_safety_checks must be preserved, got: {call!r}"
    assert output["acknowledged_safety_checks"] == [
        {"id": "check-1", "code": "confirm"},
    ], f"non-empty acknowledged_safety_checks must be preserved, got: {output!r}"


# ─────────────────────────── pass-to-pass ────────────────────────────

def test_helpers_vitest_suite_passes():
    """Run the package's helpers test file (the one the PR amended)."""
    r = subprocess.run(
        [
            "pnpm",
            "exec",
            "vitest",
            "run",
            "--reporter=basic",
            "--no-coverage",
            "packages/agents-openai/test/openaiResponsesModel.helpers.test.ts",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env=ENV,
    )
    assert r.returncode == 0, (
        f"vitest helpers suite failed (rc={r.returncode}):\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n"
        f"--- stderr ---\n{r.stderr[-2000:]}"
    )


def test_agents_openai_full_vitest_passes():
    """Run the full agents-openai vitest suite as a broader regression net."""
    r = subprocess.run(
        [
            "pnpm",
            "exec",
            "vitest",
            "run",
            "--reporter=basic",
            "--no-coverage",
            "packages/agents-openai/test",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=900,
        env=ENV,
    )
    assert r.returncode == 0, (
        f"agents-openai vitest suite failed (rc={r.returncode}):\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n"
        f"--- stderr ---\n{r.stderr[-2000:]}"
    )


def test_agents_openai_typecheck():
    """The package must still type-check after the change."""
    r = subprocess.run(
        ["pnpm", "-F", "@openai/agents-openai", "build-check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env=ENV,
    )
    assert r.returncode == 0, (
        f"build-check failed (rc={r.returncode}):\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n"
        f"--- stderr ---\n{r.stderr[-2000:]}"
    )


def test_agents_openai_eslint():
    """ESLint over the agents-openai package must stay clean."""
    r = subprocess.run(
        [
            "pnpm",
            "exec",
            "eslint",
            "packages/agents-openai/src",
            "packages/agents-openai/test",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env=ENV,
    )
    assert r.returncode == 0, (
        f"eslint failed (rc={r.returncode}):\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n"
        f"--- stderr ---\n{r.stderr[-2000:]}"
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

def test_exec_p2p_openai_agents_core_test_agent_test_ts_52_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/agent.test.ts (52 tests)'
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

def test_exec_p2p_openai_agents_core_test_mcpprotocolcancellation_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/mcpProtocolCancellation.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_mcpservers_test_ts_13_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/mcpServers.test.ts (13 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_mcptofunctiontool_test_ts_9_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/mcpToFunctionTool.test.ts (9 tests)'
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

def test_exec_p2p_openai_agents_core_test_run_stream_test_ts_44_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/run.stream.test.ts (44 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_run_test_ts_121_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/run.test.ts (121 tests)'
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

def test_exec_p2p_openai_agents_core_test_runner_modeloutputs_test_ts_51_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/modelOutputs.test.ts (51 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_modelsettings_test_ts_11_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/modelSettings.test.ts (11 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_sessionpersistence_extended_test_ts_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/sessionPersistence.extended.test.ts (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runner_sessionpersistence_test_ts_35_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/sessionPersistence.test.ts (35 tests)'
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

def test_exec_p2p_openai_agents_core_test_runner_turnresolution_test_ts_22_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runner/turnResolution.test.ts (22 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff


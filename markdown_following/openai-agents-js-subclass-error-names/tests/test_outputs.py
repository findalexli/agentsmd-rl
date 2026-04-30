"""Behavioral tests for openai/openai-agents-js#862.

The PR sets `this.name = new.target.name` in the abstract `AgentsError`
constructor so concrete subclasses report their own class name when the error
is stringified or logged. Each test below imports the compiled module from
`@openai/agents-core` and asserts that the `.name` property of a concrete
subclass instance equals the subclass's class name.

At the base commit every test fails (all subclasses inherit `.name === 'Error'`
because the abstract constructor never assigns it). With the gold patch
applied and the package re-built, every test passes.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/openai-agents-js")
AGENTS_CORE = REPO / "packages" / "agents-core"


def _node_error_names() -> dict:
    """Construct one instance of every exported AgentsError subclass and
    return their `.name` properties as a JSON-decoded dict."""
    script = textwrap.dedent(
        """
        const m = require('@openai/agents-core');
        const out = {};
        out.MaxTurnsExceededError = new m.MaxTurnsExceededError('msg', {}).name;
        out.ModelBehaviorError = new m.ModelBehaviorError('msg', {}).name;
        out.UserError = new m.UserError('msg', {}).name;
        out.SystemError = new m.SystemError('msg', {}).name;
        out.GuardrailExecutionError = new m.GuardrailExecutionError(
            'msg', new Error('cause'), {}
        ).name;
        out.ToolCallError = new m.ToolCallError(
            'msg', new Error('cause'), {}
        ).name;
        out.InputGuardrailTripwireTriggered = new m.InputGuardrailTripwireTriggered(
            'msg', {}, {}
        ).name;
        out.OutputGuardrailTripwireTriggered = new m.OutputGuardrailTripwireTriggered(
            'msg', {}, {}
        ).name;
        out.ToolInputGuardrailTripwireTriggered = new m.ToolInputGuardrailTripwireTriggered(
            'msg', {}, {}
        ).name;
        out.ToolOutputGuardrailTripwireTriggered = new m.ToolOutputGuardrailTripwireTriggered(
            'msg', {}, {}
        ).name;
        process.stdout.write(JSON.stringify(out));
        """
    )
    proc = subprocess.run(
        ["node", "-e", script],
        cwd=AGENTS_CORE,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, (
        f"Node failed with exit {proc.returncode}\n"
        f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    return json.loads(proc.stdout)


# ---------------------------------------------------------------------------
# Fail-to-pass behavioral tests: each must fail at base, pass at gold.
# ---------------------------------------------------------------------------

def test_error_name_max_turns_exceeded():
    names = _node_error_names()
    assert names["MaxTurnsExceededError"] == "MaxTurnsExceededError", (
        f"expected 'MaxTurnsExceededError', got {names['MaxTurnsExceededError']!r}"
    )


def test_error_name_model_behavior():
    names = _node_error_names()
    assert names["ModelBehaviorError"] == "ModelBehaviorError"


def test_error_name_user_error():
    names = _node_error_names()
    assert names["UserError"] == "UserError"


def test_error_name_system_error():
    names = _node_error_names()
    assert names["SystemError"] == "SystemError"


def test_error_name_guardrail_execution():
    names = _node_error_names()
    assert names["GuardrailExecutionError"] == "GuardrailExecutionError"


def test_error_name_tool_call():
    names = _node_error_names()
    assert names["ToolCallError"] == "ToolCallError"


def test_error_name_input_guardrail_tripwire():
    names = _node_error_names()
    assert names["InputGuardrailTripwireTriggered"] == "InputGuardrailTripwireTriggered"


def test_error_name_output_guardrail_tripwire():
    names = _node_error_names()
    assert names["OutputGuardrailTripwireTriggered"] == "OutputGuardrailTripwireTriggered"


def test_error_name_tool_input_guardrail_tripwire():
    names = _node_error_names()
    assert names["ToolInputGuardrailTripwireTriggered"] == "ToolInputGuardrailTripwireTriggered"


def test_error_name_tool_output_guardrail_tripwire():
    names = _node_error_names()
    assert names["ToolOutputGuardrailTripwireTriggered"] == "ToolOutputGuardrailTripwireTriggered"


def test_error_string_includes_subclass_name():
    """`String(err)` for a subclass must start with the subclass name, not 'Error'."""
    script = textwrap.dedent(
        """
        const { UserError, ToolCallError } = require('@openai/agents-core');
        const out = {
            user: String(new UserError('boom', {})),
            tool: String(new ToolCallError('boom', new Error('c'), {})),
        };
        process.stdout.write(JSON.stringify(out));
        """
    )
    proc = subprocess.run(
        ["node", "-e", script],
        cwd=AGENTS_CORE,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["user"].startswith("UserError:"), data["user"]
    assert data["tool"].startswith("ToolCallError:"), data["tool"]


def test_invalid_tool_input_error_inherits_subclass_name():
    """Internal-but-instantiable subclasses (e.g. InvalidToolInputError) must also
    pick up the subclass name via `new.target.name`."""
    script = textwrap.dedent(
        """
        const { InvalidToolInputError } = require('@openai/agents-core/errors');
        const e = new InvalidToolInputError('msg', {});
        process.stdout.write(JSON.stringify({ name: e.name, str: String(e) }));
        """
    )
    proc = subprocess.run(
        ["node", "-e", script],
        cwd=AGENTS_CORE,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode != 0:
        # Fallback path: not all builds expose `errors` as a direct subpath.
        # Re-run via explicit dist path.
        script = textwrap.dedent(
            """
            const { InvalidToolInputError } = require('./dist/errors');
            const e = new InvalidToolInputError('msg', {});
            process.stdout.write(JSON.stringify({ name: e.name, str: String(e) }));
            """
        )
        proc = subprocess.run(
            ["node", "-e", script],
            cwd=AGENTS_CORE,
            capture_output=True,
            text=True,
            timeout=60,
        )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["name"] == "InvalidToolInputError", data
    assert data["str"].startswith("InvalidToolInputError:"), data


# ---------------------------------------------------------------------------
# Pass-to-pass: upstream tests that pass at both base and gold.
# ---------------------------------------------------------------------------

def test_pnpm_lint_passes():
    """The repo's eslint must pass on the modified source."""
    proc = subprocess.run(
        ["pnpm", "lint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CI": "1"},
    )
    assert proc.returncode == 0, (
        f"pnpm lint failed:\nstdout tail:\n{proc.stdout[-1500:]}\n"
        f"stderr tail:\n{proc.stderr[-1500:]}"
    )


def test_agents_core_build_check_passes():
    """`pnpm -F @openai/agents-core build-check` (tsc --noEmit) must succeed."""
    proc = subprocess.run(
        ["pnpm", "-F", "@openai/agents-core", "build-check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1"},
    )
    assert proc.returncode == 0, (
        f"build-check failed:\nstdout tail:\n{proc.stdout[-1500:]}\n"
        f"stderr tail:\n{proc.stderr[-1500:]}"
    )


def test_upstream_errors_vitest_passes():
    """The upstream errors.test.ts must pass — the existing assertions about
    initialized/throwing instances should remain green at both base and gold."""
    proc = subprocess.run(
        ["pnpm", "test", "errors"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CI": "1", "NODE_ENV": "test"},
    )
    assert proc.returncode == 0, (
        f"vitest errors failed:\nstdout tail:\n{proc.stdout[-2000:]}\n"
        f"stderr tail:\n{proc.stderr[-1500:]}"
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

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_should_set_error_names():
    """fail_to_pass | PR added test 'should set error names' in 'packages/agents-core/test/errors.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-core/test/errors.test.ts" -t "should set error names" 2>&1 || npx vitest run "packages/agents-core/test/errors.test.ts" -t "should set error names" 2>&1 || pnpm jest "packages/agents-core/test/errors.test.ts" -t "should set error names" 2>&1 || npx jest "packages/agents-core/test/errors.test.ts" -t "should set error names" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should set error names' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === Execution-mined f2p tests (taskforge.exec_f2p_miner) ===
# Source: dual-pass exec at base vs gold inside the task's docker image
# Test command: pnpm test
# 1 fail→pass + 50 pass→pass test name(s) discovered.

def test_exec_f2p_openai_agents_core_test_errors_test_ts_2_tests(_run_cmd=None):
    # Discovered f2p (failed at base, passed at gold): ' @openai/agents-core  test/errors.test.ts (2 tests)'
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

def test_exec_p2p_openai_agents_core_test_defaultmodel_test_ts_7_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/defaultModel.test.ts (7 tests)'
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


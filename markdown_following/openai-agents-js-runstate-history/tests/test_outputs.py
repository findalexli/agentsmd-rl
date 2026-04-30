"""Behavioural tests for the openai-agents-js RunState.history task.

Each test_* function corresponds 1:1 with a check id in eval_manifest.yaml.
The TS oracle (check_history.ts) is invoked via tsx; its line-prefixed
output (`CHECK <name>: PASS|FAIL ...`) is parsed to attribute results
to individual python tests.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/openai-agents-js")
PKG = REPO / "packages" / "agents-core"
TSX_BIN = REPO / "node_modules" / ".bin" / "tsx"

ORACLE_TS_SRC = Path("/tests/check_history.ts")
ORACLE_TS_DST = PKG / "check_history_oracle.ts"


@pytest.fixture(scope="module")
def oracle_output() -> dict[str, str]:
    """Run the oracle script once and parse its output.

    Returns a mapping from check name to the full status line (`PASS`
    or `FAIL <reason>`).
    """
    shutil.copyfile(ORACLE_TS_SRC, ORACLE_TS_DST)
    try:
        env = os.environ.copy()
        env["NODE_ENV"] = "test"
        result = subprocess.run(
            [str(TSX_BIN), str(ORACLE_TS_DST.name)],
            cwd=PKG,
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
    finally:
        if ORACLE_TS_DST.exists():
            ORACLE_TS_DST.unlink()

    combined = result.stdout + result.stderr
    parsed: dict[str, str] = {}
    for line in combined.splitlines():
        line = line.strip()
        if not line.startswith("CHECK "):
            continue
        rest = line[len("CHECK ") :]
        try:
            name, status = rest.split(": ", 1)
        except ValueError:
            continue
        parsed[name] = status

    parsed["__returncode__"] = str(result.returncode)
    parsed["__raw__"] = combined
    return parsed


def _assert_check(parsed: dict[str, str], check_name: str) -> None:
    raw = parsed.get("__raw__", "")
    status = parsed.get(check_name)
    assert status is not None, (
        f"Oracle check '{check_name}' did not appear in tsx output. "
        f"This usually means the script crashed before reaching it.\n"
        f"--- oracle output (last 2000 chars) ---\n{raw[-2000:]}"
    )
    assert status.startswith("PASS"), (
        f"Oracle check '{check_name}' failed: {status}\n"
        f"--- oracle output (last 2000 chars) ---\n{raw[-2000:]}"
    )


# ---------------------------------------------------------------------------
# fail_to_pass: behavioural oracle (4 distinct assertions)
# ---------------------------------------------------------------------------


def test_history_string_input_with_generated_item(oracle_output: dict[str, str]) -> None:
    """history = [{user-message-from-string}, ...generatedItems.rawItem]."""
    _assert_check(oracle_output, "string_input_with_generated_item")


def test_history_string_input_no_generated_items(oracle_output: dict[str, str]) -> None:
    """With no generated items, history wraps the string input only."""
    _assert_check(oracle_output, "string_input_no_generated_items")


def test_history_array_input_preserves_order(oracle_output: dict[str, str]) -> None:
    """When _originalInput is an array, those items appear unchanged at the start."""
    _assert_check(oracle_output, "array_input_preserves_order")


def test_history_preserved_after_serialization(oracle_output: dict[str, str]) -> None:
    """history equals after a toString()/fromString() round-trip."""
    _assert_check(oracle_output, "preserved_after_serialization")


# ---------------------------------------------------------------------------
# pass_to_pass: build-check + lint
# ---------------------------------------------------------------------------


def test_agents_core_build_check() -> None:
    """`pnpm -F @openai/agents-core run build-check` must succeed.

    This compiles the package (and its test files) with `tsc --noEmit`,
    catching any TypeScript errors introduced by the change.
    """
    result = subprocess.run(
        ["pnpm", "-F", "@openai/agents-core", "run", "build-check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        "build-check failed.\n"
        f"--- stdout (last 2000 chars) ---\n{result.stdout[-2000:]}\n"
        f"--- stderr (last 2000 chars) ---\n{result.stderr[-2000:]}"
    )


def test_repo_lint() -> None:
    """`pnpm lint` must pass on the modified source tree."""
    result = subprocess.run(
        ["pnpm", "lint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        "Lint failed.\n"
        f"--- stdout (last 2000 chars) ---\n{result.stdout[-2000:]}\n"
        f"--- stderr (last 2000 chars) ---\n{result.stderr[-2000:]}"
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

def test_ci_test_run_linter():
    """pass_to_pass | CI job 'test' → step 'Run linter'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run linter' failed (returncode={r.returncode}):\n"
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

def test_exec_p2p_openai_agents_test_index_test_ts_3_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents  test/index.test.ts (3 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_test_metadata_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents  test/metadata.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_agent_test_ts_15_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/agent.test.ts (15 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_errors_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/errors.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_extensions_handofffilters_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/extensions/handoffFilters.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_extensions_handoffprompt_test_ts_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/extensions/handoffPrompt.test.ts (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_guardrail_test_ts_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/guardrail.test.ts (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_handoff_test_ts_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/handoff.test.ts (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_handoffs_test_ts_4_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/handoffs.test.ts (4 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_helpers_message_test_ts_4_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/helpers/message.test.ts (4 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_index_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/index.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_items_test_ts_8_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/items.test.ts (8 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_mcp_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/mcp.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_mcpcache_test_ts_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/mcpCache.test.ts (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_mcptoolfilter_integration_test_ts_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/mcpToolFilter.integration.test.ts (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_mcptoolfilter_test_ts_10_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/mcpToolFilter.test.ts (10 tests)'
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

def test_exec_p2p_openai_agents_core_test_result_test_ts_4_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/result.test.ts (4 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_run_stream_test_ts_3_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/run.stream.test.ts (3 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_run_test_ts_24_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/run.test.ts (24 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_run_utils_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/run.utils.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runcontext_test_ts_3_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runContext.test.ts (3 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runimplementation_test_ts_37_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runImplementation.test.ts (37 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_runstate_test_ts_14_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/runState.test.ts (14 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_shims_mcp_server_browser_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/shims/mcp-server/browser.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_shims_mcp_server_node_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/shims/mcp-server/node.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_tool_test_ts_6_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/tool.test.ts (6 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_tracing_test_ts_11_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/tracing.test.ts (11 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_usage_test_ts_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/usage.test.ts (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_utils_index_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/utils/index.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_utils_messages_test_ts_4_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/utils/messages.test.ts (4 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_utils_safeexecute_test_ts_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/utils/safeExecute.test.ts (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_utils_serialize_test_ts_4_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/utils/serialize.test.ts (4 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_utils_smartstring_test_ts_7_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/utils/smartString.test.ts (7 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_utils_tools_test_ts_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/utils/tools.test.ts (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_core_test_utils_typeguards_test_ts_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-core  test/utils/typeGuards.test.ts (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_extensions_test_twiliorealtimetransport_test_ts_4_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-extensions  test/TwilioRealtimeTransport.test.ts (4 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_extensions_test_aisdk_test_ts_25_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-extensions  test/aiSdk.test.ts (25 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_extensions_test_index_test_ts_3_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-extensions  test/index.test.ts (3 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_openai_test_defaults_test_ts_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-openai  test/defaults.test.ts (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_openai_test_index_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-openai  test/index.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_openai_test_openaichatcompletionsconverter_test_ts_15_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-openai  test/openaiChatCompletionsConverter.test.ts (15 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_openai_test_openaichatcompletionsmodel_test_ts_10_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-openai  test/openaiChatCompletionsModel.test.ts (10 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_openai_test_openaichatcompletionsstreaming_test_ts_4_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-openai  test/openaiChatCompletionsStreaming.test.ts (4 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_openai_test_openaiprovider_test_ts_4_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-openai  test/openaiProvider.test.ts (4 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_openai_test_openairesponsesmodel_helpers_test_ts_14_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-openai  test/openaiResponsesModel.helpers.test.ts (14 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_openai_test_openairesponsesmodel_test_ts_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-openai  test/openaiResponsesModel.test.ts (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_openai_agents_openai_test_openaitracingexporter_test_ts_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' @openai/agents-openai  test/openaiTracingExporter.test.ts (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff


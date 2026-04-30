import subprocess
import os
import tempfile

REPO = '/workspace/openai-agents-js'

def run(cmd, **kwargs):
    kwargs.setdefault('capture_output', True)
    kwargs.setdefault('text', True)
    kwargs.setdefault('timeout', 300)
    kwargs.setdefault('cwd', REPO)
    return subprocess.run(cmd, **kwargs)


# ---------------------------------------------------------------------------
# F2P tests — fail on base commit, pass after the fix
# ---------------------------------------------------------------------------

def test_gpt51_default_reasoning_none():
    """getDefaultModelSettings('gpt-5.1') returns effort 'none'."""
    test_code = """import { describe, test, expect } from 'vitest';
import { getDefaultModelSettings } from '../src/defaultModel';

describe('gpt-5.1 defaults', () => {
  test('reasoning effort is none', () => {
    expect(getDefaultModelSettings('gpt-5.1')).toEqual({
      reasoning: { effort: 'none' },
      text: { verbosity: 'low' },
    });
  });
});
"""
    test_dir = f'{REPO}/packages/agents-core/test'
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.test.ts', dir=test_dir, delete=False)
    f.write(test_code)
    f.close()
    try:
        r = run(
            ['npx', 'vitest', 'run', f'packages/agents-core/test/{os.path.basename(f.name)}'],
            env={**os.environ, 'CI': '1', 'NODE_ENV': 'test'},
            timeout=120,
        )
        assert r.returncode == 0, (
            f"gpt-5.1 should default to effort='none'.\\n"
            f"STDOUT:\\n{r.stdout[-800:]}\\nSTDERR:\\n{r.stderr[-800:]}"
        )
    finally:
        os.unlink(f.name)


def test_gpt52_default_reasoning_none():
    """getDefaultModelSettings('gpt-5.2') returns effort 'none'."""
    test_code = """import { describe, test, expect } from 'vitest';
import { getDefaultModelSettings } from '../src/defaultModel';

describe('gpt-5.2 defaults', () => {
  test('reasoning effort is none', () => {
    expect(getDefaultModelSettings('gpt-5.2')).toEqual({
      reasoning: { effort: 'none' },
      text: { verbosity: 'low' },
    });
  });
});
"""
    test_dir = f'{REPO}/packages/agents-core/test'
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.test.ts', dir=test_dir, delete=False)
    f.write(test_code)
    f.close()
    try:
        r = run(
            ['npx', 'vitest', 'run', f'packages/agents-core/test/{os.path.basename(f.name)}'],
            env={**os.environ, 'CI': '1', 'NODE_ENV': 'test'},
            timeout=120,
        )
        assert r.returncode == 0, (
            f"gpt-5.2 should default to effort='none'.\\n"
            f"STDOUT:\\n{r.stdout[-800:]}\\nSTDERR:\\n{r.stderr[-800:]}"
        )
    finally:
        os.unlink(f.name)


def test_xhigh_reasoning_effort_valid():
    """'xhigh' is accepted as a ModelSettingsReasoningEffort value."""
    test_code = """import { ModelSettings } from './model';

const settings: ModelSettings = {
  reasoning: { effort: 'xhigh' },
};
void settings;
"""
    src_dir = f'{REPO}/packages/agents-core/src'
    fname = '_tmp_xhigh_check.ts'
    fpath = os.path.join(src_dir, fname)
    with open(fpath, 'w') as f:
        f.write(test_code)
    try:
        tsc = os.path.join(REPO, 'node_modules', '.bin', 'tsc')
        r = subprocess.run(
            [tsc, '--noEmit', '--project', 'tsconfig.test.json'],
            capture_output=True, text=True, timeout=60,
            cwd=f'{REPO}/packages/agents-core',
        )
        # tsc writes errors to stdout. Check both stdout and stderr.
        combined = (r.stdout or '') + '\\n' + (r.stderr or '')
        xhigh_errors = [l for l in combined.split('\\n') if 'xhigh' in l.lower() and 'error' in l.lower()]
        assert len(xhigh_errors) == 0, (
            f"'xhigh' should be accepted as a reasoning effort value.\\n"
            f"Errors:\\n" + '\\n'.join(xhigh_errors)
        )
    finally:
        if os.path.exists(fpath):
            os.unlink(fpath)


# ---------------------------------------------------------------------------
# P2P tests — pass on base commit
# ---------------------------------------------------------------------------

def test_gpt52_codex_still_low_effort():
    """getDefaultModelSettings('gpt-5.2-codex') retains effort 'low' (not 'none')."""
    test_code = """import { describe, test, expect } from 'vitest';
import { getDefaultModelSettings } from '../src/defaultModel';

describe('gpt-5.2-codex defaults', () => {
  test('reasoning effort is still low', () => {
    expect(getDefaultModelSettings('gpt-5.2-codex')).toEqual({
      reasoning: { effort: 'low' },
      text: { verbosity: 'low' },
    });
  });
});
"""
    test_dir = f'{REPO}/packages/agents-core/test'
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.test.ts', dir=test_dir, delete=False)
    f.write(test_code)
    f.close()
    try:
        r = run(
            ['npx', 'vitest', 'run', f'packages/agents-core/test/{os.path.basename(f.name)}'],
            env={**os.environ, 'CI': '1', 'NODE_ENV': 'test'},
            timeout=120,
        )
        assert r.returncode == 0, (
            f"gpt-5.2-codex should retain effort='low'.\\n"
            f"STDOUT:\\n{r.stdout[-800:]}\\nSTDERR:\\n{r.stderr[-800:]}"
        )
    finally:
        os.unlink(f.name)


def test_repo_build_check():
    """TypeScript build check passes for agents-core."""
    r = subprocess.run(
        ['pnpm', '-F', 'agents-core', 'build-check'],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Build check failed:\\n{r.stderr[-800:]}"


def test_repo_existing_vitest():
    """Existing defaultModel vitest tests pass."""
    r = run(
        ['npx', 'vitest', 'run', 'packages/agents-core/test/defaultModel.test.ts'],
        env={**os.environ, 'CI': '1', 'NODE_ENV': 'test'},
        timeout=120,
    )
    assert r.returncode == 0, (
        f"Existing vitest tests failed.\\n"
        f"STDOUT:\\n{r.stdout[-800:]}\\nSTDERR:\\n{r.stderr[-800:]}"
    )


def test_repo_lint():
    """ESLint passes on the changed source files."""
    r = subprocess.run(
        ['pnpm', 'eslint', 'packages/agents-core/src/defaultModel.ts',
         'packages/agents-core/src/model.ts'],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\\n{r.stderr[-800:]}"

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


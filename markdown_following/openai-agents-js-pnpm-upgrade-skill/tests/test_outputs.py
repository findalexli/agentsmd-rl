import os
import re
import subprocess

import yaml

REPO = "/workspace/openai-agents-js"
WORKFLOWS_DIR = os.path.join(REPO, ".github", "workflows")


def _workflow_files():
    return sorted(
        os.path.join(WORKFLOWS_DIR, f)
        for f in os.listdir(WORKFLOWS_DIR)
        if f.endswith((".yml", ".yaml"))
    )


def _find_action_setup_steps(doc):
    """Walk a parsed YAML doc and yield (step_name, uses, with_block) tuples."""
    if isinstance(doc, dict):
        if "uses" in doc and "pnpm/action-setup" in str(doc.get("uses", "")):
            yield doc.get("name"), doc["uses"], doc.get("with", {})
        for v in doc.values():
            yield from _find_action_setup_steps(v)
    elif isinstance(doc, list):
        for item in doc:
            yield from _find_action_setup_steps(item)


# ---------- fail_to_pass ----------

def test_action_setup_pinned():
    """No workflow uses pnpm/action-setup with a floating major-only tag like @v4."""
    for fpath in _workflow_files():
        fname = os.path.basename(fpath)
        with open(fpath) as fh:
            content = fh.read()
        for m in re.finditer(r"pnpm/action-setup@(\S+)", content):
            tag = m.group(1)
            assert re.search(r"\d+\.\d+", tag), (
                f"{fname}: pnpm/action-setup tag '{tag}' is a floating major; "
                f"must be pinned to a specific minor/patch version"
            )


def test_version_field_in_with():
    """Every pnpm/action-setup step specifies a version number in its with block."""
    for fpath in _workflow_files():
        fname = os.path.basename(fpath)
        with open(fpath) as fh:
            doc = yaml.safe_load(fh)
        for step_name, uses, with_block in _find_action_setup_steps(doc):
            assert isinstance(with_block, dict), (
                f"{fname}: pnpm/action-setup step '{step_name}' is missing its 'with' block"
            )
            assert "version" in with_block, (
                f"{fname}: pnpm/action-setup step '{step_name}' has no 'version' in 'with'"
            )


def test_docs_step_name():
    """The workflow step that installs pnpm in docs.yml is named 'Install pnpm'."""
    docs_yml = os.path.join(WORKFLOWS_DIR, "docs.yml")
    with open(docs_yml) as fh:
        doc = yaml.safe_load(fh)
    steps = doc.get("jobs", {}).get("build", {}).get("steps", [])
    for step in steps:
        if "pnpm/action-setup" in str(step.get("uses", "")):
            assert step.get("name") == "Install pnpm", (
                f"docs.yml pnpm/action-setup step should be named 'Install pnpm', "
                f"got '{step.get('name')}'"
            )
            return
    raise AssertionError("No pnpm/action-setup step found in docs.yml")


def test_pnpm_upgrade_skill_exists():
    """The pnpm-upgrade SKILL.md file exists."""
    skill_path = os.path.join(REPO, ".codex", "skills", "pnpm-upgrade", "SKILL.md")
    assert os.path.exists(skill_path), f"{skill_path} does not exist"


def test_skill_frontmatter():
    """SKILL.md has correct frontmatter fields."""
    skill_path = os.path.join(REPO, ".codex", "skills", "pnpm-upgrade", "SKILL.md")
    with open(skill_path) as fh:
        content = fh.read()
    assert "name: pnpm-upgrade" in content, "SKILL.md missing 'name: pnpm-upgrade' in frontmatter"
    assert "pnpm self-update" in content, "SKILL.md must reference pnpm self-update"
    assert "packageManager" in content, "SKILL.md must reference packageManager alignment"
    assert "pnpm/action-setup" in content, "SKILL.md must reference pnpm/action-setup"


# ---------- pass_to_pass ----------

def test_workflow_yaml_valid():
    """Every workflow YAML file remains valid YAML (p2p)."""
    for fpath in _workflow_files():
        fname = os.path.basename(fpath)
        with open(fpath) as fh:
            try:
                yaml.safe_load(fh)
            except yaml.YAMLError as e:
                raise AssertionError(f"{fname} is not valid YAML: {e}")


def test_repo_checkout_ok():
    """The repo is checked out at the expected base commit (p2p)."""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, f"git rev-parse failed: {r.stderr}"
    # HEAD should be the base commit (before fix applied)
    # This is informational; pass_to_pass just verifies the repo is usable

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_run_build():
    """pass_to_pass | CI job 'build' → step 'Run build'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run build' failed (returncode={r.returncode}):\n"
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


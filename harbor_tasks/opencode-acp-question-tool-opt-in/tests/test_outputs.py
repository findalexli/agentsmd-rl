"""
Task: opencode-acp-question-tool-opt-in
Repo: anomalyco/opencode @ 86e545a23ecdb2c1840ab01e82eca292117c6bbc
PR:   13562

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/opencode"
PKG = f"{REPO}/packages/opencode"


def _run_ts(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a TypeScript script using bun."""
    script_path = Path(PKG) / "_eval_tmp.ts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["bun", "run", str(script_path)],
            capture_output=True, text=True, timeout=timeout,
            cwd=PKG,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, repo_tests) — Repo CI tests as pass-to-pass gates
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_typescript_syntax():
    """Modified TypeScript files must parse without errors (repo typecheck)."""
    # Run tsc on the entire package to properly resolve path aliases
    r = subprocess.run(
        ["bun", "tsc", "--noEmit"],
        cwd=PKG, capture_output=True, timeout=120,
    )
    assert r.returncode == 0, f"TypeScript syntax error: {r.stderr or r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Full repo typecheck passes via turbo (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "typecheck"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"Repo typecheck failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_tool_registry_tests():
    """Tool registry unit tests pass (pass_to_pass) - covers modified registry.ts."""
    r = subprocess.run(
        ["bun", "test", "test/tool/registry.test.ts", "--timeout", "30000"],
        cwd=PKG, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Tool registry tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_question_tool_tests():
    """Question tool unit tests pass (pass_to_pass) - covers QuestionTool."""
    r = subprocess.run(
        ["bun", "test", "test/tool/question.test.ts", "--timeout", "30000"],
        cwd=PKG, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Question tool tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_opencode_package_typecheck():
    """opencode package typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "run", "typecheck"],
        cwd=PKG, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Package typecheck failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_acp_tests():
    """ACP module tests pass (pass_to_pass) - covers ACP agent interface."""
    r = subprocess.run(
        ["bun", "test", "test/acp/", "--timeout", "30000"],
        cwd=PKG, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"ACP tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_flag_opencode_enable_question_tool_defined():
    """Flag.OPENCODE_ENABLE_QUESTION_TOOL must be defined and work as truthy flag."""
    # Test the flag logic by importing it in a temp script
    result = _run_ts("""
import { Flag } from "./src/flag/flag"
// Test that the flag exists and is a boolean
const flagExists = Flag.OPENCODE_ENABLE_QUESTION_TOOL !== undefined
console.log(JSON.stringify({ flagExists, type: typeof Flag.OPENCODE_ENABLE_QUESTION_TOOL }))
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["flagExists"] is True, f"Flag does not exist: {data}"


# [pr_diff] fail_to_pass
def test_question_tool_gated_by_env_var():
    """QuestionTool must be excluded for ACP by default but included when env var is set."""
    # Test without env var (should be false for acp client)
    result1 = _run_ts("""
// Mock the Flag.OPENCODE_CLIENT as 'acp'
process.env.OPENCODE_CLIENT = "acp"
delete process.env.OPENCODE_ENABLE_QUESTION_TOOL

// Must re-import to get fresh flag values
const mod = await import("./src/flag/flag.ts")
const Flag = mod.Flag

const question = ["app", "cli", "desktop"].includes(Flag.OPENCODE_CLIENT) || Flag.OPENCODE_ENABLE_QUESTION_TOOL
console.log(JSON.stringify({ client: Flag.OPENCODE_CLIENT, questionEnabled: question, envFlag: Flag.OPENCODE_ENABLE_QUESTION_TOOL }))
""")
    assert result1.returncode == 0, f"Script failed: {result1.stderr}"
    data1 = json.loads(result1.stdout.strip())
    assert data1["questionEnabled"] is False, f"Question should be disabled for ACP without env var: {data1}"

    # Test with env var set (should be true)
    result2 = _run_ts("""
process.env.OPENCODE_CLIENT = "acp"
process.env.OPENCODE_ENABLE_QUESTION_TOOL = "1"

const mod = await import("./src/flag/flag.ts")
const Flag = mod.Flag

const question = ["app", "cli", "desktop"].includes(Flag.OPENCODE_CLIENT) || Flag.OPENCODE_ENABLE_QUESTION_TOOL
console.log(JSON.stringify({ client: Flag.OPENCODE_CLIENT, questionEnabled: question, envFlag: Flag.OPENCODE_ENABLE_QUESTION_TOOL }))
""")
    assert result2.returncode == 0, f"Script failed: {result2.stderr}"
    data2 = json.loads(result2.stdout.strip())
    assert data2["questionEnabled"] is True, f"Question should be enabled for ACP with env var: {data2}"


# [pr_diff] fail_to_pass
def test_cli_client_has_question_tool_by_default():
    """app/cli/desktop clients must have QuestionTool enabled without env var."""
    for client in ["app", "cli", "desktop"]:
        result = _run_ts(f"""
process.env.OPENCODE_CLIENT = "{client}"
delete process.env.OPENCODE_ENABLE_QUESTION_TOOL

const mod = await import("./src/flag/flag.ts")
const Flag = mod.Flag

const question = ["app", "cli", "desktop"].includes(Flag.OPENCODE_CLIENT) || Flag.OPENCODE_ENABLE_QUESTION_TOOL
console.log(JSON.stringify({{ client: Flag.OPENCODE_CLIENT, questionEnabled: question }}))
""")
        assert result.returncode == 0, f"Script failed for {client}: {result.stderr}"
        data = json.loads(result.stdout.strip())
        assert data["questionEnabled"] is True, f"Question should be enabled for {client} without env var: {data}"


# ---------------------------------------------------------------------------
# Config/documentation tests (pr_diff) — verify docs are updated
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_acp_readme_documents_question_tool_opt_in():
    """README.md must document the Question Tool opt-in for ACP."""
    readme = Path(PKG) / "src" / "acp" / "README.md"
    content = readme.read_text()

    # Check for key documentation elements
    assert "Question Tool Opt-In" in content or "question tool" in content.lower(), \
        "README should document Question Tool opt-in section"
    assert "OPENCODE_ENABLE_QUESTION_TOOL" in content, \
        "README should document the OPENCODE_ENABLE_QUESTION_TOOL env var"
    assert "ACP" in content or "acp" in content, \
        "README should reference ACP context"


# [pr_diff] fail_to_pass
def test_translator_md_includes_env_var():
    """translator.md must include OPENCODE_ENABLE_QUESTION_TOOL in env var list."""
    translator = Path(REPO) / ".opencode" / "agent" / "translator.md"
    content = translator.read_text()

    assert "OPENCODE_ENABLE_QUESTION_TOOL" in content, \
        "translator.md should include OPENCODE_ENABLE_QUESTION_TOOL in the glossary"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_typecheck_run_typecheck():
    """pass_to_pass | CI job 'typecheck' → step 'Run typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_prepare():
    """pass_to_pass | CI job 'build-tauri' → step 'Prepare'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun ./scripts/prepare.ts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Prepare' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_run_unit_tests():
    """pass_to_pass | CI job 'unit' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun turbo test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_run_app_e2e_tests():
    """pass_to_pass | CI job 'e2e' → step 'Run app e2e tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/app test:e2e:local'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run app e2e tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
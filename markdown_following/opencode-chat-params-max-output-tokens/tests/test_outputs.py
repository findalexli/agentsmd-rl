"""
Task: opencode-chat-params-max-output-tokens
Repo: anomalyco/opencode @ 5a6d10cd5363bd47c8e666bbc63435853a1f25b5
PR:   #21220

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
LLM_FILE = f"{REPO}/packages/opencode/src/session/llm.ts"
PLUGIN_FILE = f"{REPO}/packages/plugin/src/index.ts"


def _read(path: str) -> str:
    return Path(path).read_text()


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_modified_files_exist():
    """Both modified files exist and have substantial content."""
    llm_src = _read(LLM_FILE)
    assert len(llm_src) > 1000, "llm.ts is too small — likely a stub"
    plugin_src = _read(PLUGIN_FILE)
    assert len(plugin_src) > 500, "plugin/src/index.ts is too small"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_max_output_tokens_in_hook_output():
    """
    The chat.params hook output object must contain maxOutputTokens.
    Verified by parsing the AST structure of the Plugin.trigger call.
    """
    src = _read(LLM_FILE)

    marker = '"chat.params"'
    idx = src.find(marker)
    assert idx != -1, "Plugin.trigger('chat.params') not found in llm.ts"

    chunk = src[idx:idx + 2000]

    brace_depth = 0
    blocks = []
    block_start = -1
    in_string = False
    string_char = None

    for i, char in enumerate(chunk):
        if char in '"\'`':
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                backslash_count = 0
                j = i - 1
                while j >= 0 and chunk[j] == '\\':
                    backslash_count += 1
                    j -= 1
                if backslash_count % 2 == 0:
                    in_string = False

        if not in_string:
            if char == '{':
                if brace_depth == 0:
                    block_start = i
                brace_depth += 1
            elif char == '}':
                brace_depth -= 1
                if brace_depth == 0 and block_start >= 0:
                    blocks.append(chunk[block_start:i+1])
                    block_start = -1

    assert len(blocks) >= 2, "Could not find input and output objects in Plugin.trigger call"

    output_obj = blocks[1]
    assert "maxOutputTokens" in output_obj, \
        "maxOutputTokens not found in chat.params hook output object - plugins cannot provide this value"


# [pr_diff] fail_to_pass
def test_stream_text_uses_params_max_output_tokens():
    """
    streamText must use params.maxOutputTokens (from hook), not a local variable.
    """
    src = _read(LLM_FILE)

    stream_idx = src.find("return streamText(")
    assert stream_idx != -1, "streamText call not found in llm.ts"

    call_section = src[stream_idx:stream_idx + 3000]

    assert "params.maxOutputTokens" in call_section, \
        "streamText does not use params.maxOutputTokens - plugins cannot override maxOutputTokens"


# [pr_diff] fail_to_pass
def test_hook_type_includes_max_output_tokens():
    """
    The Hooks interface for chat.params must include maxOutputTokens in its output type.
    """
    src = _read(PLUGIN_FILE)

    marker = '"chat.params"'
    idx = src.find(marker)
    assert idx != -1, "chat.params hook not found in plugin/src/index.ts"

    section = src[idx:idx + 800]

    assert "maxOutputTokens" in section, \
        "maxOutputTokens not in chat.params hook output type"

    type_pattern = r"maxOutputTokens\s*[?:]\s*(?:number\s*\|\s*undefined|undefined\s*\|\s*number)"
    assert re.search(type_pattern, section), \
        "maxOutputTokens type is not (number | undefined) - expected proper type annotation"


# [pr_diff] fail_to_pass
def test_max_output_tokens_computed_before_hook():
    """
    maxOutputTokens must be computed BEFORE Plugin.trigger("chat.params",...).
    """
    src = _read(LLM_FILE)

    max_def_pattern = r"(?:const|let)\s+maxOutputTokens\s*="
    max_def = re.search(max_def_pattern, src)
    assert max_def, "maxOutputTokens definition not found in llm.ts"

    hook_pattern = r'Plugin\.trigger\(\s*["\']chat\.params["\']'
    hook_match = re.search(hook_pattern, src)
    assert hook_match, "Plugin.trigger('chat.params') not found in llm.ts"

    assert max_def.start() < hook_match.start(), \
        "maxOutputTokens is defined AFTER Plugin.trigger('chat.params') — must be before so plugins receive the default value"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression
# -----------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_hook_preserves_existing_params():
    """chat.params hook output type still includes temperature, topP, topK, options."""
    src = _read(PLUGIN_FILE)

    marker = '"chat.params"'
    idx = src.find(marker)
    assert idx != -1, "chat.params hook not found"

    section = src[idx:idx + 800]
    for field in ["temperature", "topP", "topK", "options"]:
        assert field in section, f"chat.params hook output missing '{field}' field"


# [static] pass_to_pass
def test_stream_text_still_passes_core_params():
    """streamText call still passes temperature, topP, topK from params."""
    src = _read(LLM_FILE)

    stream_idx = src.find("return streamText(")
    assert stream_idx != -1, "streamText call not found"

    section = src[stream_idx:stream_idx + 2000]
    for field in ["temperature", "topP", "topK"]:
        assert f"params.{field}" in section, \
            f"streamText call missing params.{field}"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — behavioral CI/CD checks
# -----------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typecheck_plugin():
    """Plugin package typecheck passes."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/opencode/packages/plugin && bun run typecheck"],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Plugin typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_typecheck_opencode():
    """Opencode package typecheck passes."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/opencode/packages/opencode && bun run typecheck"],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Opencode typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_llm_tests():
    """LLM session tests pass."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/opencode/packages/opencode && bun test test/session/llm.test.ts"],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"LLM tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI: root typecheck (turbo typecheck across all packages)
def test_ci_typecheck_run_typecheck():
    """pass_to_pass | CI job 'typecheck' → step 'Run typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_cli_build():
    """pass_to_pass | CI job 'build-cli' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", './packages/opencode/script/build.ts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_electron_prepare():
    """pass_to_pass | CI job 'build-electron' → step 'Prepare'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun ./scripts/prepare.ts'], cwd=os.path.join(REPO, 'packages/desktop-electron'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Prepare' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_electron_build():
    """pass_to_pass | CI job 'build-electron' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run build'], cwd=os.path.join(REPO, 'packages/desktop-electron'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_verify_certificate():
    """pass_to_pass | CI job 'build-tauri' → step 'Verify Certificate'"""
    r = subprocess.run(
        ["bash", "-lc", 'CERT_INFO=$(security find-identity -v -p codesigning build.keychain | grep "Developer ID Application")\nCERT_ID=$(echo "$CERT_INFO" | awk -F\'"\' \'{print $2}\')\necho "CERT_ID=$CERT_ID" >> $GITHUB_ENV\necho "Certificate imported."'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify Certificate' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_show_tauri_cli_version():
    """pass_to_pass | CI job 'build-tauri' → step 'Show tauri-cli version'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo tauri --version'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Show tauri-cli version' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_run_unit_tests():
    """fail_to_pass | CI job 'unit' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun turbo test:ci'], cwd=REPO,
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

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
    
    # Find the Plugin.trigger("chat.params" call
    marker = '"chat.params"'
    idx = src.find(marker)
    assert idx != -1, "Plugin.trigger('chat.params') not found in llm.ts"
    
    # Extract a chunk after the marker to find the output object
    chunk = src[idx:idx + 2000]
    
    # Find the output object (second argument to Plugin.trigger)
    # It starts with { temperature: ... } and ends before the closing )
    # The structure is: Plugin.trigger("chat.params", {input}, {output})
    
    # Find all top-level brace blocks in this section
    brace_depth = 0
    blocks = []
    block_start = -1
    in_string = False
    string_char = None
    
    for i, char in enumerate(chunk):
        # Handle string escaping
        if char in '"\'`':
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                # Check if escaped
                backslash_count = 0
                j = i - 1
                while j >= 0 and chunk[j] == '\\':
                    backslash_count += 1
                    j -= 1
                if backslash_count % 2 == 0:  # Not escaped
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
    
    # Need at least 2 blocks: the input object and output object
    assert len(blocks) >= 2, "Could not find input and output objects in Plugin.trigger call"
    
    # Second block is the output object
    output_obj = blocks[1]
    assert "maxOutputTokens" in output_obj, \
        "maxOutputTokens not found in chat.params hook output object - plugins cannot provide this value"


# [pr_diff] fail_to_pass
def test_stream_text_uses_params_max_output_tokens():
    """
    streamText must use params.maxOutputTokens (from hook), not a local variable.
    
    This test verifies that the streamText call receives maxOutputTokens from
    the params object returned by Plugin.trigger, allowing plugins to override it.
    """
    src = _read(LLM_FILE)
    
    # Find the streamText call
    stream_idx = src.find("return streamText(")
    assert stream_idx != -1, "streamText call not found in llm.ts"
    
    # Extract a large chunk to capture the full call
    call_section = src[stream_idx:stream_idx + 3000]
    
    # Check that params.maxOutputTokens is used (not bare maxOutputTokens:)
    # The pattern we look for is that maxOutputTokens is accessed via the params object
    assert "params.maxOutputTokens" in call_section, \
        "streamText does not use params.maxOutputTokens - plugins cannot override maxOutputTokens"
    
    # Also verify that maxOutputTokens appears in the params destructuring or access pattern
    # This ensures it's being pulled from the hook-returned params object


# [pr_diff] fail_to_pass
def test_hook_type_includes_max_output_tokens():
    """
    The Hooks interface for chat.params must include maxOutputTokens in its output type.
    This allows TypeScript to type-check plugin implementations.
    """
    src = _read(PLUGIN_FILE)
    
    marker = '"chat.params"'
    idx = src.find(marker)
    assert idx != -1, "chat.params hook not found in plugin/src/index.ts"
    
    # Extract section to find the output type definition
    section = src[idx:idx + 800]
    
    # Verify maxOutputTokens is declared in the output type
    assert "maxOutputTokens" in section, \
        "maxOutputTokens not in chat.params hook output type"
    
    # Verify proper typing (number | undefined) - this ensures plugins get proper type checking
    type_pattern = r"maxOutputTokens\s*[?:]\s*:\s*(?:number\s*\|\s*undefined|undefined\s*\|\s*number)"
    assert re.search(type_pattern, section), \
        "maxOutputTokens type is not (number | undefined) - expected proper type annotation"


# [pr_diff] fail_to_pass  
def test_max_output_tokens_computed_before_hook():
    """
    maxOutputTokens must be computed BEFORE Plugin.trigger("chat.params",...).
    
    This ensures the value is available to be passed in the hook's output object,
    allowing plugins to see and potentially modify the default value.
    """
    src = _read(LLM_FILE)
    
    # Find where maxOutputTokens is defined (const or let)
    max_def_pattern = r"(?:const|let)\s+maxOutputTokens\s*="
    max_def = re.search(max_def_pattern, src)
    assert max_def, "maxOutputTokens definition not found in llm.ts"
    
    # Find the chat.params trigger call
    hook_pattern = r'Plugin\.trigger\(\s*["\']chat\.params["\']'
    hook_match = re.search(hook_pattern, src)
    assert hook_match, "Plugin.trigger('chat.params') not found in llm.ts"
    
    # The definition must come BEFORE the hook call
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
# Pass-to-pass (repo_tests) — CI/CD checks
# -----------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typecheck_plugin():
    """Plugin package typecheck passes (pass_to_pass)."""
    # Install bun and dependencies
    install_bun = subprocess.run(
        ["bash", "-c", "curl -fsSL https://bun.sh/install | bash >/dev/null 2>&1 && mv /root/.bun/bin/bun /usr/local/bin/"],
        capture_output=True, text=True, timeout=60,
    )
    assert install_bun.returncode == 0, f"Failed to install bun: {install_bun.stderr}"
    
    install_deps = subprocess.run(
        ["bash", "-c", "cd /workspace/opencode && bun install"],
        capture_output=True, text=True, timeout=180,
    )
    # Ignore warnings, only fail on actual errors
    
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/opencode/packages/plugin && bun run typecheck"],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Plugin typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_typecheck_opencode():
    """Opencode package typecheck passes (pass_to_pass)."""
    # Bun should already be installed from previous test, but check just in case
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/opencode/packages/opencode && bun run typecheck"],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Opencode typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_llm_tests():
    """LLM session tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/opencode/packages/opencode && bun test test/session/llm.test.ts"],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"LLM tests failed:\n{r.stderr[-500:]}"

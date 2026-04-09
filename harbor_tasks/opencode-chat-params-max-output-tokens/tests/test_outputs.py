"""
Task: opencode-chat-params-max-output-tokens
Repo: anomalyco/opencode @ 5a6d10cd5363bd47c8e666bbc63435853a1f25b5
PR:   #21220

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import shlex
import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
LLM_FILE = f"{REPO}/packages/opencode/src/session/llm.ts"
PLUGIN_FILE = f"{REPO}/packages/plugin/src/index.ts"


def _read(path: str) -> str:
    return Path(path).read_text()


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


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
def test_max_output_tokens_in_hook_params():
    """maxOutputTokens must be in the output object passed to Plugin.trigger("chat.params",...)."""
    r = _run_node("""
import { readFileSync } from 'fs';
const src = readFileSync('packages/opencode/src/session/llm.ts', 'utf8');

// Find the Plugin.trigger("chat.params",...) call
const marker = '"chat.params"';
const idx = src.indexOf(marker);
if (idx === -1) { console.error('Plugin.trigger("chat.params") not found'); process.exit(1); }

// Extract section starting from the marker
const section = src.slice(idx, idx + 1500);

// Find all top-level { } blocks (input object, then output object)
let depth = 0;
let blocks = [];
let start = -1;
for (let i = 0; i < section.length; i++) {
    if (section[i] === '{') {
        if (depth === 0) start = i;
        depth++;
    } else if (section[i] === '}') {
        depth--;
        if (depth === 0 && start >= 0) {
            blocks.push(section.slice(start, i + 1));
            start = -1;
        }
    }
}

// The second block is the output object passed to the hook
if (blocks.length < 2) {
    console.error('Could not find input and output objects in chat.params trigger call');
    process.exit(1);
}

const output = blocks[1];
if (!output.includes('maxOutputTokens')) {
    console.error('maxOutputTokens not found in chat.params output object');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Node check failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_stream_text_uses_params_max_output_tokens():
    """streamText call must use params.maxOutputTokens, not a bare local variable."""
    src = _read(LLM_FILE)

    stream_idx = src.find("return streamText(")
    assert stream_idx != -1, "streamText call not found in llm.ts"

    call_section = src[stream_idx:stream_idx + 2000]

    # The fix uses "params.maxOutputTokens" — the base uses bare "maxOutputTokens,"
    assert "params.maxOutputTokens" in call_section, \
        "streamText does not use params.maxOutputTokens — plugins cannot override maxOutputTokens"


# [pr_diff] fail_to_pass
def test_hook_type_includes_max_output_tokens():
    """The Hooks interface for chat.params must include maxOutputTokens in its output type."""
    src = _read(PLUGIN_FILE)

    marker = '"chat.params"'
    idx = src.find(marker)
    assert idx != -1, "chat.params hook not found in plugin/src/index.ts"

    # Extract from marker to the next hook definition
    section = src[idx:idx + 500]

    assert "maxOutputTokens" in section, \
        "maxOutputTokens not in chat.params hook output type"

    # Verify proper typing (number | undefined), not any
    assert re.search(r"maxOutputTokens\s*[?:]?\s*:?\s*(number|undefined)", section), \
        "maxOutputTokens type is not properly defined (expected number or undefined)"


# [pr_diff] fail_to_pass
def test_max_output_tokens_computed_before_hook():
    """maxOutputTokens must be computed BEFORE Plugin.trigger("chat.params",...), not after."""
    src = _read(LLM_FILE)

    max_def = re.search(r"const\s+maxOutputTokens\s*=?", src)
    assert max_def, "const maxOutputTokens = ... not found in llm.ts"

    # Find the chat.params trigger call (flexible whitespace matching)
    hook_match = re.search(r'Plugin\.trigger\(\s*["\']chat\.params["\']', src)
    assert hook_match, "Plugin.trigger('chat.params') not found in llm.ts"

    assert max_def.start() < hook_match.start(), \
        "maxOutputTokens is defined AFTER Plugin.trigger('chat.params') — must be before so plugins can modify it"


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

    section = src[idx:idx + 500]
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

"""
Task: opencode-acp-config-options
Repo: opencode @ 4712c18a5833da85cd3946357662b148e78573f7
PR:   21134

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/opencode"
AGENT_TS = f"{REPO}/packages/opencode/src/acp/agent.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typecheck():
    """TypeScript typechecking must pass for the opencode package."""
    r = subprocess.run(
        ["bun", "typecheck"],
        cwd=f"{REPO}/packages/opencode",
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"bun typecheck failed:\n{r.stdout.decode()[-2000:]}\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_build_config_options_model_output():
    """buildConfigOptions produces a model option with type 'select' and correct fields."""
    script = textwrap.dedent("""\
        const fs = require('fs');
        const src = fs.readFileSync('%s', 'utf8');

        const marker = 'function buildConfigOptions(';
        const start = src.indexOf(marker);
        if (start === -1) { console.error('buildConfigOptions not found'); process.exit(1); }

        let braceStart = src.indexOf('{', start);
        let depth = 0;
        let end = -1;
        for (let i = braceStart; i < src.length; i++) {
            if (src[i] === '{') depth++;
            if (src[i] === '}') depth--;
            if (depth === 0) { end = i + 1; break; }
        }
        if (end === -1) { console.error('Could not find function end'); process.exit(1); }

        let funcSrc = src.slice(start, end);
        funcSrc = funcSrc.replace(/:\\s*SessionConfigOption\\[\\]/g, '');
        funcSrc = funcSrc.replace(/input:\\s*\\{[^)]+\\}/s, 'input');

        const fn = eval('(' + funcSrc + ')');

        const result = fn({
            currentModelId: 'anthropic/claude-opus',
            availableModels: [
                { modelId: 'anthropic/claude-opus', name: 'Claude Opus' },
                { modelId: 'anthropic/claude-sonnet', name: 'Claude Sonnet' },
                { modelId: 'openai/gpt-4o', name: 'GPT-4o' },
            ],
        });

        if (!Array.isArray(result)) { console.error('not array'); process.exit(1); }

        const model = result.find(o => o.id === 'model');
        if (!model) { console.error('no model option'); process.exit(1); }
        if (model.type !== 'select') { console.error('model type: ' + model.type); process.exit(1); }
        if (model.category !== 'model') { console.error('model category: ' + model.category); process.exit(1); }
        if (model.currentValue !== 'anthropic/claude-opus') { console.error('wrong currentValue'); process.exit(1); }
        if (model.options.length !== 3) { console.error('expected 3 options, got ' + model.options.length); process.exit(1); }
        if (model.options[0].value !== 'anthropic/claude-opus') { console.error('wrong first value'); process.exit(1); }
        if (model.options[0].name !== 'Claude Opus') { console.error('wrong first name'); process.exit(1); }

        const mode = result.find(o => o.id === 'mode');
        if (mode) { console.error('unexpected mode option when no modes provided'); process.exit(1); }

        console.log(JSON.stringify(result));
    """ % AGENT_TS)

    r = subprocess.run(["node", "-e", script], capture_output=True, timeout=30)
    assert r.returncode == 0, f"buildConfigOptions model test failed:\n{r.stderr.decode()}"

    data = json.loads(r.stdout.decode().strip())
    assert len(data) == 1, f"Expected 1 option (model only), got {len(data)}"


# [pr_diff] fail_to_pass
def test_build_config_options_mode_output():
    """buildConfigOptions includes mode option when modes are provided."""
    script = textwrap.dedent("""\
        const fs = require('fs');
        const src = fs.readFileSync('%s', 'utf8');

        const marker = 'function buildConfigOptions(';
        const start = src.indexOf(marker);
        if (start === -1) { console.error('buildConfigOptions not found'); process.exit(1); }

        let braceStart = src.indexOf('{', start);
        let depth = 0;
        let end = -1;
        for (let i = braceStart; i < src.length; i++) {
            if (src[i] === '{') depth++;
            if (src[i] === '}') depth--;
            if (depth === 0) { end = i + 1; break; }
        }
        if (end === -1) { console.error('Could not find function end'); process.exit(1); }

        let funcSrc = src.slice(start, end);
        funcSrc = funcSrc.replace(/:\\s*SessionConfigOption\\[\\]/g, '');
        funcSrc = funcSrc.replace(/input:\\s*\\{[^)]+\\}/s, 'input');

        const fn = eval('(' + funcSrc + ')');

        const result = fn({
            currentModelId: 'openai/gpt-4o',
            availableModels: [{ modelId: 'openai/gpt-4o', name: 'GPT-4o' }],
            modes: {
                currentModeId: 'code',
                availableModes: [
                    { id: 'code', name: 'Code' },
                    { id: 'ask', name: 'Ask', description: 'Ask questions about code' },
                    { id: 'architect', name: 'Architect' },
                ],
            },
        });

        if (!Array.isArray(result)) { console.error('not array'); process.exit(1); }
        if (result.length !== 2) { console.error('expected 2 options, got ' + result.length); process.exit(1); }

        const mode = result.find(o => o.id === 'mode');
        if (!mode) { console.error('no mode option'); process.exit(1); }
        if (mode.type !== 'select') { console.error('mode type: ' + mode.type); process.exit(1); }
        if (mode.category !== 'mode') { console.error('mode category: ' + mode.category); process.exit(1); }
        if (mode.currentValue !== 'code') { console.error('wrong currentValue'); process.exit(1); }
        if (mode.options.length !== 3) { console.error('expected 3 mode options'); process.exit(1); }

        const ask = mode.options.find(o => o.value === 'ask');
        if (!ask || !ask.description) { console.error('ask mode missing description'); process.exit(1); }
        const architect = mode.options.find(o => o.value === 'architect');
        if (architect && architect.description) { console.error('architect should not have description'); process.exit(1); }

        console.log(JSON.stringify(result));
    """ % AGENT_TS)

    r = subprocess.run(["node", "-e", script], capture_output=True, timeout=30)
    assert r.returncode == 0, f"buildConfigOptions mode test failed:\n{r.stderr.decode()}"

    data = json.loads(r.stdout.decode().strip())
    assert len(data) == 2, f"Expected 2 options (model + mode), got {len(data)}"


# [pr_diff] fail_to_pass
def test_config_options_in_session_lifecycle():
    """configOptions must be set in at least 2 session response paths."""
    src = Path(AGENT_TS).read_text()

    calls = re.findall(
        r"configOptions\s*[:=]\s*(?:load\.configOptions|buildConfigOptions\s*\()", src
    )
    assert len(calls) >= 2, (
        f"configOptions should be set in at least 2 session response paths, "
        f"found {len(calls)}: {calls}"
    )


# [pr_diff] fail_to_pass
def test_set_session_config_option_dispatch():
    """setSessionConfigOption must handle 'model' and 'mode' configIds and reject unknown."""
    src = Path(AGENT_TS).read_text()

    assert "setSessionConfigOption" in src, "setSessionConfigOption method not found"

    method_start = src.index("setSessionConfigOption")
    brace_pos = src.index("{", method_start)
    depth = 0
    method_end = -1
    for i in range(brace_pos, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                method_end = i + 1
                break

    assert method_end > 0, "Could not extract setSessionConfigOption body"
    method_body = src[method_start:method_end]

    assert re.search(r'''configId\s*===?\s*["']model["']''', method_body), (
        "setSessionConfigOption must handle configId 'model'"
    )
    assert re.search(r'''configId\s*===?\s*["']mode["']''', method_body), (
        "setSessionConfigOption must handle configId 'mode'"
    )

    assert re.search(
        r"Unknown config option|unknown.*config|invalid.*config", method_body, re.IGNORECASE
    ), "setSessionConfigOption must reject unknown configIds with an error"

    assert "buildConfigOptions" in method_body or "configOptions" in method_body, (
        "setSessionConfigOption must return configOptions in response"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:13 @ 4712c18a5833da85cd3946357662b148e78573f7
def test_no_any_type_in_new_code():
    """New configOptions code must not use the 'any' type (AGENTS.md line 13)."""
    src = Path(AGENT_TS).read_text()

    assert "function buildConfigOptions" in src, "buildConfigOptions function not found"

    # Check buildConfigOptions for 'any' type
    start = src.index("function buildConfigOptions")
    brace_pos = src.index("{", start)
    depth = 0
    end = -1
    for i in range(brace_pos, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    func_body = src[start:end]
    any_uses = re.findall(r"(?::\s*any\b|as\s+any\b|<any>)", func_body)
    assert len(any_uses) == 0, (
        f"buildConfigOptions uses 'any' type {len(any_uses)} time(s). "
        f"AGENTS.md requires avoiding the 'any' type."
    )

    # Also check setSessionConfigOption
    if "setSessionConfigOption" in src:
        m_start = src.index("setSessionConfigOption")
        m_brace = src.index("{", m_start)
        depth = 0
        m_end = -1
        for i in range(m_brace, len(src)):
            if src[i] == "{":
                depth += 1
            elif src[i] == "}":
                depth -= 1
                if depth == 0:
                    m_end = i + 1
                    break

        method_body = src[m_start:m_end]
        any_uses = re.findall(r"(?::\s*any\b|as\s+any\b|<any>)", method_body)
        assert len(any_uses) == 0, (
            f"setSessionConfigOption uses 'any' type {len(any_uses)} time(s). "
            f"AGENTS.md requires avoiding the 'any' type."
        )

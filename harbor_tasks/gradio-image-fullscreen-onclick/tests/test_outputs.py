"""
Task: gradio-image-fullscreen-onclick
Repo: gradio-app/gradio @ 4a4c7f3b0d6fd8009fdafc580d5852984f961db1
PR:   13004

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

import pytest

REPO = "/workspace"
FILE = Path(REPO) / "js/image/shared/ImagePreview.svelte"


def _run_node(script: str, timeout: int = 15) -> subprocess.CompletedProcess:
    """Execute a Node.js script in the repo directory."""
    tmp = Path(REPO) / "_eval_tmp.cjs"
    tmp.write_text(script)
    try:
        return subprocess.run(
            ["node", str(tmp)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        tmp.unlink(missing_ok=True)


# Node.js extraction script: reads ImagePreview.svelte, finds the
# FullscreenButton block, and extracts the onclick handler body using
# brace-counting (robust against nested {}).
_EXTRACT_JS = """\
const fs = require('fs');
const src = fs.readFileSync('js/image/shared/ImagePreview.svelte', 'utf8');

const result = {
    blockFound: false,
    hasOnclick: false,
    hasOnFullscreen: false,
    handler: null,
};

const blockMatch = src.match(/<FullscreenButton[\\s\\S]*?\\/>/);
if (!blockMatch) {
    console.log(JSON.stringify(result));
    process.exit(0);
}

result.blockFound = true;
const block = blockMatch[0];
result.hasOnFullscreen = block.includes('on:fullscreen');

const onclickIdx = block.indexOf('onclick');
if (onclickIdx === -1) {
    console.log(JSON.stringify(result));
    process.exit(0);
}

result.hasOnclick = true;

// Extract handler body using brace-counting (handles nested {})
const eqIdx = block.indexOf('=', onclickIdx);
const braceStart = block.indexOf('{', eqIdx);
if (braceStart === -1) {
    console.log(JSON.stringify(result));
    process.exit(0);
}
let depth = 1, i = braceStart + 1;
while (i < block.length && depth > 0) {
    if (block[i] === '{') depth++;
    else if (block[i] === '}') depth--;
    i++;
}
result.handler = block.substring(braceStart + 1, i - 1).trim();

console.log(JSON.stringify(result));
"""


@pytest.fixture(scope="module")
def svelte_src():
    """Read the ImagePreview.svelte source."""
    assert FILE.exists(), f"{FILE} not found"
    return FILE.read_text()


@pytest.fixture(scope="module")
def handler_info():
    """Extract FullscreenButton onclick handler info via Node.js."""
    r = _run_node(_EXTRACT_JS)
    assert r.returncode == 0, f"Node extraction failed: {r.stderr}"
    return json.loads(r.stdout)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

def test_svelte_syntax(svelte_src):
    """ImagePreview.svelte must have valid Svelte structure (script + template)."""
    assert "<script" in svelte_src, "Missing <script> tag"
    assert "FullscreenButton" in svelte_src, "FullscreenButton component missing"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_onclick_prop_present(handler_info):
    """FullscreenButton must receive an onclick prop (not on:fullscreen directive)."""
    assert handler_info["blockFound"], "FullscreenButton not found in template"
    assert handler_info["hasOnclick"], "No onclick prop found on FullscreenButton"


def test_onclick_updates_state(handler_info):
    """onclick handler must set fullscreen to the value passed by FullscreenButton.

    Extracts the handler via brace-counting in Node.js, then evaluates it
    with multiple input values to verify it updates state correctly.
    """
    handler_src = handler_info.get("handler")
    assert handler_src, "Could not extract onclick handler from FullscreenButton"

    test_script = f"""\
const handlerSrc = {json.dumps(handler_src)};
const results = [];
for (const val of [true, false, true, false]) {{
    let fullscreen = !val;
    const dispatch = () => {{}};
    const handler = eval('(' + handlerSrc + ')');
    handler(val);
    results.push({{ input: val, fullscreen }});
}}
console.log(JSON.stringify(results));
"""

    r = _run_node(test_script)
    assert r.returncode == 0, f"Handler evaluation failed:\n{r.stderr}"
    results = json.loads(r.stdout.strip())
    for state in results:
        assert state["fullscreen"] == state["input"], \
            f"onclick({state['input']}) did not set fullscreen = {state['input']}"


def test_onclick_dispatches_event(handler_info):
    """onclick handler must dispatch a fullscreen event for parent components.

    Verifies dispatch is called with correct arguments for multiple input values.
    """
    handler_src = handler_info.get("handler")
    assert handler_src, "Could not extract onclick handler from FullscreenButton"

    test_script = f"""\
const handlerSrc = {json.dumps(handler_src)};
const dispatched = [];
for (const val of [true, false]) {{
    let fullscreen = !val;
    const dispatch = (event, detail) => dispatched.push({{ event, detail }});
    const handler = eval('(' + handlerSrc + ')');
    handler(val);
}}
console.log(JSON.stringify(dispatched));
"""

    r = _run_node(test_script)
    assert r.returncode == 0, f"Handler evaluation failed:\n{r.stderr}"
    dispatched = json.loads(r.stdout.strip())
    assert len(dispatched) >= 2, \
        f"Expected dispatch called for each input, got {len(dispatched)} calls"
    for call in dispatched:
        assert "fullscreen" in str(call.get("event", "")).lower(), \
            f"Dispatch event should reference fullscreen, got: {call}"


def test_no_on_fullscreen_directive(handler_info):
    """Broken on:fullscreen event directive must be removed from FullscreenButton."""
    assert handler_info["blockFound"], "FullscreenButton not found in template"
    assert not handler_info["hasOnFullscreen"], \
        "FullscreenButton still uses broken on:fullscreen directive"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

def test_download_link_preserved(svelte_src):
    """DownloadLink component must still be rendered in the template."""
    assert "<DownloadLink" in svelte_src, "DownloadLink was removed from template"


def test_share_button_preserved(svelte_src):
    """ShareButton component must still be rendered in the template."""
    assert "ShareButton" in svelte_src, "ShareButton reference removed from template"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

def test_tab_indentation(svelte_src):
    """Modified file must use tab indentation consistent with surrounding code."""
    lines = svelte_src.split("\n")
    tab_lines = sum(1 for l in lines if l.startswith("\t"))
    space_lines = sum(1 for l in lines if re.match(r"^ {2,}[^ ]", l) and not l.startswith("\t"))
    assert tab_lines > 0, "No tab-indented lines found"
    assert space_lines < 5, \
        f"Too many space-indented lines ({space_lines}), file uses tabs"


def test_no_trailing_whitespace(svelte_src):
    """Modified Svelte file must not have trailing whitespace on lines."""
    for i, line in enumerate(svelte_src.split("\n"), 1):
        assert line == line.rstrip(), \
            f"Line {i} has trailing whitespace: {line!r}"

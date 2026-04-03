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


@pytest.fixture(scope="module")
def svelte_src():
    """Read the ImagePreview.svelte source."""
    assert FILE.exists(), f"{FILE} not found"
    return FILE.read_text()


@pytest.fixture(scope="module")
def fullscreen_button_block(svelte_src):
    """Extract the FullscreenButton component usage block from the template."""
    # Find the FullscreenButton component tag (possibly multi-line)
    # Match from <FullscreenButton to the closing />
    m = re.search(
        r"<FullscreenButton\b([\s\S]*?)/>",
        svelte_src,
    )
    assert m is not None, "FullscreenButton component not found in template"
    return m.group(0)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_svelte_syntax(svelte_src):
    """ImagePreview.svelte must have valid Svelte structure (script + template)."""
    # Verify basic Svelte file structure: has <script> and template content
    assert "<script" in svelte_src, "Missing <script> tag"
    assert "FullscreenButton" in svelte_src, "FullscreenButton component missing from file"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_onclick_prop_present(fullscreen_button_block):
    """FullscreenButton must receive an onclick prop (not on:fullscreen directive)."""
    assert "onclick" in fullscreen_button_block, \
        "No onclick prop found on FullscreenButton"


# [pr_diff] fail_to_pass
def test_onclick_updates_state():
    """onclick handler must set fullscreen to the value passed by FullscreenButton.

    We extract the onclick handler from the Svelte source and evaluate it in Node.js
    with multiple input values to verify it updates state correctly.
    """
    src = FILE.read_text()
    # Extract the onclick handler: onclick={(is_fullscreen) => { ... }}
    # or onclick={someFunction} etc.
    m = re.search(
        r"<FullscreenButton\b[\s\S]*?onclick\s*=\s*\{([\s\S]*?)\}\s*(?=\n\s*[/\w{])",
        src,
    )
    assert m is not None, "Could not extract onclick handler from FullscreenButton"
    handler_src = m.group(1).strip()

    # Test with multiple values: true, false, true again
    test_script = f"""
    const results = [];
    for (const val of [true, false, true, false]) {{
      let fullscreen = !val;  // start with opposite
      const dispatch = (...args) => {{ results.push(args); }};
      const handler = {handler_src};
      handler(val);
      results.push({{ input: val, fullscreen }});
    }}
    console.log(JSON.stringify(results));
    """

    r = subprocess.run(
        ["node", "-e", test_script],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Handler evaluation failed:\n{r.stderr}"

    data = json.loads(r.stdout)
    # data alternates: dispatch args, state check, dispatch args, state check, ...
    # Each pair: dispatch call args, then {input, fullscreen}
    for i in range(0, len(data), 2):
        state = data[i + 1]
        assert state["fullscreen"] == state["input"], \
            f"onclick({state['input']}) did not set fullscreen = {state['input']}"


# [pr_diff] fail_to_pass
def test_onclick_dispatches_event():
    """onclick handler must dispatch a fullscreen event for parent components.

    Verifies dispatch is called with correct arguments for multiple input values.
    """
    src = FILE.read_text()
    m = re.search(
        r"<FullscreenButton\b[\s\S]*?onclick\s*=\s*\{([\s\S]*?)\}\s*(?=\n\s*[/\w{])",
        src,
    )
    assert m is not None, "Could not extract onclick handler from FullscreenButton"
    handler_src = m.group(1).strip()

    test_script = f"""
    const dispatched = [];
    for (const val of [true, false]) {{
      let fullscreen = !val;
      const dispatch = (event, detail) => {{ dispatched.push({{ event, detail }}); }};
      const handler = {handler_src};
      handler(val);
    }}
    console.log(JSON.stringify(dispatched));
    """

    r = subprocess.run(
        ["node", "-e", test_script],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Handler evaluation failed:\n{r.stderr}"

    dispatched = json.loads(r.stdout)
    assert len(dispatched) >= 2, \
        f"Expected dispatch to be called for each input, got {len(dispatched)} calls"

    # Verify the event name includes "fullscreen"
    for call in dispatched:
        assert "fullscreen" in str(call.get("event", "")).lower(), \
            f"Dispatch event name should reference fullscreen, got: {call}"


# [pr_diff] fail_to_pass
def test_no_on_fullscreen_directive(fullscreen_button_block):
    """Broken on:fullscreen event directive must be removed from FullscreenButton."""
    assert "on:fullscreen" not in fullscreen_button_block, \
        "FullscreenButton still uses broken on:fullscreen directive"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_download_link_preserved(svelte_src):
    """DownloadLink component must still be rendered in the template."""
    assert "DownloadLink" in svelte_src, "DownloadLink was removed from template"
    assert re.search(r"<DownloadLink\b", svelte_src), \
        "DownloadLink component tag not found"


# [pr_diff] pass_to_pass
def test_share_button_preserved(svelte_src):
    """ShareButton component must still be rendered in the template."""
    # ShareButton is conditionally rendered — check it exists in the template
    assert re.search(r"<ShareButton\b", svelte_src) or \
        re.search(r"ShareButton", svelte_src), \
        "ShareButton reference removed from template"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:45 @ 4a4c7f3b0d6fd8009fdafc580d5852984f961db1
def test_tab_indentation(svelte_src):
    """Modified file must use tab indentation consistent with surrounding code."""
    lines = svelte_src.split("\n")
    tab_lines = sum(1 for l in lines if l.startswith("\t"))
    space_lines = sum(1 for l in lines if re.match(r"^ {2,}[^ ]", l) and not l.startswith("\t"))
    assert tab_lines > 0, "No tab-indented lines found"
    assert space_lines < 5, \
        f"Too many space-indented lines ({space_lines}), file uses tabs"


# [agent_config] pass_to_pass — AGENTS.md:44 @ 4a4c7f3b0d6fd8009fdafc580d5852984f961db1
def test_no_trailing_whitespace(svelte_src):
    """Modified Svelte file must not have trailing whitespace on lines."""
    for i, line in enumerate(svelte_src.split("\n"), 1):
        assert line == line.rstrip(), \
            f"Line {i} has trailing whitespace: {line!r}"

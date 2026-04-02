"""
Task: gradio-chatinterface-fill-height-scale
Repo: gradio-app/gradio @ bb127c74bd6301e3782e0ce4744161ae976a8481
PR:   12956

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/gradio"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python file must parse without syntax errors."""
    import ast

    src = Path(f"{REPO}/gradio/chat_interface.py").read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_fill_height_no_hardcoded_400():
    """ChatInterface(fill_height=True) must not hardcode chatbot height to 400.

    Bug: `height=400 if self.fill_height else None` sets height=400 when
    fill_height=True, blocking CSS flex expansion.
    Fix: remove the height override so Chatbot uses its own default.
    """
    from gradio import ChatInterface, Chatbot

    default_height = Chatbot().height

    # Test with multiple callbacks to prevent hardcoding
    callbacks = [
        lambda msg, hist: f"Echo: {msg}",
        lambda msg, hist: msg.upper(),
        lambda msg, hist: "fixed",
    ]

    for i, fn in enumerate(callbacks):
        ci = ChatInterface(fn=fn, fill_height=True)
        assert ci.chatbot.height == default_height, (
            f"Callback {i}: fill_height=True chatbot height={ci.chatbot.height}, "
            f"expected Chatbot default={default_height}"
        )


# [pr_diff] fail_to_pass
def test_fill_height_height_not_conditional():
    """Chatbot height must be the same regardless of fill_height value.

    Bug: height differs based on fill_height (400 vs None).
    Fix: height is always Chatbot's own default, fill_height only affects layout.
    """
    from gradio import ChatInterface

    def echo(msg, hist):
        return f"Echo: {msg}"

    ci_true = ChatInterface(fn=echo, fill_height=True)
    ci_false = ChatInterface(fn=echo, fill_height=False)

    assert ci_true.chatbot.height == ci_false.chatbot.height, (
        f"Heights differ: fill_height=True={ci_true.chatbot.height}, "
        f"fill_height=False={ci_false.chatbot.height}"
    )

    # Also verify with a different callback
    def upper(msg, hist):
        return msg.upper()

    ci_true2 = ChatInterface(fn=upper, fill_height=True)
    ci_false2 = ChatInterface(fn=upper, fill_height=False)
    assert ci_true2.chatbot.height == ci_false2.chatbot.height


# [pr_diff] fail_to_pass
def test_init_svelte_scale_from_fill_height():
    """init.svelte.ts sets scale on root column based on fill_height config.

    # AST-only because: Svelte/TS cannot be executed from Python without
    # a full frontend build + browser runtime.
    """
    content = Path(f"{REPO}/js/core/src/init.svelte.ts").read_text()
    lines = content.splitlines()
    found = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
            continue
        if "scale" in line and "fill_height" in line:
            context_start = max(0, i - 40)
            context_end = min(len(lines), i + 20)
            context = "\n".join(lines[context_start:context_end])
            if "column" in context:
                found = True
                break

    assert found, "init.svelte.ts missing scale assignment from fill_height in column context"


# [pr_diff] fail_to_pass
def test_blocks_svelte_forwards_fill_height():
    """Blocks.svelte forwards fill_height in config to AppTree in >=2 contexts.

    # AST-only because: Svelte/TS cannot be executed from Python without
    # a full frontend build + browser runtime. The fix adds fill_height to both
    # the constructor and reload() config objects.
    """
    content = Path(f"{REPO}/js/core/src/Blocks.svelte").read_text()
    lines = content.splitlines()
    config_contexts = 0
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
            i += 1
            continue
        if "fill_height" in lines[i]:
            context_start = max(0, i - 15)
            context_end = min(len(lines), i + 15)
            context = "\n".join(lines[context_start:context_end])
            config_keywords = ["autoscroll", "api_prefix", "max_file_size", "version"]
            if sum(1 for kw in config_keywords if kw in context) >= 2:
                config_contexts += 1
                i += 20  # skip ahead to avoid double-counting same block
                continue
        i += 1

    assert config_contexts >= 2, (
        f"Blocks.svelte has fill_height in {config_contexts} config contexts, need >=2"
    )


# [pr_diff] fail_to_pass
def test_types_ts_fill_height_in_appconfig():
    """types.ts AppConfig interface must include fill_height property.

    # AST-only because: TypeScript cannot be executed from Python.
    """
    content = Path(f"{REPO}/js/core/src/types.ts").read_text()

    # Find the AppConfig interface block and check for fill_height
    in_appconfig = False
    brace_depth = 0
    found = False
    started = False

    for line in content.splitlines():
        if "interface AppConfig" in line:
            in_appconfig = True
        if in_appconfig:
            brace_depth += line.count("{") - line.count("}")
            if "{" in line:
                started = True
            if "fill_height" in line:
                found = True
                break
            if started and brace_depth <= 0:
                break

    assert found, "types.ts AppConfig interface is missing fill_height property"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_fill_height_true_basic_functionality():
    """ChatInterface(fill_height=True) preserves basic chatbot functionality."""
    from gradio import ChatInterface

    callbacks = [
        lambda msg, hist: f"Echo: {msg}",
        lambda msg, hist: msg.upper(),
        lambda msg, hist: "",
    ]

    for fn in callbacks:
        ci = ChatInterface(fn=fn, fill_height=True)
        assert ci.chatbot is not None, "chatbot is None"
        assert ci.chatbot.scale == 1, f"chatbot.scale={ci.chatbot.scale}"
        assert ci.fill_height is True


# [pr_diff] pass_to_pass
def test_default_config_includes_fill_height():
    """Default ChatInterface config includes fill_height=True."""
    from gradio import ChatInterface

    def echo(msg, hist):
        return f"Echo: {msg}"

    ci = ChatInterface(fn=echo)
    assert ci.fill_height is True, f"fill_height={ci.fill_height}"
    config = ci.config
    assert "fill_height" in config, "fill_height not in config keys"
    assert config["fill_height"] is True, f"config fill_height={config['fill_height']}"


# [pr_diff] pass_to_pass
def test_fill_height_false_config_propagation():
    """ChatInterface(fill_height=False) config reflects fill_height=False."""
    from gradio import ChatInterface

    def echo(msg, hist):
        return f"Echo: {msg}"

    ci = ChatInterface(fn=echo, fill_height=False)
    config = ci.config
    fh = config.get("fill_height")
    assert fh is False, f"config fill_height={fh}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_chat_interface_not_stub():
    """chat_interface.py is substantive, not an empty stub."""
    src = Path(f"{REPO}/gradio/chat_interface.py").read_text()
    line_count = len(src.splitlines())
    assert line_count > 100, f"only {line_count} lines"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:43 @ bb127c74bd6301e3782e0ce4744161ae976a8481
def test_ruff_format_chat_interface():
    """Python code must be formatted with ruff (AGENTS.md line 43)."""
    r = subprocess.run(
        ["python3", "-m", "ruff", "format", "--check", "gradio/chat_interface.py"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    if r.returncode != 0:
        # Try ruff as standalone command
        r = subprocess.run(
            ["ruff", "format", "--check", "gradio/chat_interface.py"],
            cwd=REPO,
            capture_output=True,
            timeout=30,
        )
    assert r.returncode == 0, (
        f"ruff format check failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )

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
    Fix: height is always Chatbot\s
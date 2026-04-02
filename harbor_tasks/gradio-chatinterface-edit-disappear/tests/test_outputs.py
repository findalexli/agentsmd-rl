"""
Task: gradio-chatinterface-edit-disappear
Repo: gradio-app/gradio @ d5e1b8f6cb7473b70fc8c082589996d5e0402810
PR:   12997

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys

REPO = "/workspace/gradio"


def _get_ci(editable=True, type_="messages"):
    """Helper: create a ChatInterface for testing."""
    if REPO not in sys.path:
        sys.path.insert(0, REPO)
    from gradio import ChatInterface

    def echo(msg, hist):
        return f"Echo: {msg}"

    return ChatInterface(fn=echo, type=type_, editable=editable)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """chat_interface.py must parse without syntax errors."""
    import py_compile

    py_compile.compile(f"{REPO}/gradio/chat_interface.py", doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_edit_restores_message_before_response():
    """After editing a user message, the edited text must be visible in the
    chatbot before the response callback runs (the core bug).

    Tests multiple edit scenarios to prevent hardcoding."""
    sys.path.insert(0, REPO)
    from gradio.events import EditData

    ci = _get_ci(editable=True)

    test_cases = [
        ("hello", "hello edited"),
        ("what is 2+2?", "what is 3+3?"),
        ("", "now has content"),
    ]

    for original, edited in test_cases:
        history = [
            {"role": "user", "content": original},
            {"role": "assistant", "content": f"Echo: {original}"},
        ]
        edit_data = EditData(
            target=ci.chatbot,
            value=edited,
            index=0,
            _data={"index": 0, "value": edited},
        )
        result = ci._edit_message(history, edit_data)
        chatbot_after_edit, state_after_edit, saved_input = result

        # Path A: _edit_message itself already includes the edited message
        if (
            isinstance(chatbot_after_edit, list)
            and any(
                isinstance(m, dict) and m.get("content") == edited
                for m in chatbot_after_edit
            )
        ):
            continue

        # Path B: A chained _append_message_to_history restores the message
        restored = ci._append_message_to_history(saved_input, state_after_edit, "user")
        assert isinstance(restored, list), (
            f"_append_message_to_history returned {type(restored)}, expected list"
        )
        found = any(
            isinstance(m, dict) and m.get("content") == edited for m in restored
        )
        assert found, (
            f"Edited message '{edited}' not restored after _edit_message + "
            f"_append_message_to_history. Got: {restored}"
        )

        # Verify the append step is actually wired into the edit event chain
        chatbot_id = ci.chatbot._id
        chatbot_state_id = ci.chatbot_state._id
        saved_input_id = ci.saved_input._id
        has_append_dep = False
        for dep in ci.dependencies:
            input_ids = {inp for inp in dep.get("inputs", []) if isinstance(inp, int)}
            output_ids = {out for out in dep.get("outputs", []) if isinstance(out, int)}
            if (
                chatbot_id in output_ids
                and (saved_input_id in input_ids or chatbot_state_id in input_ids)
                and chatbot_state_id in input_ids
            ):
                has_append_dep = True
                break
        assert has_append_dep, (
            "_append_message_to_history is not chained in the edit event "
            "dependency graph"
        )


# [pr_diff] fail_to_pass
def test_edit_chain_has_append_step():
    """editable=True must register more append-to-chatbot deps than
    editable=False, proving the edit chain includes a restore step."""
    ci_edit = _get_ci(editable=True)
    ci_no_edit = _get_ci(editable=False)

    def count_append_deps(ci):
        chatbot_id = ci.chatbot._id
        chatbot_state_id = ci.chatbot_state._id
        count = 0
        for dep in ci.dependencies:
            input_ids = {inp for inp in dep.get("inputs", []) if isinstance(inp, int)}
            output_ids = {out for out in dep.get("outputs", []) if isinstance(out, int)}
            if chatbot_state_id in input_ids and chatbot_id in output_ids:
                count += 1
        return count

    edit_count = count_append_deps(ci_edit)
    no_edit_count = count_append_deps(ci_no_edit)

    if edit_count > no_edit_count:
        return  # The edit chain adds at least one extra append dep — good

    # Alternative fix: _edit_message itself restores the message (no new dep)
    sys.path.insert(0, REPO)
    from gradio.events import EditData

    for original, edited in [("hi", "hi edited"), ("foo", "bar")]:
        history = [
            {"role": "user", "content": original},
            {"role": "assistant", "content": f"Echo: {original}"},
        ]
        edit_data = EditData(
            target=ci_edit.chatbot,
            value=edited,
            index=0,
            _data={"index": 0, "value": edited},
        )
        result = ci_edit._edit_message(history, edit_data)
        chatbot_out = result[0]
        assert isinstance(chatbot_out, list) and any(
            isinstance(m, dict) and m.get("content") == edited for m in chatbot_out
        ), (
            f"editable=True has {edit_count} append deps (same as "
            f"{no_edit_count}) and _edit_message does not restore '{edited}'"
        )


# [pr_diff] fail_to_pass
def test_edit_chain_toggles_textbox_interactivity():
    """editable=True must register more textbox-output deps than editable=False,
    proving the edit chain adds disable/enable textbox interactivity steps."""
    ci_edit = _get_ci(editable=True)
    ci_no_edit = _get_ci(editable=False)

    def count_textbox_deps(ci):
        textbox_id = ci.textbox._id
        return sum(
            1
            for dep in ci.dependencies
            if textbox_id in {out for out in dep.get("outputs", []) if isinstance(out, int)}
        )

    edit_count = count_textbox_deps(ci_edit)
    no_edit_count = count_textbox_deps(ci_no_edit)

    assert edit_count > no_edit_count, (
        f"editable=True has {edit_count} textbox-output deps, "
        f"same as editable=False ({no_edit_count}). "
        "Edit chain should add at least 2 extra deps (disable before response, "
        "enable after)."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_submit_appends_message():
    """_append_message_to_history still works for normal submit flow."""
    ci = _get_ci(editable=False)

    # Test with multiple inputs to prevent hardcoding
    test_messages = ["test message", "what about spaces?", "", "unicode: αβγ 🎉"]

    history = []
    for msg in test_messages:
        history = ci._append_message_to_history(msg, history, "user")

    assert len(history) == len(test_messages)
    for i, msg in enumerate(test_messages):
        assert history[i]["content"] == msg
        assert history[i]["role"] == "user"


# [pr_diff] pass_to_pass
def test_editable_false_no_edit_event():
    """ChatInterface with editable=False must not register edit events."""
    ci = _get_ci(editable=False)
    for dep in ci.dependencies:
        for t in dep.get("targets", []):
            if isinstance(t, (list, tuple)) and len(t) >= 2 and t[1] == "edit":
                raise AssertionError("edit event found when editable=False")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:43 @ d5e1b8f6cb7473b70fc8c082589996d5e0402810
def test_ruff_lint_clean():
    """Python code is formatted with ruff — AGENTS.md:43."""
    r = subprocess.run(
        ["ruff", "check", "gradio/chat_interface.py", "--select", "E,W", "--quiet"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"ruff check failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )

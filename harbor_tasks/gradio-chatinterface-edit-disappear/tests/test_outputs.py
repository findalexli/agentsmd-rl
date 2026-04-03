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


def _get_ci(editable=True):
    """Helper: create a ChatInterface for testing."""
    if REPO not in sys.path:
        sys.path.insert(0, REPO)
    from gradio import ChatInterface

    def echo(msg, hist):
        return f"Echo: {msg}"

    return ChatInterface(fn=echo, editable=editable)


def _make_edit_data(ci, index, value, previous_value):
    """Create an EditData with correct constructor signature."""
    sys.path.insert(0, REPO)
    from gradio.events import EditData

    return EditData(
        target=ci.chatbot,
        data={"index": index, "value": value, "previous_value": previous_value},
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
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
    """After editing, the edited user message is visible in the chatbot
    before the response callback runs (the core bug).

    Traces the edit event chain to verify it includes an _append step,
    then calls the functions to verify the mechanism works."""
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
        ed = _make_edit_data(ci, index=0, value=edited, previous_value=original)
        chatbot_after, state_after, saved = ci._edit_message(history, ed)

        # Path A: _edit_message itself returns the edited message
        if isinstance(chatbot_after, list) and any(
            isinstance(m, dict) and m.get("content") == edited
            for m in chatbot_after
        ):
            continue

        # Path B: the edit chain must wire _append_message_to_history after _edit_message
        chatbot_id = ci.chatbot._id
        saved_id = ci.saved_input._id
        state_id = ci.chatbot_state._id

        # Find edit event root
        root_fn = None
        for fn in ci.fns.values():
            for tid, ename in fn.targets:
                if tid == chatbot_id and ename == "edit":
                    root_fn = fn
                    break
        assert root_fn is not None, "No edit event registered"

        # Trace the chain; look for an append dep:
        # inputs ⊇ {saved_input, chatbot_state}, outputs == {chatbot}
        has_append = False
        cur_id = root_fn._id
        visited = {cur_id}
        while True:
            next_fns = [
                f for f in ci.fns.values()
                if f.trigger_after == cur_id and f._id not in visited
            ]
            if not next_fns:
                break
            for fn in next_fns:
                visited.add(fn._id)
                fn_in = {c._id for c in fn.inputs}
                fn_out = {c._id for c in fn.outputs}
                if saved_id in fn_in and state_id in fn_in and fn_out == {chatbot_id}:
                    has_append = True
            cur_id = next_fns[0]._id

        assert has_append, (
            f"Edited message '{edited}' not restored: _edit_message truncates "
            f"history and the edit chain has no _append_message_to_history step"
        )

        # Verify the append mechanism actually works
        restored = ci._append_message_to_history(saved, state_after, "user")
        assert any(
            isinstance(m, dict) and m.get("content") == edited for m in restored
        ), f"_append_message_to_history did not restore '{edited}'"


# [pr_diff] fail_to_pass
def test_edit_chain_has_append_step():
    """editable=True registers an additional pure-append dep (outputs==[chatbot])
    compared to editable=False, proving the edit chain includes a restore step.

    Uses exact output matching to distinguish _append_message_to_history
    (outputs=[chatbot]) from submit_fn (outputs=[null_component, chatbot, ...])."""
    ci_edit = _get_ci(editable=True)
    ci_no_edit = _get_ci(editable=False)

    def count_pure_append_deps(ci):
        """Count fns where inputs ⊇ {saved_input, chatbot_state} and outputs == {chatbot}."""
        saved_id = ci.saved_input._id
        state_id = ci.chatbot_state._id
        bot_id = ci.chatbot._id
        return sum(
            1
            for fn in ci.fns.values()
            if {saved_id, state_id} <= {c._id for c in fn.inputs}
            and {c._id for c in fn.outputs} == {bot_id}
        )

    edit_count = count_pure_append_deps(ci_edit)
    no_edit_count = count_pure_append_deps(ci_no_edit)

    if edit_count > no_edit_count:
        return  # The edit chain adds at least one extra pure-append dep

    # Alternative fix: _edit_message itself restores the message (no new dep)
    for original, edited in [("hi", "hi edited"), ("foo", "bar")]:
        history = [
            {"role": "user", "content": original},
            {"role": "assistant", "content": f"Echo: {original}"},
        ]
        ed = _make_edit_data(ci_edit, index=0, value=edited, previous_value=original)
        chatbot_out = ci_edit._edit_message(history, ed)[0]
        assert isinstance(chatbot_out, list) and any(
            isinstance(m, dict) and m.get("content") == edited for m in chatbot_out
        ), (
            f"editable=True has {edit_count} pure-append deps (same as "
            f"{no_edit_count}) and _edit_message does not restore '{edited}'"
        )


# [pr_diff] fail_to_pass
def test_edit_chain_toggles_textbox_interactivity():
    """editable=True registers more textbox-output deps than editable=False,
    proving the edit chain adds disable/enable textbox interactivity steps."""
    ci_edit = _get_ci(editable=True)
    ci_no_edit = _get_ci(editable=False)

    def count_textbox_output_deps(ci):
        textbox_id = ci.textbox._id
        return sum(
            1
            for fn in ci.fns.values()
            if textbox_id in {c._id for c in fn.outputs}
        )

    edit_count = count_textbox_output_deps(ci_edit)
    no_edit_count = count_textbox_output_deps(ci_no_edit)

    assert edit_count > no_edit_count, (
        f"editable=True has {edit_count} textbox-output deps, "
        f"same as editable=False ({no_edit_count}). "
        "Edit chain should add at least 2 extra deps (disable before response, "
        "enable after)."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_submit_appends_message():
    """_append_message_to_history still works for normal submit flow."""
    ci = _get_ci(editable=False)

    test_messages = ["test message", "what about spaces?", "", "unicode: αβγ"]

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
    chatbot_id = ci.chatbot._id
    for fn in ci.fns.values():
        for target_id, event_name in fn.targets:
            if target_id == chatbot_id and event_name == "edit":
                raise AssertionError("edit event found when editable=False")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:43 @ d5e1b8f6cb7473b70fc8c082589996d5e0402810
def test_ruff_lint_clean():
    """Python code is formatted with ruff — AGENTS.md:43."""
    r = subprocess.run(
        ["ruff", "check", "gradio/chat_interface.py",
         "--select", "E9,F63,F7,F82", "--quiet"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"ruff check failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )

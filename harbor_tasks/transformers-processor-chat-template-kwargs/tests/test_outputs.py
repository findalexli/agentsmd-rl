"""
Task: transformers-processor-chat-template-kwargs
Repo: huggingface/transformers @ 6a056a16a856097cb0400ce9a48e96ab9d469e30
PR:   #44881

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/workspace/transformers"


def _discover_extraction_fn():
    """Find the template variable extraction function by behavior, not name.

    Scans chat_template_utils for any callable that accepts a Jinja2 template
    string and returns a set/frozenset of undeclared variable names.
    """
    sys.path.insert(0, f"{REPO}/src")
    import transformers.utils.chat_template_utils as ctm

    test_template = "{{ messages }}{{ bos_token }}{% if custom_var %}yes{% endif %}"
    expected = {"messages", "bos_token", "custom_var"}

    # Functions that exist in the base commit — skip these
    KNOWN_EXISTING = {
        "render_jinja_template",
        "get_json_schema",
        "_compile_jinja_template",
        "_render_with_assistant_indices",
    }

    for name in sorted(dir(ctm)):
        if name in KNOWN_EXISTING or name.startswith("__"):
            continue
        obj = getattr(ctm, name)
        if not callable(obj) or isinstance(obj, type):
            continue
        try:
            result = obj(test_template)
            if isinstance(result, (set, frozenset)) and expected.issubset(result):
                return name, obj
        except Exception:
            continue
    return None, None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import py_compile

    files = [
        "src/transformers/processing_utils.py",
        "src/transformers/utils/chat_template_utils.py",
        "src/transformers/models/smolvlm/processing_smolvlm.py",
        "src/transformers/models/voxtral/processing_voxtral.py",
    ]
    for f in files:
        py_compile.compile(f"{REPO}/{f}", doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_template_variable_extraction():
    """Extraction function finds undeclared Jinja2 variables including custom ones."""
    _, fn = _discover_extraction_fn()
    assert fn is not None, "No template variable extraction function found in chat_template_utils"

    # Standard + custom variables
    t1 = "{{ messages }}{{ bos_token }}{% if custom_var %}yes{% endif %}"
    v1 = fn(t1)
    assert isinstance(v1, (set, frozenset)), f"Expected set/frozenset, got {type(v1)}"
    assert {"messages", "bos_token", "custom_var"}.issubset(v1)

    # Loop variables must be excluded (only undeclared variables)
    t2 = (
        "{% for msg in messages %}{{ msg['role'] }}: {{ msg['content'] }}{% endfor %}"
        "{% if add_generation_prompt %}assistant:{% endif %}"
    )
    v2 = fn(t2)
    assert "messages" in v2
    assert "add_generation_prompt" in v2
    assert "msg" not in v2, f"Loop variable 'msg' should not be undeclared: {v2}"

    # Empty/literal template has no variables
    v3 = fn("Hello world")
    assert len(v3) == 0, f"Expected no variables, got {v3}"

    # Nested conditionals
    t4 = "{% if a %}{% if b %}{{ c }}{% endif %}{% endif %}"
    v4 = fn(t4)
    assert {"a", "b", "c"}.issubset(v4), f"Missing vars in {v4}"


# [pr_diff] fail_to_pass
def test_extraction_varies_by_template():
    """Extraction is dynamic (not a hardcoded list) — different templates yield different results."""
    _, fn = _discover_extraction_fn()
    assert fn is not None, "No extraction function found"

    v1 = fn("{{ x }}{{ y }}")
    v2 = fn("{{ z }}")
    assert "x" in v1 and "y" in v1, f"Expected x,y in {v1}"
    assert "z" in v2 and "x" not in v2, f"Expected only z in {v2}"

    # Template with many custom vars
    v3 = fn("{{ num_frames }}{{ fps }}{{ custom_flag }}{{ messages }}")
    assert {"num_frames", "fps", "custom_flag", "messages"}.issubset(v3)


# [pr_diff] fail_to_pass
def test_kwargs_separation():
    """Template introspection correctly separates template vars from processor kwargs."""
    _, fn = _discover_extraction_fn()
    assert fn is not None, "No extraction function found"

    template = (
        "{% for msg in messages %}{{ msg['content'] }}{% endfor %}"
        "{% if add_generation_prompt %}assistant: {% endif %}"
    )
    variables = fn(template)

    # Template vars correctly identified
    assert "messages" in variables
    assert "add_generation_prompt" in variables

    # Processor kwargs should NOT be template variables
    for k in ["padding", "max_length", "return_tensors", "truncation"]:
        assert k not in variables, f"'{k}' should not be a template variable"

    # Simulate the separation logic the fix enables
    all_kwargs = {
        "messages": [{"role": "user", "content": "hi"}],
        "add_generation_prompt": True,
        "padding": "max_length",
        "max_length": 50,
    }
    processor_kwargs = {k: v for k, v in all_kwargs.items() if k not in variables}
    assert "padding" in processor_kwargs
    assert "max_length" in processor_kwargs
    assert "messages" not in processor_kwargs
    assert "add_generation_prompt" not in processor_kwargs

    # Custom variable in a different template routes correctly
    t2 = "{% for msg in messages %}{{ msg.content }}{% endfor %}{% if custom_flag %}yes{% endif %}"
    v2 = fn(t2)
    proc2 = {k: v for k, v in {"custom_flag": True, "padding": "max_length"}.items() if k not in v2}
    assert "custom_flag" not in proc2, "custom_flag is a template var, should not be in processor_kwargs"
    assert "padding" in proc2, "padding is always a processor kwarg"


# [pr_diff] fail_to_pass
def test_apply_chat_template_uses_introspection():
    """apply_chat_template calls the extraction function for kwarg routing."""
    import importlib
    from unittest.mock import MagicMock, patch

    sys.path.insert(0, f"{REPO}/src")
    import transformers.processing_utils as pu
    from transformers.processing_utils import ProcessorMixin

    fn_name, original_fn = _discover_extraction_fn()
    assert fn_name is not None, "No extraction function found"

    # Verify the function is imported into processing_utils
    fn_in_pu = getattr(pu, fn_name, None)
    assert fn_in_pu is not None, f"{fn_name} not imported into processing_utils"

    # Track whether apply_chat_template calls it
    call_log = []

    def tracking_wrapper(t):
        call_log.append(t)
        return original_fn(t)

    template = '{% for msg in messages %}{{ msg["content"] }}{% endfor %}'
    mock_self = MagicMock()
    mock_self.chat_template = {"default": template}
    mock_self.tokenizer.special_tokens_map = {}
    mock_self.tokenizer.__class__.__name__ = "TestTokenizer"

    with patch.object(pu, fn_name, side_effect=tracking_wrapper):
        try:
            ProcessorMixin.apply_chat_template(
                mock_self,
                [{"role": "user", "content": "hello"}],
            )
        except Exception:
            pass  # May fail due to mock limitations; we only care about the call

    assert len(call_log) > 0, f"apply_chat_template did NOT call {fn_name}"
    assert call_log[0] == template, f"Called with wrong template: {call_log[0]}"


# [pr_diff] fail_to_pass
def test_extraction_cached():
    """Extraction function caches results for performance."""
    _, fn = _discover_extraction_fn()
    assert fn is not None, "No extraction function found"

    t = "{{ messages }}{{ custom }}"
    r1 = fn(t)
    r2 = fn(t)

    cached = False
    # functools.lru_cache / functools.cache expose cache_info()
    if hasattr(fn, "cache_info"):
        info = fn.cache_info()
        cached = info.hits >= 1
    # Cached functions return the same object (identity check)
    elif id(r1) == id(r2):
        cached = True

    assert cached, "Extraction function does not appear to be cached"

    # Different inputs must produce different cached results
    r3 = fn("{{ other_var }}")
    assert r3 != r1, "Different templates should not return same result"


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — style enforcement
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — AGENTS.md:2 @ 6a056a16a856097cb0400ce9a48e96ab9d469e30
def test_ruff_style_check():
    """Modified Python files pass ruff linting (make style requirement from AGENTS.md)."""
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True,
    )
    files = [
        f"{REPO}/src/transformers/processing_utils.py",
        f"{REPO}/src/transformers/utils/chat_template_utils.py",
        f"{REPO}/src/transformers/models/smolvlm/processing_smolvlm.py",
        f"{REPO}/src/transformers/models/voxtral/processing_voxtral.py",
    ]
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check"] + files,
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, f"ruff check failed:\n{result.stdout}\n{result.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_render_jinja_template_backward_compat():
    """render_jinja_template still works after changes."""
    sys.path.insert(0, f"{REPO}/src")
    from transformers.utils.chat_template_utils import render_jinja_template

    template = '{% for msg in messages %}{{ msg["role"] }}: {{ msg["content"] }}\n{% endfor %}'
    conversations = [[{"role": "user", "content": "Hello"}]]
    prompt, indices = render_jinja_template(
        conversations=conversations,
        chat_template=template,
        add_generation_prompt=False,
    )
    assert "user: Hello" in prompt[0], f"Unexpected prompt: {prompt}"

    # Batched conversations
    conversations2 = [
        [{"role": "user", "content": "Hi"}],
        [{"role": "user", "content": "Bye"}],
    ]
    prompt2, _ = render_jinja_template(
        conversations=conversations2,
        chat_template=template,
        add_generation_prompt=False,
    )
    assert len(prompt2) == 2
    assert "Hi" in prompt2[0]
    assert "Bye" in prompt2[1]

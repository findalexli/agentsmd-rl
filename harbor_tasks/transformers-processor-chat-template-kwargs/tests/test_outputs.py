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


def _run_python_code(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo environment via subprocess."""
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
        env={"PYTHONPATH": f"{REPO}/src"},
    )


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
# Fail-to-pass (pr_diff) — core behavioral tests using subprocess
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_template_variable_extraction_subprocess():
    """Extraction function exists and finds undeclared Jinja2 variables including custom ones."""
    code = """
import sys
sys.path.insert(0, "/workspace/transformers/src")

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

fn = None
for name in sorted(dir(ctm)):
    if name in KNOWN_EXISTING or name.startswith("__"):
        continue
    obj = getattr(ctm, name)
    if not callable(obj) or isinstance(obj, type):
        continue
    try:
        result = obj(test_template)
        if isinstance(result, (set, frozenset)) and expected.issubset(result):
            fn = obj
            break
    except Exception:
        continue

assert fn is not None, "No template variable extraction function found in chat_template_utils"

# Test standard + custom variables
t1 = "{{ messages }}{{ bos_token }}{% if custom_var %}yes{% endif %}"
v1 = fn(t1)
assert isinstance(v1, (set, frozenset)), f"Expected set/frozenset, got {type(v1)}"
assert {"messages", "bos_token", "custom_var"}.issubset(v1), f"Missing vars: {v1}"

# Loop variables must be excluded
t2 = (
    "{% for msg in messages %}{{ msg['role'] }}: {{ msg['content'] }}{% endfor %}"
    "{% if add_generation_prompt %}assistant:{% endif %}"
)
v2 = fn(t2)
assert "messages" in v2, f"messages not in {v2}"
assert "add_generation_prompt" in v2, f"add_generation_prompt not in {v2}"
assert "msg" not in v2, f"Loop variable 'msg' should not be undeclared: {v2}"

# Empty/literal template
v3 = fn("Hello world")
assert len(v3) == 0, f"Expected no variables, got {v3}"

# Nested conditionals
t4 = "{% if a %}{% if b %}{{ c }}{% endif %}{% endif %}"
v4 = fn(t4)
assert {"a", "b", "c"}.issubset(v4), f"Missing vars in {v4}"

print("PASS")
"""
    r = _run_python_code(code, timeout=30)
    assert r.returncode == 0, f"Test failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_extraction_is_dynamic():
    """Extraction varies by template (dynamic, not hardcoded)."""
    code = """
import sys
sys.path.insert(0, "/workspace/transformers/src")

import transformers.utils.chat_template_utils as ctm

test_template = "{{ messages }}{{ bos_token }}{% if custom_var %}yes{% endif %}"
expected = {"messages", "bos_token", "custom_var"}

KNOWN_EXISTING = {
    "render_jinja_template",
    "get_json_schema",
    "_compile_jinja_template",
    "_render_with_assistant_indices",
}

fn = None
for name in sorted(dir(ctm)):
    if name in KNOWN_EXISTING or name.startswith("__"):
        continue
    obj = getattr(ctm, name)
    if not callable(obj) or isinstance(obj, type):
        continue
    try:
        result = obj(test_template)
        if isinstance(result, (set, frozenset)) and expected.issubset(result):
            fn = obj
            break
    except Exception:
        continue

assert fn is not None, "No extraction function found"

v1 = fn("{{ x }}{{ y }}")
v2 = fn("{{ z }}")
assert "x" in v1 and "y" in v1, f"Expected x,y in {v1}"
assert "z" in v2 and "x" not in v2, f"Expected only z in {v2}"

# Template with many custom vars
v3 = fn("{{ num_frames }}{{ fps }}{{ custom_flag }}{{ messages }}")
assert {"num_frames", "fps", "custom_flag", "messages"}.issubset(v3), f"Missing in {v3}"

print("PASS")
"""
    r = _run_python_code(code, timeout=30)
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_extraction_cached():
    """Extraction function uses caching for performance."""
    code = """
import sys
sys.path.insert(0, "/workspace/transformers/src")

import transformers.utils.chat_template_utils as ctm

test_template = "{{ messages }}{{ bos_token }}{% if custom_var %}yes{% endif %}"
expected = {"messages", "bos_token", "custom_var"}

KNOWN_EXISTING = {
    "render_jinja_template",
    "get_json_schema",
    "_compile_jinja_template",
    "_render_with_assistant_indices",
}

fn = None
for name in sorted(dir(ctm)):
    if name in KNOWN_EXISTING or name.startswith("__"):
        continue
    obj = getattr(ctm, name)
    if not callable(obj) or isinstance(obj, type):
        continue
    try:
        result = obj(test_template)
        if isinstance(result, (set, frozenset)) and expected.issubset(result):
            fn = obj
            break
    except Exception:
        continue

assert fn is not None, "No extraction function found"

t = "{{ messages }}{{ custom }}"
r1 = fn(t)
r2 = fn(t)

# Check for lru_cache / functools.cache
cached = False
if hasattr(fn, "cache_info"):
    info = fn.cache_info()
    cached = info.hits >= 1
# If no cache_info, check if same object returned
elif r1 is r2:
    cached = True

assert cached, "Extraction function does not appear to be cached"

# Different inputs produce different results
r3 = fn("{{ other_var }}")
assert r3 != r1, "Different templates should not return same result"

print("PASS")
"""
    r = _run_python_code(code, timeout=30)
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_processing_utils_imports_extraction():
    """processing_utils imports and uses the extraction function for kwarg routing."""
    code = """
import sys
sys.path.insert(0, "/workspace/transformers/src")

# First discover the extraction function name
import transformers.utils.chat_template_utils as ctm

test_template = "{{ messages }}{{ bos_token }}{% if custom_var %}yes{% endif %}"
expected = {"messages", "bos_token", "custom_var"}

KNOWN_EXISTING = {
    "render_jinja_template",
    "get_json_schema",
    "_compile_jinja_template",
    "_render_with_assistant_indices",
}

fn_name = None
for name in sorted(dir(ctm)):
    if name in KNOWN_EXISTING or name.startswith("__"):
        continue
    obj = getattr(ctm, name)
    if not callable(obj) or isinstance(obj, type):
        continue
    try:
        result = obj(test_template)
        if isinstance(result, (set, frozenset)) and expected.issubset(result):
            fn_name = name
            break
    except Exception:
        continue

assert fn_name is not None, "Could not discover extraction function name"

# Now check that processing_utils imports it
import transformers.processing_utils as pu

fn_in_pu = getattr(pu, fn_name, None)
assert fn_in_pu is not None, f"{fn_name} not imported into processing_utils"

# Check that it appears in the source
source_file = "/workspace/transformers/src/transformers/processing_utils.py"
with open(source_file) as f:
    source = f.read()

# Should be imported from chat_template_utils
assert f"from .utils.chat_template_utils import" in source or \
       "from transformers.utils.chat_template_utils import" in source or \
       f"{fn_name}" in source, f"{fn_name} not referenced in processing_utils"

print("PASS")
"""
    r = _run_python_code(code, timeout=30)
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_kwargs_separation_behavior():
    """Template introspection correctly separates template vars from processor kwargs."""
    code = """
import sys
sys.path.insert(0, "/workspace/transformers/src")

import transformers.utils.chat_template_utils as ctm

test_template = "{{ messages }}{{ bos_token }}{% if custom_var %}yes{% endif %}"
expected = {"messages", "bos_token", "custom_var"}

KNOWN_EXISTING = {
    "render_jinja_template",
    "get_json_schema",
    "_compile_jinja_template",
    "_render_with_assistant_indices",
}

fn = None
for name in sorted(dir(ctm)):
    if name in KNOWN_EXISTING or name.startswith("__"):
        continue
    obj = getattr(ctm, name)
    if not callable(obj) or isinstance(obj, type):
        continue
    try:
        result = obj(test_template)
        if isinstance(result, (set, frozenset)) and expected.issubset(result):
            fn = obj
            break
    except Exception:
        continue

assert fn is not None, "No extraction function found"

# Test template separation
template = (
    "{% for msg in messages %}{{ msg['content'] }}{% endfor %}"
    "{% if add_generation_prompt %}assistant: {% endif %}"
)
variables = fn(template)

assert "messages" in variables, f"messages should be a template var"
assert "add_generation_prompt" in variables, f"add_generation_prompt should be a template var"

# Processor kwargs should NOT be template variables
for k in ["padding", "max_length", "return_tensors", "truncation"]:
    assert k not in variables, f"'{k}' should not be a template variable"

# Simulate the separation logic
all_kwargs = {
    "messages": [{"role": "user", "content": "hi"}],
    "add_generation_prompt": True,
    "padding": "max_length",
    "max_length": 50,
}
processor_kwargs = {k: v for k, v in all_kwargs.items() if k not in variables}
assert "padding" in processor_kwargs, "padding should be in processor_kwargs"
assert "max_length" in processor_kwargs, "max_length should be in processor_kwargs"
assert "messages" not in processor_kwargs, "messages should NOT be in processor_kwargs"
assert "add_generation_prompt" not in processor_kwargs, "add_generation_prompt should NOT be in processor_kwargs"

# Custom variable test
t2 = "{% for msg in messages %}{{ msg.content }}{% endfor %}{% if custom_flag %}yes{% endif %}"
v2 = fn(t2)
proc2 = {k: v for k, v in {"custom_flag": True, "padding": "max_length"}.items() if k not in v2}
assert "custom_flag" not in proc2, "custom_flag is a template var, should not be in processor_kwargs"
assert "padding" in proc2, "padding is always a processor kwarg"

print("PASS")
"""
    r = _run_python_code(code, timeout=30)
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression tests
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_render_jinja_template_backward_compat():
    """render_jinja_template still works after changes (subprocess execution)."""
    code = """
import sys
sys.path.insert(0, "/workspace/transformers/src")

from transformers.utils.chat_template_utils import render_jinja_template

template = '{% for msg in messages %}{{ msg["role"] }}: {{ msg["content"] }}\\n{% endfor %}'
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
assert len(prompt2) == 2, f"Expected 2 prompts, got {len(prompt2)}"
assert "Hi" in prompt2[0], f"'Hi' not in {prompt2[0]}"
assert "Bye" in prompt2[1], f"'Bye' not in {prompt2[1]}"

print("PASS")
"""
    r = _run_python_code(code, timeout=30)
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout


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

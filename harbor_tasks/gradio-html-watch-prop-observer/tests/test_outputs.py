"""
Task: gradio-html-watch-prop-observer
Repo: gradio-app/gradio @ f4c3a6dcb45218722d3150baef953c731d3eccf2

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: All tests are structural (regex/AST) because the Docker image has no
Node.js runtime — Svelte components cannot be compiled or executed.
"""

import ast
import re
from pathlib import Path

REPO = "/workspace/gradio"

INDEX = Path(f"{REPO}/js/html/Index.svelte")
SHARED = Path(f"{REPO}/js/html/shared/HTML.svelte")
PYHTML = Path(f"{REPO}/gradio/components/html.py")


def _strip_comments(text: str) -> str:
    """Remove JS/Svelte comments to prevent gaming via comment injection."""
    text = re.sub(r"//.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    return text


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_files_exist_and_python_parses():
    """All three modified files exist and html.py parses."""
    assert INDEX.exists(), f"{INDEX} not found"
    assert SHARED.exists(), f"{SHARED} not found"
    assert PYHTML.exists(), f"{PYHTML} not found"
    ast.parse(PYHTML.read_text())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_falsy_value_coalescing():
    """Value derivation uses ?? (nullish coalescing) not || which coerces 0 to empty."""
    content = _strip_comments(INDEX.read_text())

    # Bug pattern: gradio.props.value || "" treats 0 as falsy
    bug = re.search(r"(?:gradio\.props\.value|\.value)\s*\|\|\s*[\"']", content)
    assert bug is None, "Bug pattern (|| with string fallback) still present"

    # Must still derive value from gradio.props (not deleted entirely)
    assert "gradio.props.value" in content or "props.value" in content, \
        "Value derivation removed entirely"


# [pr_diff] fail_to_pass
def test_watch_function_defined():
    """A watch function is defined that stores callbacks (not an empty stub)."""
    index = _strip_comments(INDEX.read_text())
    shared = _strip_comments(SHARED.read_text())
    combined = index + "\n" + shared

    # Must define a watch/observe function with >= 2 params
    watch_func = re.search(
        r"(?:function\s+(?:watch|observe|onPropChange)\s*\([^)]*,[^)]*\)|"
        r"(?:watch|observe|onPropChange)\s*[:=]\s*(?:function\s*)?\([^)]*,[^)]*\)\s*(?:=>|:|\{))",
        combined,
    )
    assert watch_func, "No watch/observe function defined with >= 2 parameters"

    # Must store callbacks (push/set/add to collection — not an empty stub)
    has_storage = bool(re.search(
        r"(?:push|set|add)\s*\(.*(?:callback|cb|handler|fn|prop|entry)", combined, re.DOTALL
    ))
    has_collection = bool(re.search(
        r"(?:entries|watchers|observers|listeners|callbacks|_watchers|watch_entries)\s*[\[.\]]",
        combined,
    ))
    assert has_storage or has_collection, "Watch function has no callback storage (stub)"


# [pr_diff] fail_to_pass
def test_watch_exposed_in_js_on_load():
    """Watch function is passed into the js_on_load Function scope."""
    shared = _strip_comments(SHARED.read_text())

    # Pattern A: new Function(..., "watch", ...) AND func(..., watch...)
    has_func_param = bool(re.search(r"new\s+Function\s*\([^)]*[\"']watch[\"']", shared))
    has_func_call = bool(re.search(r"func\s*\([^)]*(?:watch|observe)", shared))

    # Pattern B: watch set on context/props/env object before func call
    has_context = bool(re.search(
        r"\w+\s*(?:\[.*(?:watch|observe).*\]|\.(?:watch|observe))\s*=",
        shared,
    ))

    assert (has_func_param and has_func_call) or has_context, \
        "Watch not integrated into js_on_load scope"


# [pr_diff] fail_to_pass
def test_prop_changes_fire_watchers():
    """Backend prop changes detect changed keys and invoke registered watch callbacks."""
    shared = _strip_comments(SHARED.read_text())
    index = _strip_comments(INDEX.read_text())
    combined = shared + "\n" + index

    # Must collect WHICH props changed (not in base code)
    has_changed_collection = bool(re.search(
        r"(?:changed|diff|modified|updated)\w*\s*(?:\.push|\.add|\[|\s*=\s*\[)", combined
    ))
    assert has_changed_collection, "No changed-key collection found"

    # Fire/notify function that iterates and calls callbacks
    fire_def = bool(re.search(
        r"(?:function\s+(?:fire_watchers|fire_observers|notify\w*|emit\w*|dispatch\w*)\s*\(|"
        r"(?:fire_watchers|fire_observers|notify\w*|emit\w*|dispatch\w*)\s*[:=]\s*(?:function|\())",
        combined,
    ))
    assert fire_def, "No fire/notify function defined"

    fire_loop = bool(re.search(
        r"(?:for\s*\(|forEach|\.map)\s*[^;]*(?:entr|watch|observ|listen|callback|subscri|handler)",
        combined,
    ))
    callback_call = bool(re.search(
        r"(?:callback|cb|handler|fn|entry\.callback|\.callback)\s*\(\s*\)", combined
    ))
    assert fire_loop and callback_call, "Fire/notify must iterate watchers and invoke callbacks"

    # Fire called after detecting changes (via queueMicrotask/setTimeout/tick or direct call)
    has_fire_call = bool(re.search(
        r"(?:fire_watchers|fire_observers|notify\w*|emit\w*|dispatch\w*)\s*\(\s*(?:changed|diff|modified|updated)",
        combined,
    ))
    has_inline = bool(re.search(
        r"(?:queueMicrotask|setTimeout|tick)\s*\([^)]*(?:fire|notify|emit|dispatch)",
        combined,
    ))
    assert has_fire_call or has_inline, "Fire/notify not called with changed keys"


# [pr_diff] fail_to_pass
def test_python_docstring_documents_watch():
    """html.py HTML class documents the watch function in js_on_load context."""
    source = PYHTML.read_text()
    tree = ast.parse(source)

    html_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "HTML":
            html_class = node
            break
    assert html_class, "HTML class not found"

    found = False
    # Check string constants > 50 chars that mention both watch and js_on_load
    for node in ast.walk(html_class):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            val = node.value.lower()
            if len(node.value) > 50 and "watch" in val and "js_on_load" in val:
                found = True
                break

    # Also check class and __init__ docstrings
    cls_doc = ast.get_docstring(html_class) or ""
    if "watch" in cls_doc.lower():
        found = True

    for item in html_class.body:
        if isinstance(item, ast.FunctionDef) and item.name == "__init__":
            doc = ast.get_docstring(item) or ""
            if "watch" in doc.lower() and "js_on_load" in doc.lower():
                found = True

    assert found, "No watch documentation in js_on_load context"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub / regression
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_existing_features_preserved():
    """Svelte files have real content with existing component features intact."""
    files_checks = [
        (INDEX, 40, ["Gradio", "upload", "props", "visible", "label"]),
        (SHARED, 80, ["Handlebars", "js_on_load", "trigger", "reactiveProps",
                       "createEventDispatcher"]),
    ]
    for path, min_lines, required in files_checks:
        content = _strip_comments(path.read_text())
        lines = len(content.strip().splitlines())
        assert lines >= min_lines, f"{path} has {lines} lines, expected >= {min_lines}"
        for req in required:
            assert req in content, f"{path} missing expected content '{req}'"

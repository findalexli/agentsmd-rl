"""
Task: gradio-html-watch-prop-observer
Repo: gradio-app/gradio @ f4c3a6dcb45218722d3150baef953c731d3eccf2

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/gradio"

INDEX = Path(f"{REPO}/js/html/Index.svelte")
SHARED = Path(f"{REPO}/js/html/shared/HTML.svelte")
PYHTML = Path(f"{REPO}/gradio/components/html.py")


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a Python script to a temp file and execute it in the repo dir."""
    script = Path(f"{REPO}/_eval_tmp.py")
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


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
    """All three modified files exist and html.py parses without errors."""
    assert INDEX.exists(), f"{INDEX} not found"
    assert SHARED.exists(), f"{SHARED} not found"
    assert PYHTML.exists(), f"{PYHTML} not found"
    r = _run_py("import ast; ast.parse(open('gradio/components/html.py').read()); print('PASS')")
    assert r.returncode == 0, f"html.py parse error: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_falsy_value_coalescing():
    """Value derivation uses ?? (nullish coalescing) not || which coerces 0 to empty."""
    r = _run_py(r"""
import re

content = open("js/html/Index.svelte").read()
# Strip comments to prevent gaming
content = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

# Bug pattern: gradio.props.value || "" treats 0 as falsy
bug = re.search(r"(?:gradio\.props\.value|\.value)\s*\|\|\s*[\"']", content)
assert bug is None, f"Bug pattern (|| with string fallback) still present: {bug.group()}"

# Fix: must use ?? operator
fix = re.search(r"gradio\.props\.value\s*\?\?\s*[\"']", content)
assert fix is not None, "Value derivation does not use ?? (nullish coalescing)"

# Value derivation must still reference gradio.props.value
assert "gradio.props.value" in content, "Value derivation removed entirely"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_watch_function_defined():
    """A watch function and fire_watchers function are defined in Index.svelte with proper structure."""
    r = _run_py(r"""
import re

content = open("js/html/Index.svelte").read()
content = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

# 1. watch_entries array must exist (stores registered watchers)
assert "watch_entries" in content, "No watch_entries array defined"

# 2. watch() function must be defined
watch_def = re.search(r"function\s+watch\s*\(", content)
assert watch_def, "No watch() function defined"

# 3. watch() must push entries to watch_entries (not a stub)
assert "watch_entries.push" in content, "watch() does not push to watch_entries (stub?)"

# 4. fire_watchers() function must be defined
fire_def = re.search(r"function\s+fire_watchers\s*\(", content)
assert fire_def, "No fire_watchers() function defined"

# 5. fire_watchers must iterate entries and invoke callbacks
has_iteration = bool(re.search(r"(?:for\s*\(|\.forEach|\.some)\s*.*entry", content, re.DOTALL))
assert has_iteration, "fire_watchers does not iterate over entries"

# 6. Callback must be invoked (entry.callback or similar)
assert "callback" in content, "No callback invocation found"

# 7. Error handling around callback execution
assert "try" in content or "catch" in content, "No error handling in watch callback execution"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_watch_exposed_in_js_on_load():
    """Watch function is passed into the js_on_load Function scope as 'watch' parameter."""
    r = _run_py(r"""
import re

content = open("js/html/shared/HTML.svelte").read()
content = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

# 1. "watch" must appear as a string literal in new Function parameter list
func_param = re.search("new\\s+Function\\s*\\([^)]*[\"']watch[\"']", content)
assert func_param, "'watch' not in new Function() parameter list"

# 2. watch_fn must be passed as argument when calling func()
func_call = re.search(r"func\s*\([^)]*watch_fn", content)
assert func_call, "watch_fn not passed to func() call"

# 3. watch_fn must be declared as a component prop
assert "watch_fn" in content, "watch_fn not declared as a prop in HTML.svelte"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_prop_changes_fire_watchers():
    """Backend prop changes detect changed keys and invoke fire_watchers via queueMicrotask."""
    r = _run_py(r"""
import re

content = open("js/html/shared/HTML.svelte").read()
content = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

# 1. Must collect changed keys
assert "changedKeys" in content or "changed_keys" in content, \
    "No changed-key collection found"

# 2. Must detect changes using JSON.stringify for deep comparison
assert "JSON.stringify" in content, \
    "No JSON.stringify comparison — shallow comparison misses nested changes"

# 3. fire_watchers must be called with the changed keys
fire_call = re.search(r"fire_watchers\s*\(", content)
assert fire_call, "fire_watchers() not called in prop update effect"

# 4. Must use deferred execution so callbacks see updated template
assert "queueMicrotask" in content, \
    "No queueMicrotask — callbacks may fire before template re-renders"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_python_docstring_documents_watch():
    """html.py HTML class js_on_load parameter docstring documents the watch function."""
    r = _run_py(r"""
import ast

source = open("gradio/components/html.py").read()
tree = ast.parse(source)

# Look for the js_on_load parameter docstring that mentions watch
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        val = node.value
        val_lower = val.lower()
        # The PR adds watch documentation to the js_on_load parameter description
        # This is a long string constant (>50 chars) mentioning both watch and js_on_load
        if len(val) > 50 and "watch" in val_lower and "js_on_load" in val_lower:
            # Verify it actually describes the watch function usage
            if "watch(" in val or "watch (" in val or "watch function" in val_lower:
                found = True
                break

assert found, "No watch function documentation found in js_on_load context in html.py"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


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


# ---------------------------------------------------------------------------
# Pass-to-pass (repo CI/CD) — ensure repo's own checks pass on base and after fix
# ---------------------------------------------------------------------------


# [repo_ci] pass_to_pass
def test_repo_python_syntax():
    """Repo's Python files have valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", "gradio/components/html.py"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax error in html.py: {r.stderr}"


# [repo_ci] pass_to_pass
def test_repo_ruff_check():
    """Repo's Python linting passes on html.py (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
            apt-get update -qq 2>/dev/null || true
            apt-get install -y -qq python3-pip 2>/dev/null || true
            pip3 install --break-system-packages ruff 2>/dev/null || pip3 install ruff 2>/dev/null || true
            ruff check gradio/components/html.py
        """],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_ci] pass_to_pass
def test_repo_ruff_format():
    """Repo's Python formatting passes on html.py (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
            apt-get update -qq 2>/dev/null || true
            apt-get install -y -qq python3-pip 2>/dev/null || true
            pip3 install --break-system-packages ruff 2>/dev/null || pip3 install ruff 2>/dev/null || true
            ruff format --check gradio/components/html.py
        """],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_ci] pass_to_pass
def test_repo_svelte_syntax():
    """Svelte files are valid JS/HTML syntax (pass_to_pass)."""
    # Check that Svelte files parse as valid HTML-like content
    for path in [INDEX, SHARED]:
        content = path.read_text()
        # Basic checks for valid Svelte component structure
        assert "<script" in content, f"{path} missing script tag"
        assert len(content) > 100, f"{path} seems too short ({len(content)} chars)"
        # Check for balanced basic brackets (rough check)
        open_tags = content.count("<")
        close_tags = content.count(">")
        assert open_tags > 0 and close_tags > 0, f"{path} missing HTML tags"
        assert content.count("{") >= content.count("}"), f"{path} may have unbalanced braces"


# [repo_ci] pass_to_pass
def test_repo_imports_parse():
    """Repo's Python imports parse correctly (pass_to_pass)."""
    # Check that imports in html.py are syntactically valid (AST parse only)
    # Don't actually import because gradio_client is not in the minimal environment
    r = _run_py("""
import ast
source = open('gradio/components/html.py').read()
tree = ast.parse(source)
imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
assert len(imports) > 0, "No imports found in html.py"
print('PASS')
""")
    assert r.returncode == 0, f"Import parse failed:\n{r.stderr}"
    assert "PASS" in r.stdout

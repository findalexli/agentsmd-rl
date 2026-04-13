"""
Task: gradio-add-server-functions-support-to
Repo: gradio-app/gradio @ 7c3fa2a6900cfa3c87cb61ffa9b34b75d1ae49ba
PR:   12929

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import ast
from pathlib import Path

REPO = "/workspace/gradio"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python files must parse without errors."""
    files = ["gradio/components/html.py"]
    for f in files:
        src = Path(f"{REPO}/{f}").read_text()
        ast.parse(src)


# [repo_tests] pass_to_pass
def test_repo_html_component_tests():
    """Repo's HTML component tests pass (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "pytest", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    subprocess.run(
        ["pip", "install", "-e", f"{REPO}/client/python", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["python", "-m", "pytest", f"{REPO}/test/components/test_html.py", "-v"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"HTML component tests failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_button_component_tests():
    """Repo's Button component tests pass (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "pytest", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    subprocess.run(
        ["pip", "install", "-e", f"{REPO}/client/python", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["python", "-m", "pytest", f"{REPO}/test/components/test_button.py", "-v"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Button component tests failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_component_props_tests():
    """Repo's component props tests pass (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "pytest", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    subprocess.run(
        ["pip", "install", "-e", f"{REPO}/client/python", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["python", "-m", "pytest", f"{REPO}/test/test_component_props.py", "-v"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Component props tests failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Ruff lint check on modified files passes (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["ruff", "check", f"{REPO}/gradio/components/html.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Ruff format check on modified files passes (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["ruff", "format", "--check", f"{REPO}/gradio/components/html.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_file_explorer_tests():
    """Repo's FileExplorer component tests pass (pass_to_pass) - tests server_fns functionality."""
    subprocess.run(
        ["pip", "install", "pytest", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    subprocess.run(
        ["pip", "install", "-e", f"{REPO}/client/python", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["python", "-m", "pytest", f"{REPO}/test/components/test_file_explorer.py", "-v"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"FileExplorer component tests failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_image_editor_tests():
    """Repo's ImageEditor component tests pass (pass_to_pass) - tests server_fns functionality."""
    subprocess.run(
        ["pip", "install", "pytest", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    subprocess.run(
        ["pip", "install", "-e", f"{REPO}/client/python", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["python", "-m", "pytest", f"{REPO}/test/components/test_image_editor.py", "-v"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"ImageEditor component tests failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_server_import_added():
    """The server decorator is imported from gradio.components.base."""
    src = Path(f"{REPO}/gradio/components/html.py").read_text()
    assert "from gradio.components.base import Component, server" in src, \
        "server not imported from gradio.components.base"


# [pr_diff] fail_to_pass
def test_server_functions_parameter_exists():
    """The HTML component accepts server_functions parameter."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
sys.path.insert(0, '/workspace/gradio')
from gradio.components.html import HTML
import inspect

sig = inspect.signature(HTML.__init__)
params = list(sig.parameters.keys())
assert 'server_functions' in params, f"server_functions not in params: {params}"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_server_functions_decorated_and_attached():
    """Functions in server_functions are decorated with @server and attached to instance."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
sys.path.insert(0, '/workspace/gradio')
import gradio as gr

def test_func(x):
    return f"Result: {x}"

try:
    html = gr.HTML(value="test", server_functions=[test_func])
    assert hasattr(html, 'test_func'), "test_func not attached"
    assert hasattr(html, 'server_fns'), "server_fns missing"
    assert len(html.server_fns) > 0, "server_fns empty"
    print("PASS")
except Exception as e:
    print(f"FAIL: {e}")
    sys.exit(1)
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_js_on_load_docstring_updated():
    """The js_on_load docstring documents the server object availability."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
sys.path.insert(0, '/workspace/gradio')
from gradio.components.html import HTML

doc = HTML.__init__.__doc__
assert "server" in doc.lower(), "js_on_load docstring missing 'server'"
assert "server_functions" in doc, "docstring missing 'server_functions'"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_server_functions_docstring_exists():
    """The server_functions parameter is documented in the docstring."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
sys.path.insert(0, '/workspace/gradio')
from gradio.components.html import HTML

doc = HTML.__init__.__doc__
assert "server_functions:" in doc, "server_functions not documented"
assert "async method" in doc or "backend" in doc.lower(), "docs don't explain backend"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_html_component_still_works():
    """HTML component without server_functions still works (regression test)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
sys.path.insert(0, '/workspace/gradio')
import gradio as gr

html = gr.HTML(value="<h1>Hello</h1>")
assert html.value == "<h1>Hello</h1>", "Basic HTML broken"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [static] pass_to_pass
def test_not_stub():
    """server_functions logic is not a stub."""
    src = Path(f"{REPO}/gradio/components/html.py").read_text()
    assert "if server_functions:" in src, "server_functions handling missing"
    assert "for fn in server_functions:" in src, "server_functions loop missing"
    assert "decorated = server(fn)" in src or "server(fn)" in src, \
        "server decorator usage missing"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass
def test_skill_md_html_signature_updated():
    """SKILL.md HTML signature includes server_functions parameter."""
    skill_path = Path(f"{REPO}/.agents/skills/gradio/SKILL.md")
    if not skill_path.exists():
        return
    src = skill_path.read_text()
    assert "server_functions" in src, "server_functions not in SKILL.md"


# [agent_config] fail_to_pass
def test_skill_md_server_functions_section():
    """SKILL.md has a Server Functions section with example code."""
    skill_path = Path(f"{REPO}/.agents/skills/gradio/SKILL.md")
    if not skill_path.exists():
        return
    src = skill_path.read_text()
    assert "## Server Functions" in src or "Server Functions" in src, \
        "Server Functions section missing"
    assert "server_functions=[" in src, "Example usage missing"
    assert "server." in src and "await" in src, "server object explanation missing"


# [agent_config] fail_to_pass
def test_code_style_consistency():
    """Code changes are consistent with surrounding style."""
    src = Path(f"{REPO}/gradio/components/html.py").read_text()
    lines = src.split('\n')
    import_line = None
    for line in lines:
        if 'from gradio.components.base import' in line:
            import_line = line
            break
    assert import_line is not None, "Import line not found"
    assert 'Component, server' in import_line or 'Component,server' in import_line, \
        "Import style inconsistent"

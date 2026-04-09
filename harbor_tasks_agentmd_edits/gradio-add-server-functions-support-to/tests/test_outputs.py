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


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_server_import_added():
    """The server decorator is imported from gradio.components.base."""
    src = Path(f"{REPO}/gradio/components/html.py").read_text()
    # Check for: from gradio.components.base import Component, server
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

# Define a simple test function
def test_func(x):
    return f"Result: {x}"

# Create HTML with server_functions
try:
    html = gr.HTML(
        value="test",
        server_functions=[test_func],
    )
    # Check that the function was decorated and attached
    assert hasattr(html, 'test_func'), "test_func not attached to HTML instance"
    # Check that the function was added to server_fns list
    assert hasattr(html, 'server_fns'), "server_fns attribute missing"
    assert len(html.server_fns) > 0, "server_fns list is empty"
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

# Get the docstring from the __init__ method
doc = HTML.__init__.__doc__

# Check that js_on_load documentation mentions server
assert "server" in doc.lower(), f"js_on_load docstring does not mention 'server'"
assert "server_functions" in doc, f"docstring does not mention 'server_functions'"
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

# Check for server_functions parameter documentation
assert "server_functions:" in doc, "server_functions parameter not documented"
assert "async method" in doc or "backend" in doc.lower(), \
    "server_functions documentation does not explain how it works"
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

# Test basic HTML still works
html = gr.HTML(value="<h1>Hello</h1>")
assert html.value == "<h1>Hello</h1>", "Basic HTML value not set correctly"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [static] pass_to_pass
def test_not_stub():
    """server_functions logic is not a stub (has real implementation)."""
    src = Path(f"{REPO}/gradio/components/html.py").read_text()
    # Check that there's actual implementation, not just pass or ellipsis
    # Look for the specific server_functions handling code
    assert "if server_functions:" in src, "server_functions handling missing"
    assert "for fn in server_functions:" in src, "server_functions loop missing"
    assert "decorated = server(fn)" in src or "server(fn)" in src, \
        "server decorator usage missing"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / AGENTS.md / SKILL.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .agents/skills/gradio/SKILL.md:103 @ 7c3fa2a6900cfa3c87cb61ffa9b34b75d1ae49ba
def test_skill_md_html_signature_updated():
    """SKILL.md HTML signature includes server_functions parameter."""
    skill_path = Path(f"{REPO}/.agents/skills/gradio/SKILL.md")
    if not skill_path.exists():
        # If SKILL.md doesn't exist at this path, check if it exists elsewhere
        return  # Skip if file doesn't exist at expected location

    src = skill_path.read_text()

    # Check that the HTML signature includes server_functions
    # The signature should have: server_functions: list[Callable] | None = None
    assert "server_functions" in src, \
        "server_functions not documented in SKILL.md HTML signature"


# [agent_config] fail_to_pass — .agents/skills/gradio/SKILL.md:476-532 @ 7c3fa2a6900cfa3c87cb61ffa9b34b75d1ae49ba
def test_skill_md_server_functions_section():
    """SKILL.md has a Server Functions section with example code."""
    skill_path = Path(f"{REPO}/.agents/skills/gradio/SKILL.md")
    if not skill_path.exists():
        return  # Skip if file doesn't exist at expected location

    src = skill_path.read_text()

    # Check for Server Functions section
    assert "## Server Functions" in src or "Server Functions" in src, \
        "Server Functions section missing from SKILL.md"

    # Check for example code showing usage
    assert "server_functions=[" in src, \
        "Example server_functions usage missing from SKILL.md"

    # Check that it explains the server object usage
    assert "server." in src and "await" in src, \
        "Explanation of server object async methods missing"


# [agent_config] fail_to_pass — AGENTS.md:44 @ 7c3fa2a6900cfa3c87cb61ffa9b34b75d1ae49ba
def test_code_style_consistency():
    """Code changes are consistent with surrounding style (from AGENTS.md)."""
    src = Path(f"{REPO}/gradio/components/html.py").read_text()

    # Check that the server_functions code follows the same style as other parameters
    # The import should match the style: from X import A, B
    lines = src.split('\n')

    # Find the import line
    import_line = None
    for line in lines:
        if 'from gradio.components.base import' in line:
            import_line = line
            break

    assert import_line is not None, "Import line not found"
    # The style should be consistent - importing multiple items on one line
    assert 'Component, server' in import_line or 'Component,server' in import_line, \
        "Import style inconsistent"

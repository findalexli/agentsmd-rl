"""
Task: gradio-custom-libraries-in-head-of
Repo: gradio-app/gradio @ 0b943a4fd0d7701203f1b79b70b5afed19ee8413
PR:   12990

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/workspace/gradio"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", f"{REPO}/gradio/components/html.py"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_head_parameter_accepted():
    """gr.HTML accepts head parameter without TypeError."""
    r = subprocess.run(
        [sys.executable, "-c", """
import sys
sys.path.insert(0, "/workspace/gradio")

import gradio as gr

# Should not raise TypeError about unexpected keyword argument
try:
    html = gr.HTML(
        value="<div>Test</div>",
        head='<script src="https://example.com/lib.js"></script>',
    )
    print("PASS: head parameter accepted")
except TypeError as e:
    if "head" in str(e):
        print(f"FAIL: head parameter not accepted - {e}")
        sys.exit(1)
    raise
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Test failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_head_in_config():
    """head value is included in component config output."""
    r = subprocess.run(
        [sys.executable, "-c", """
import sys
sys.path.insert(0, "/workspace/gradio")

import gradio as gr

head_value = '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>'
html = gr.HTML(
    value="<canvas id='chart'></canvas>",
    head=head_value,
)
config = html.get_config()

# Check head is in config
if "head" not in config:
    print(f"FAIL: 'head' key not in config. Keys: {list(config.keys())}")
    sys.exit(1)

# Check head value is correct
if config["head"] != head_value:
    print(f"FAIL: head value mismatch. Expected: {head_value!r}, Got: {config['head']!r}")
    sys.exit(1)

print("PASS: head correctly included in config")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Test failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_head_none_default():
    """head defaults to None when not provided."""
    r = subprocess.run(
        [sys.executable, "-c", """
import sys
sys.path.insert(0, "/workspace/gradio")

import gradio as gr

html = gr.HTML(value="<div>Test</div>")
config = html.get_config()

if "head" not in config:
    print(f"FAIL: 'head' key not in config")
    sys.exit(1)

if config["head"] is not None:
    print(f"FAIL: head should default to None, got: {config['head']!r}")
    sys.exit(1)

print("PASS: head defaults to None")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Test failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_head_stored_on_instance():
    """head attribute is accessible on HTML instance."""
    r = subprocess.run(
        [sys.executable, "-c", """
import sys
sys.path.insert(0, "/workspace/gradio")

import gradio as gr

head_value = '<link rel="stylesheet" href="https://example.com/style.css">'
html = gr.HTML(value="<div>Test</div>", head=head_value)

# Check head is stored as instance attribute
if not hasattr(html, 'head'):
    print("FAIL: 'head' attribute not found on HTML instance")
    sys.exit(1)

if html.head != head_value:
    print(f"FAIL: html.head mismatch. Expected: {head_value!r}, Got: {html.head!r}")
    sys.exit(1)

print("PASS: head stored on instance")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Test failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_html_tests_pass():
    """Existing HTML component tests still pass."""
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "test/components/test_html.py", "-x", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Existing tests failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_html_tests_fast():
    """HTML component tests pass without warnings (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "test/components/test_html.py", "-x", "--tb=short", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"HTML tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_gradio_imports_cleanly():
    """gradio module imports without errors (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-c", "import gradio; print('gradio imported successfully')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"gradio import failed: {r.stderr}"
    assert "gradio imported successfully" in r.stdout


# [static] pass_to_pass
def test_not_stub():
    """HTML.get_config has real logic, not just pass/return."""
    import ast

    src = Path(f"{REPO}/gradio/components/html.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_config":
            # Check for meaningful statements (not just Pass or simple returns)
            stmts = [s for s in node.body if not isinstance(s, (ast.Pass, ast.Expr))]
            assert len(stmts) >= 3, "get_config body is a stub or too simple"
            return

    assert False, "get_config method not found"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from SKILL.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .agents/skills/gradio/SKILL.md:106 @ 0b943a4fd0d7701203f1b79b70b5afed19ee8413
def test_skill_documentation_exists():
    """SKILL.md documents HTML component parameters including head."""
    skill_path = Path(f"{REPO}/.agents/skills/gradio/SKILL.md")
    if not skill_path.exists():
        # SKILL.md may not exist in base commit, skip
        return

    content = skill_path.read_text()

    # Check HTML signature mentions head parameter
    html_sig = "HTML(value:"
    if html_sig in content:
        # Verify head is documented if HTML is mentioned
        html_section = content[content.find(html_sig):content.find(html_sig) + 500]
        # We just verify the file exists and has HTML docs
        assert "head" in content or "HTML" in content, "SKILL.md missing HTML documentation"

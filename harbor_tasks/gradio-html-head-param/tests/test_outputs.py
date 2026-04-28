"""
Task: gradio-html-head-param
Repo: gradio-app/gradio @ 0b943a4fd0d7701203f1b79b70b5afed19ee8413
PR:   12990

Adds a `head` parameter to gr.HTML for injecting third-party scripts/CSS
into the document head. The SKILL.md and custom HTML guide must be updated
to document this new feature.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/gradio"


def _file_content(path: str) -> str:
    """Read a file from the repo."""
    return (Path(REPO) / path).read_text()


def _run_py(code: str) -> subprocess.CompletedProcess:
    """Execute Python code in the repo directory via subprocess."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


def test_syntax_check():
    """Modified gradio/components/html.py parses without syntax errors."""
    r = _run_py("""
import ast
from pathlib import Path
tree = ast.parse(Path("gradio/components/html.py").read_text())
assert tree is not None
print("PASS")
""")
    assert r.returncode == 0, f"Syntax error in html.py: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass gates (repo CI/CD tests)
# ---------------------------------------------------------------------------


def test_repo_ruff_check():
    """Repo's ruff lint passes on html.py (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "ruff", "check", "gradio/components/html.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:]}"


def test_repo_ruff_format():
    """Repo's ruff format check passes on html.py (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "ruff", "format", "--check", "gradio/components/html.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr[-500:]}"


def test_repo_html_tests():
    """HTML component tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "test/components/test_html.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"HTML component tests failed:\n{r.stderr[-500:]}"


def test_repo_html_syntax():
    """Repo's html.py parses without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c", "import ast; ast.parse(open('gradio/components/html.py').read()); print('OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr[-500:]}"
    assert "OK" in r.stdout


def test_repo_ruff_check_on_test_files():
    """Repo's ruff lint passes on HTML test file (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "ruff", "check", "test/components/test_html.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check on test file failed:\n{r.stderr[-500:]}"


def test_repo_ruff_format_on_test_files():
    """Repo's ruff format check passes on HTML test file (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "ruff", "format", "--check", "test/components/test_html.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check on test file failed:\n{r.stderr[-500:]}"


def test_repo_components_syntax():
    """All components parse without syntax errors (pass_to_pass)."""
    code = """
import ast
import sys
from pathlib import Path

components_dir = Path('gradio/components')
errors = []
for py_file in components_dir.glob('*.py'):
    try:
        ast.parse(py_file.read_text())
    except SyntaxError as e:
        errors.append(f'{py_file}: {e}')

if errors:
    print('Syntax errors found:')
    for err in errors:
        print(err)
    sys.exit(1)
else:
    print('OK')
"""
    r = subprocess.run(
        ["python", "-c", code],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Components syntax check failed:\n{r.stderr[-500:]}"
    assert "OK" in r.stdout





def test_repo_ruff_format_components_dir():
    """Ruff format check passes on entire components directory (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "ruff", "format", "--check", "gradio/components/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check on components dir failed:\n{r.stderr[-500:]}"


def test_repo_gradio_import():
    """Gradio package imports successfully (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c", "import gradio; print(gradio.__version__); print('OK')"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Gradio import failed:\n{r.stderr[-500:]}"
    assert "OK" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - code behavior
# ---------------------------------------------------------------------------


def test_head_param_in_init():
    """HTML.__init__ must accept a head parameter before server_functions."""
    r = _run_py("""
import inspect
from gradio.components.html import HTML

sig = inspect.signature(HTML.__init__)
params = list(sig.parameters.keys())

# head must be an explicit named parameter (not just **kwargs)
assert 'head' in params, f"head not in __init__ signature: {params}"

# head must appear before server_functions
head_idx = params.index('head')
sf_idx = params.index('server_functions')
assert head_idx < sf_idx, (
    f"head at position {head_idx}, server_functions at {sf_idx}"
)
print("PASS: head parameter in correct position")
""")
    assert r.returncode == 0, f"head param not in signature: {r.stderr}"
    assert "PASS" in r.stdout


def test_head_stored_as_attribute():
    """HTML instance must store head value and return it via attribute access."""
    r = _run_py("""
from gradio.components.html import HTML

test_head = "<script src='test.js'></script>"
html = HTML(value="<div>test</div>", head=test_head)

# Verify self.head attribute returns the value
actual = html.head
assert actual == test_head, f"Expected {test_head!r}, got {actual!r}"
print("PASS: head attribute stored correctly")
""")
    assert r.returncode == 0, f"self.head not accessible: {r.stderr}"
    assert "PASS" in r.stdout


def test_publish_format_uses_self_head():
    """_to_publish_format must use self.head as fallback when head arg not provided."""
    r = _run_py("""
from gradio.components.html import HTML

test_head = "<script src='https://example.com/lib.js'></script>"
html = HTML(value="<div>test</div>", head=test_head)

# Call _to_publish_format WITHOUT passing head argument
result = html._to_publish_format(name="test")

# Verify the result contains self.head as the fallback
actual_head = result.get("head")
assert actual_head == test_head, f"Expected head={test_head!r}, got {actual_head!r}"
print("PASS: _to_publish_format falls back to self.head")
""")
    assert r.returncode == 0, f"_to_publish_format doesn't use self.head: {r.stderr}"
    assert "PASS" in r.stdout


def test_publish_format_head_arg_takes_precedence():
    """_to_publish_format must use head arg when provided, overriding self.head."""
    r = _run_py("""
from gradio.components.html import HTML

instance_head = "<script src='instance.js'></script>"
arg_head = "<script src='arg.js'></script>"
html = HTML(value="<div>test</div>", head=instance_head)

# Call _to_publish_format WITH head argument
result = html._to_publish_format(name="test", head=arg_head)

# Verify the head argument takes precedence
actual_head = result.get("head")
assert actual_head == arg_head, f"Expected head={arg_head!r}, got {actual_head!r}"
print("PASS: head argument takes precedence over self.head")
""")
    assert r.returncode == 0, f"head arg doesn't take precedence: {r.stderr}"
    assert "PASS" in r.stdout


def test_push_to_hub_uses_self_head():
    """push_to_hub must pass self.head as fallback to _to_publish_format."""
    r = _run_py("""
from gradio.components.html import HTML
from unittest.mock import patch, MagicMock

test_head = "<script src='https://example.com/lib.js'></script>"
html = HTML(value="<div>test</div>", head=test_head)

# Track what _to_publish_format is called with
captured_args = {}
original_to_publish_format = html._to_publish_format

def tracking_to_publish_format(*args, **kwargs):
    captured_args['args'] = args
    captured_args['kwargs'] = kwargs
    # Return minimal required data
    return {
        "id": "test-id",
        "name": "test",
        "head": kwargs.get('head', 'NOT_PASSED'),
        "description": "",
        "author": "",
    }

# Patch the method on the instance
html._to_publish_format = tracking_to_publish_format

# Mock huggingface_hub imports that are imported inside push_to_hub
with patch.dict('sys.modules', {'huggingface_hub': MagicMock()}):
    import sys
    mock_hf = sys.modules['huggingface_hub']
    mock_hf.CommitOperationAdd = MagicMock
    mock_hf.HfApi = MagicMock
    mock_hf.hf_hub_download = MagicMock(return_value=None)
    
    # Mock HfApi instance methods
    mock_api = MagicMock()
    mock_commit = MagicMock()
    mock_commit.pr_url = "https://example.com/pr"
    mock_api.create_commit.return_value = mock_commit
    mock_hf.HfApi.return_value = mock_api
    
    # Also need to mock the open() call for reading manifest
    from unittest.mock import mock_open
    with patch('builtins.open', mock_open(read_data='[]')):
        try:
            html.push_to_hub(name="test")
        except Exception as e:
            # Some errors are expected with mocking, but we captured the call
            pass

# Verify _to_publish_format was called with head=self.head
actual_head = captured_args.get('kwargs', {}).get('head')
assert actual_head == test_head, f"Expected head={test_head!r}, got {actual_head!r}"
print("PASS: push_to_hub passes self.head to _to_publish_format")
""")
    assert r.returncode == 0, f"push_to_hub doesn't use self.head: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - config/documentation updates
# ---------------------------------------------------------------------------


def test_skill_md_html_signature_has_head():
    """SKILL.md HTML component signature must include head parameter."""
    content = _file_content(".agents/skills/gradio/SKILL.md")
    # Find the HTML signature section
    html_marker = "### `HTML("
    assert html_marker in content, "HTML component signature not found in SKILL.md"

    html_start = content.find(html_marker)
    # The signature is on one line ending with `)`
    sig_end = content.find(")`", html_start) + 1
    sig_line = content[html_start:sig_end + 1]

    assert "head" in sig_line, "head parameter not in HTML signature in SKILL.md"
    # Check that head appears with reasonable type annotation
    assert "head:" in sig_line, "head must have type annotation in SKILL.md signature"
    # head must appear before server_functions in the signature
    head_pos = sig_line.find("head:")
    sf_pos = sig_line.find("server_functions")
    assert head_pos < sf_pos, (
        "head parameter must come before server_functions in SKILL.md signature"
    )


def test_guide_documents_head_parameter():
    """Custom HTML guide must document the head parameter with examples."""
    content = _file_content(
        "guides/03_building-with-blocks/06_custom-HTML-components.md"
    )
    lower = content.lower()
    # Must have a section about head
    assert "## loading third-party scripts" in lower or "## loading third-party scripts with head" in lower, (
        "Guide must have a section about the head parameter titled 'Loading Third-Party Scripts'"
    )
    # Must mention third-party libraries
    assert "third-party" in lower or "third party" in lower, (
        "Guide should mention third-party library loading"
    )
    # Must include a code example using head parameter
    assert "head=" in content or "head =" in content, (
        "Guide must include a code example with head parameter"
    )
    # Must show script tag usage
    assert "<script" in content.lower(), (
        "Guide should show script tag loading example"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
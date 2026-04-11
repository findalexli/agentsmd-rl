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


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - code behavior
# ---------------------------------------------------------------------------


def test_head_param_in_init():
    """HTML.__init__ must accept a head parameter before server_functions."""
    r = _run_py(r"""
import ast
from pathlib import Path

tree = ast.parse(Path("gradio/components/html.py").read_text())
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                param_names = [arg.arg for arg in item.args.args]
                assert "head" in param_names, (
                    f"head not found in __init__ params: {param_names}"
                )
                # head must come before server_functions
                if "server_functions" in param_names:
                    head_idx = param_names.index("head")
                    sf_idx = param_names.index("server_functions")
                    assert head_idx < sf_idx, (
                        "head param must come before server_functions"
                    )
                # head must have a default of None
                defaults = item.args.defaults
                kw_defaults = item.args.kw_defaults  # for keyword-only args
                found = True
                print("PASS")
                break
        if found:
            break
if not found:
    raise AssertionError("Could not find HTML.__init__ with head param")
""")
    assert r.returncode == 0, f"head param check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_head_stored_as_attribute():
    """HTML.__init__ must store head as self.head."""
    r = _run_py(r"""
import ast
from pathlib import Path

source = Path("gradio/components/html.py").read_text()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                # Check for self.head = head assignment
                has_attr = False
                for stmt in ast.walk(item):
                    if (isinstance(stmt, ast.Assign)
                        and len(stmt.targets) == 1
                        and isinstance(stmt.targets[0], ast.Attribute)
                        and stmt.targets[0].attr == "head"
                        and isinstance(stmt.targets[0].value, ast.Name)
                        and stmt.targets[0].value.id == "self"):
                        has_attr = True
                        break
                assert has_attr, "self.head = head not found in __init__"
                print("PASS")
                break
        else:
            continue
        break
""")
    assert r.returncode == 0, f"self.head check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_publish_format_uses_self_head():
    """_to_publish_format must use self.head as fallback for the head key."""
    r = _run_py(r"""
from pathlib import Path

source = Path("gradio/components/html.py").read_text()

# Find _to_publish_format method
idx = source.find("def _to_publish_format(")
assert idx != -1, "_to_publish_format method not found"

# Get the method body (up to next def at same indent)
method_start = idx
after = source[idx:]
end_idx = after.find("\ndef push_to_hub(")
if end_idx == -1:
    end_idx = len(after)
method_source = after[:end_idx]

# Must reference self.head (not just head parameter)
assert "self.head" in method_source, (
    "_to_publish_format must use self.head as fallback"
)
# The key pattern: "head": head or self.head or ""
assert 'head or self.head' in method_source, (
    '_to_publish_format must have "head or self.head" pattern'
)
print("PASS")
""")
    assert r.returncode == 0, f"_to_publish_format check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_push_to_hub_uses_self_head():
    """push_to_hub must pass self.head as fallback when head is not provided."""
    r = _run_py(r"""
from pathlib import Path

source = Path("gradio/components/html.py").read_text()

idx = source.find("def push_to_hub(")
assert idx != -1, "push_to_hub method not found"

# Get method body
after = source[idx:]
method_source = after[:after.find("\n\ndef ", 1) if "\n\ndef " in after else len(after)]

assert "self.head" in method_source, (
    "push_to_hub must reference self.head"
)
assert "head or self.head" in method_source or "head=head or self.head" in method_source, (
    "push_to_hub must use self.head as fallback for head parameter"
)
print("PASS")
""")
    assert r.returncode == 0, f"push_to_hub check failed: {r.stderr}"
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
    assert "head: str | None = None" in sig_line, (
        "head must have type str | None = None in SKILL.md signature"
    )
    # head must appear before server_functions in the signature
    head_pos = sig_line.find("head: str | None = None")
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
    assert "## loading third-party scripts" in lower or "head" in lower, (
        "Guide must have a section about the head parameter"
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

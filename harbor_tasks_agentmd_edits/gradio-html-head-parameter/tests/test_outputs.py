"""
Task: gradio-html-head-parameter
Repo: gradio-app/gradio @ 0b943a4fd0d7701203f1b79b70b5afed19ee8413
PR:   12990

Test that gr.HTML component supports the head= parameter for injecting
custom scripts/styles in the HTML <head>, and that SKILL.md is updated
to document this new parameter.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/gradio"


def _parse_file(filepath: str) -> ast.AST:
    """Parse a Python file and return its AST."""
    content = Path(filepath).read_text()
    return ast.parse(content)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

def test_syntax_check_python():
    """Python source files must parse without errors."""
    files = [
        f"{REPO}/gradio/components/html.py",
    ]
    for f in files:
        _parse_file(f)  # Will raise SyntaxError if invalid


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_html_accepts_head_parameter():
    """gr.HTML component __init__ accepts head= parameter."""
    tree = _parse_file(f"{REPO}/gradio/components/html.py")

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "__init__":
            # Find head parameter in the function signature
            args = node.args
            arg_names = [a.arg for a in args.args] + [a.arg for a in args.kwonlyargs]
            assert "head" in arg_names, (
                f"head parameter not found in HTML.__init__ signature. Got: {arg_names}"
            )
            return
    raise AssertionError("HTML.__init__ not found in html.py")


def test_head_stored_as_instance_attribute():
    """head parameter is stored as self.head instance attribute."""
    content = Path(f"{REPO}/gradio/components/html.py").read_text()

    # The PR adds self.head = head in __init__
    assert "self.head = head" in content, (
        "head parameter not stored as instance attribute. Expected 'self.head = head' in __init__."
    )


def test_head_in_api_info():
    """head attribute is returned in api_info() serialization."""
    content = Path(f"{REPO}/gradio/components/html.py").read_text()

    # The PR adds head to the returned api_info dict
    # Check for pattern like 'return {"head": self.head, ...}' or similar
    has_head_in_api = (
        '"head": self.head' in content or
        "'head': self.head" in content
    )
    assert has_head_in_api, (
        "head not included in api_info() return value. Expected head to be returned from api_info()"
    )


def test_skill_md_documents_head_param():
    """SKILL.md HTML signature includes head parameter documentation."""
    skill_path = Path(f"{REPO}/.agents/skills/gradio/SKILL.md")

    # File may not exist if agent doesn't update it
    if not skill_path.exists():
        raise AssertionError("SKILL.md does not exist - agent must update this file")

    content = skill_path.read_text()

    # Find the HTML component signature section
    assert "HTML(" in content, "SKILL.md does not contain HTML component documentation"

    # Check that head parameter is documented in the HTML signature
    assert "head:" in content or "head=" in content, (
        "SKILL.md HTML signature does not include head parameter. "
        "The signature should document head: str | None = None"
    )


def test_skill_md_signature_updated():
    """SKILL.md HTML component signature matches the updated Python signature."""
    skill_path = Path(f"{REPO}/.agents/skills/gradio/SKILL.md")

    if not skill_path.exists():
        raise AssertionError("SKILL.md does not exist - agent must update this file")

    content = skill_path.read_text()

    # Extract HTML signature line - look for the markdown header pattern
    lines = content.split("\n")
    html_sig = None

    for line in lines:
        if line.startswith("### `HTML("):
            html_sig = line
            break

    assert html_sig is not None, "Could not find HTML signature in SKILL.md"

    # Verify signature contains head parameter
    assert "head:" in html_sig or "head=" in html_sig, (
        f"SKILL.md HTML signature does not include head parameter. Got: {html_sig[:200]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — verify head works correctly when provided
# ---------------------------------------------------------------------------

def test_head_parameter_functional():
    """HTML component can be instantiated with head parameter."""
    # This is a behavioral test that exercises the full feature
    result = subprocess.run(
        [
            "python3", "-c",
            """
import gradio as gr

# Test 1: Create HTML with head parameter
html_comp = gr.HTML(
    value="<div>Test</div>",
    head='<script src="https://example.com/lib.js"></script>'
)

# Verify the head is stored
assert hasattr(html_comp, 'head'), "HTML component missing head attribute"
assert html_comp.head == '<script src="https://example.com/lib.js"></script>', \
    f"head not stored correctly: {html_comp.head}"

# Verify head appears in api_info
api_info = html_comp.api_info()
assert 'head' in api_info, "head not in api_info"
assert api_info['head'] == '<script src="https://example.com/lib.js"></script>', \
    f"head in api_info incorrect: {api_info.get('head')}"

print("All head parameter tests passed!")
"""
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Functional test failed: {result.stderr}\n{result.stdout}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — verify repo CI tests pass on base commit
# ---------------------------------------------------------------------------

def test_repo_imports_gradio():
    """Repo's gradio package imports without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "import gradio; print(gradio.__version__)"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"gradio import failed:\n{r.stderr}"


def test_repo_html_component_tests():
    """Repo's HTML component unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "test/components/test_html.py", "-v"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"HTML component tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"

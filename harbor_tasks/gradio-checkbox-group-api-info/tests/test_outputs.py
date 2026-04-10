"""
Task: gradio-checkbox-group-api-info
Repo: gradio-app/gradio @ ebbd24231dbc006c21fbbf1df00918be16883b86
PR:   12887

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/gradio"
TARGET = f"{REPO}/gradio/components/custom_html_components/colored_checkbox_group.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_repo_imports():
    """Repo main gradio package imports successfully (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "import gradio; print('gradio imported')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"gradio import failed:\n{r.stderr}"


# [static] pass_to_pass
def test_repo_component_imports():
    """ColoredCheckboxGroup component imports successfully (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "from gradio.components.custom_html_components.colored_checkbox_group import ColoredCheckboxGroup; "
         "print('ColoredCheckboxGroup imported')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"ColoredCheckboxGroup import failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_checkbox_group_tests():
    """Repo's checkbox group component tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "pytest", "test/components/test_checkbox_group.py", "-v", "--tb=short", "-x"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Checkbox group tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without errors."""
    r = subprocess.run(
        ["python3", "-c", f"import py_compile; py_compile.compile('{TARGET}', doraise=True)"],
        capture_output=True, timeout=15,
    )
    assert r.returncode == 0, f"Syntax error:\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass
def test_module_compilation():
    """Modified file can be imported as a Python module (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "from gradio.components.custom_html_components import colored_checkbox_group; "
         "print('Module imported successfully')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Module import failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_gr_checkbox_group_functionality():
    """Repo's core CheckboxGroup component functionality works (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import gradio as gr; "
         "cb = gr.CheckboxGroup(['a', 'b', 'c']); "
         "result = cb.preprocess(['a', 'c']); "
         "assert result == ['a', 'c'], f'preprocess failed: {result}'; "
         "print('CheckboxGroup functionality OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"CheckboxGroup functionality failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_custom_html_components_import():
    """Custom HTML components package imports successfully (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "from gradio.components import custom_html_components; "
         "print('Custom HTML components package imported')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Custom HTML components import failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_api_info_returns_correct_enum():
    """api_info() must not raise AttributeError and must return correct enum for given choices."""
    import sys
    sys.path.insert(0, REPO)
    from gradio.components.custom_html_components.colored_checkbox_group import ColoredCheckboxGroup

    component = ColoredCheckboxGroup(
        choices=["red", "green", "blue"],
        colors=["#FF0000", "#00FF00", "#0000FF"],
        label="Test",
    )
    result = component.api_info()
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    assert result["items"]["enum"] == ["red", "green", "blue"], (
        f"enum mismatch: {result['items']['enum']}"
    )


# [pr_diff] fail_to_pass
def test_api_info_dynamic_choices():
    """api_info() enum reflects the actual choices passed at init, preventing hardcoding."""
    import sys
    sys.path.insert(0, REPO)
    from gradio.components.custom_html_components.colored_checkbox_group import ColoredCheckboxGroup

    # Four-element list
    choices4 = ["option_x", "option_y", "option_z", "option_w"]
    comp4 = ColoredCheckboxGroup(
        choices=choices4, colors=["#111", "#222", "#333", "#444"], label="Four"
    )
    assert comp4.api_info()["items"]["enum"] == choices4

    # Single element
    comp1 = ColoredCheckboxGroup(choices=["only_one"], colors=["#FFF"], label="Single")
    assert comp1.api_info()["items"]["enum"] == ["only_one"]

    # Empty choices
    comp0 = ColoredCheckboxGroup(choices=[], colors=[], label="Empty")
    assert comp0.api_info()["items"]["enum"] == []


# [pr_diff] fail_to_pass
def test_api_info_schema_structure():
    """api_info() returns the expected API schema with correct title, type, and items shape."""
    import sys
    sys.path.insert(0, REPO)
    from gradio.components.custom_html_components.colored_checkbox_group import ColoredCheckboxGroup

    component = ColoredCheckboxGroup(
        choices=["a", "b"], colors=["#FF0000", "#00FF00"], label="Schema"
    )
    result = component.api_info()

    assert result["title"] == "Checkbox Group", f"title: {result.get('title')}"
    assert result["type"] == "array", f"type: {result.get('type')}"
    assert result["items"]["type"] == "string", f"items.type: {result['items'].get('type')}"
    assert "enum" in result["items"], "items missing 'enum' key"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) - regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_class_interface_intact():
    """ColoredCheckboxGroup can be instantiated and stores choices in props."""
    import sys
    sys.path.insert(0, REPO)
    from gradio.components.custom_html_components.colored_checkbox_group import ColoredCheckboxGroup

    component = ColoredCheckboxGroup(
        choices=["a", "b", "c"],
        colors=["#F00", "#0F0", "#00F"],
        label="Regression",
    )
    assert hasattr(component, "props"), "component missing props attribute"
    assert component.props["choices"] == ["a", "b", "c"], (
        f"props choices mismatch: {component.props.get('choices')}"
    )


# [static] pass_to_pass
def test_not_stub():
    """api_info method has real implementation (return statement, not just pass)."""
    # AST-only because: behavioral tests cover correctness; this guards against degenerate stubs
    import ast

    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ColoredCheckboxGroup":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "api_info":
                    has_return = any(isinstance(n, ast.Return) for n in ast.walk(item))
                    assert has_return, "api_info has no return statement"
                    stmts = [
                        s for s in item.body
                        if not isinstance(s, ast.Pass)
                        and not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
                    ]
                    assert len(stmts) >= 1, "api_info body is a stub"
                    return
    raise AssertionError("ColoredCheckboxGroup.api_info not found")

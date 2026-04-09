"""
Task: gradio-html-server-functions
Repo: gradio-app/gradio @ 7c3fa2a6900cfa3c87cb61ffa9b34b75d1ae49ba
PR:   12929

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import sys
import subprocess
from pathlib import Path

REPO = "/workspace/gradio"

# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python files must parse without errors."""
    files_to_check = [
        f"{REPO}/gradio/components/html.py",
        f"{REPO}/client/js/src/client.ts",
    ]

    for file_path in files_to_check:
        if file_path.endswith(".py"):
            src = Path(file_path).read_text()
            try:
                ast.parse(src)
            except SyntaxError as e:
                raise AssertionError(f"Syntax error in {file_path}: {e}")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_html_accepts_server_functions():
    """gr.HTML component accepts server_functions parameter and stores it."""
    sys.path.insert(0, REPO)

    from gradio.components.html import HTML

    def sample_fn():
        return "test"

    # This should not raise an error
    html = HTML(value="test", server_functions=[sample_fn])

    # Verify server_functions is stored
    assert html.server_functions is not None, "server_functions should be stored"
    assert len(html.server_functions) == 1, "server_functions should have 1 function"
    assert html.server_functions[0] is sample_fn, "server_functions should contain the function"


# [pr_diff] fail_to_pass
def test_html_str_shows_server_functions():
    """gr.HTML __str__ method includes server_functions information."""
    sys.path.insert(0, REPO)

    from gradio.components.html import HTML

    def my_server_func():
        return "result"

    html = HTML(value="test", server_functions=[my_server_func])

    # __str__ should mention server_functions
    str_repr = str(html)
    assert "server_functions" in str_repr, f"__str__ should include server_functions: {str_repr}"
    assert "my_server_func" in str_repr, f"__str__ should include function name: {str_repr}"


# [pr_diff] fail_to_pass
def test_html_without_server_functions():
    """gr.HTML works normally without server_functions parameter."""
    sys.path.insert(0, REPO)

    from gradio.components.html import HTML

    # Should work without server_functions
    html = HTML(value="test")
    assert html.server_functions is None, "server_functions should be None by default"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rule from SKILL.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .agents/skills/gradio/SKILL.md:106 @ 7c3fa2a6900cfa3c87cb61ffa9b34b75d1ae49ba
def test_skill_md_documents_server_functions():
    """SKILL.md must document server_functions parameter in HTML signature."""
    skill_md_path = Path(REPO) / ".agents" / "skills" / "gradio" / "SKILL.md"

    assert skill_md_path.exists(), f"SKILL.md not found at {skill_md_path}"

    content = skill_md_path.read_text()

    # The SKILL.md should document the server_functions parameter in HTML signature
    assert "server_functions" in content, "SKILL.md should document server_functions parameter"

    # Check it's in the HTML component signature (not elsewhere)
    html_section = content.split("### `HTML(")[1] if "### `HTML(" in content else ""
    assert "server_functions" in html_section, "server_functions should be in HTML signature docs"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """HTML.__init__ has real implementation for server_functions, not just pass."""
    src = Path(f"{REPO}/gradio/components/html.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "__init__":
            # Count meaningful statements (not docstrings, not just self.x = x)
            stmts = []
            for s in node.body:
                if isinstance(s, ast.Pass):
                    continue
                if isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant):
                    # Skip docstrings
                    continue
                stmts.append(s)

            # Should have statements for server_functions handling
            assert len(stmts) >= 5, f"__init__ body too simple ({len(stmts)} stmts) - likely a stub"

            # Check for server_functions related code
            src_str = ast.unparse(node)
            assert "server_functions" in src_str, "__init__ should reference server_functions"

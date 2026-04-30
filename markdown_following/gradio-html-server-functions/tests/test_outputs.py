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
# Pass-to-pass (repo_tests) — repo CI tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_html_lint():
    """Ruff lint check passes on modified Python file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "ruff"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["python", "-m", "ruff", "check", f"{REPO}/gradio/components/html.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_html_format():
    """Ruff format check passes on modified Python file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "ruff"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["python", "-m", "ruff", "format", "--check", f"{REPO}/gradio/components/html.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_html_tests():
    """HTML component tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "pytest", "pytest-asyncio"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["pip", "install", "-q", "-e", f"{REPO}/client/python"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["pip", "install", "-q", "-e", f"{REPO}"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    r = subprocess.run(
        ["python", "-m", "pytest", f"{REPO}/test/components/test_html.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"HTML tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


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

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_lint():
    """pass_to_pass | CI job 'build' → step 'Lint'"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/lint_backend.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_typecheck():
    """pass_to_pass | CI job 'build' → step 'Typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/type_check_backend.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_build_wheel():
    """pass_to_pass | CI job 'build' → step 'Build wheel'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv pip install build && python -m build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build wheel' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_build_gradio_client_wheel():
    """pass_to_pass | CI job 'build' → step 'Build gradio_client wheel'"""
    r = subprocess.run(
        ["bash", "-lc", 'python -m build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build gradio_client wheel' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci__storybook_build_build_client():
    """pass_to_pass | CI job ':storybook-build' → step 'build client'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter @gradio/client build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'build client' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci__storybook_build_generate_theme_css():
    """pass_to_pass | CI job ':storybook-build' → step 'generate theme.css'"""
    r = subprocess.run(
        ["bash", "-lc", 'python scripts/generate_theme.py --outfile js/storybook/theme.css'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'generate theme.css' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci__storybook_build_pnpm():
    """pass_to_pass | CI job ':storybook-build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm exec playwright install chromium'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci__storybook_build_build_storybook():
    """pass_to_pass | CI job ':storybook-build' → step 'build storybook'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build-storybook --quiet --stats-json'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'build storybook' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_hygiene_test_generate_notebooks():
    """pass_to_pass | CI job 'hygiene-test' → step 'Generate Notebooks'"""
    r = subprocess.run(
        ["bash", "-lc", 'python3 -m venv venv && pip install nbformat && python scripts/generate_notebooks.py'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Generate Notebooks' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_hygiene_test_generate_skill():
    """pass_to_pass | CI job 'hygiene-test' → step 'Generate Skill'"""
    r = subprocess.run(
        ["bash", "-lc", 'pip install -e . && python scripts/generate_skill.py --check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Generate Skill' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_js_test_format_check():
    """pass_to_pass | CI job 'js-test' → step 'format check'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm format:check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'format check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_js_test_unit_tests():
    """pass_to_pass | CI job 'js-test' → step 'unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test:run'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
"""
Task: gradio-markdown-pending-show-progress
Repo: gradio-app/gradio @ a2bd6e1fb5d19e59ae694ab80c2874288e9982b8
PR:   #12958

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
import shutil
from pathlib import Path

REPO = "/workspace/gradio"
SVELTE_FILE = Path(REPO) / "js" / "markdown" / "Index.svelte"


def _extract_pending_expr() -> str:
    """Extract the class:pending={EXPR} expression from Index.svelte.

    Also resolves single-identifier expressions to their reactive definitions,
    in case the agent refactored to a $: reactive variable.
    """
    content = SVELTE_FILE.read_text()
    marker = "class:pending={"
    idx = content.find(marker)
    assert idx != -1, "class:pending directive not found in Index.svelte"

    start = idx + len(marker)
    depth = 1
    end = start
    for i in range(start, len(content)):
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
            if depth == 0:
                end = i
                break

    expr = " ".join(content[start:end].split()).strip()

    # If it's a simple identifier, resolve reactive definition
    if re.match(r"^[a-zA-Z_$]\w*$", expr):
        var_name = expr
        pattern = rf"(?:\$\s*:|let|const)\s+{re.escape(var_name)}\s*=\s*([\s\S]*?)(?:;|\n\s*(?:\$|let|const|export|<))"
        m = re.search(pattern, content)
        assert m, f"Could not resolve reactive var: {var_name}"
        expr = " ".join(m.group(1).split()).strip()

    return expr


def _eval_pending(expr: str, status: str, show_progress: str) -> bool:
    """Evaluate the pending expression with mocked gradio context via Node.js."""
    js_code = f"""
const gradio = {{
    shared: {{
        loading_status: {{
            status: {repr(status)},
            show_progress: {repr(show_progress)}
        }}
    }}
}};
const loading_status = gradio.shared.loading_status;
try {{
    const result = eval({repr(expr)});
    process.stdout.write(String(!!result));
}} catch (e) {{
    console.error('Eval error:', e.message);
    process.exit(1);
}}
"""
    r = subprocess.run(
        ["node", "-e", js_code],
        capture_output=True, timeout=10, text=True,
    )
    assert r.returncode == 0, f"Node eval failed: {r.stderr}"
    return r.stdout.strip() == "true"


def _eval_pending_undefined_progress(expr: str, status: str) -> bool:
    """Evaluate the pending expression when show_progress is not set."""
    js_code = f"""
const gradio = {{
    shared: {{
        loading_status: {{
            status: {repr(status)}
        }}
    }}
}};
const loading_status = gradio.shared.loading_status;
try {{
    const result = eval({repr(expr)});
    process.stdout.write(String(!!result));
}} catch (e) {{
    console.error('Eval error:', e.message);
    process.exit(1);
}}
"""
    r = subprocess.run(
        ["node", "-e", js_code],
        capture_output=True, timeout=10, text=True,
    )
    assert r.returncode == 0, f"Node eval failed: {r.stderr}"
    return r.stdout.strip() == "true"


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — file must exist and contain class:pending
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_svelte_file_exists():
    """Index.svelte must exist and contain a class:pending directive."""
    assert SVELTE_FILE.exists(), "js/markdown/Index.svelte not found"
    content = SVELTE_FILE.read_text()
    assert "class:pending" in content, "class:pending directive missing from Index.svelte"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_pending_false_when_hidden():
    """Pending must be FALSE when status=pending and show_progress=hidden (core bug)."""
    expr = _extract_pending_expr()
    assert _eval_pending(expr, "pending", "hidden") is False, (
        "class:pending should not activate when show_progress is hidden"
    )


# [pr_diff] pass_to_pass
def test_pending_true_when_full():
    """Pending must still be TRUE when status=pending and show_progress=full (regression guard)."""
    expr = _extract_pending_expr()
    assert _eval_pending(expr, "pending", "full") is True, (
        "class:pending should activate when show_progress is full"
    )


# [pr_diff] pass_to_pass
def test_pending_true_when_minimal():
    """Pending must be TRUE when status=pending and show_progress=minimal."""
    expr = _extract_pending_expr()
    assert _eval_pending(expr, "pending", "minimal") is True, (
        "class:pending should activate when show_progress is minimal"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — non-pending states and edge cases
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_pending_false_when_complete():
    """Pending must be FALSE when status=complete regardless of show_progress."""
    expr = _extract_pending_expr()
    for sp in ("full", "hidden", "minimal"):
        assert _eval_pending(expr, "complete", sp) is False, (
            f"class:pending should not activate when status=complete (show_progress={sp})"
        )


# [pr_diff] pass_to_pass
def test_pending_true_when_progress_undefined():
    """Pending must still work when show_progress is not set (backward compat)."""
    expr = _extract_pending_expr()
    assert _eval_pending_undefined_progress(expr, "pending") is True, (
        "class:pending should activate when status=pending and show_progress is undefined"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (static) — expression must differ from buggy original
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_expression_differs_from_buggy():
    """The class:pending expression must differ from the unchanged buggy original."""
    content = SVELTE_FILE.read_text()
    # The original buggy expression (single line, no show_progress check)
    buggy_expr = 'class:pending={gradio.shared.loading_status?.status === "pending"}'
    # The fixed expression should NOT match the buggy single-line pattern
    assert buggy_expr not in content, (
        "The class:pending expression still matches the buggy original - "
        "fix must add show_progress !== 'hidden' check"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — tab indentation from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:45 @ a2bd6e1fb5d19e59ae694ab80c2874288e9982b8
def test_tab_indentation():
    """Lines near class:pending must use tab indentation (matching file convention)."""
    content = SVELTE_FILE.read_text()
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if "class:pending" in line or "show_progress" in line:
            # Non-empty lines in the template section should be tab-indented
            if line.strip():
                assert line[0] == "\t", (
                    f"Line {i+1} should use tab indentation: {line!r}"
                )


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates — verify existing tests/lint still pass
# ---------------------------------------------------------------------------

# Global to track if pnpm is installed (installed on first test that needs it)
_pnpm_installed = False


def _ensure_pnpm():
    """Ensure pnpm is available, installing if needed. Returns pnpm path."""
    global _pnpm_installed
    if _pnpm_installed:
        return "pnpm"

    pnpm = shutil.which("pnpm")
    if pnpm:
        _pnpm_installed = True
        return "pnpm"

    # Install pnpm via npm
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm@10.17.0"],
        capture_output=True, text=True, timeout=120,
    )
    if r.returncode != 0:
        raise RuntimeError(f"Failed to install pnpm: {r.stderr}")

    _pnpm_installed = True
    return "pnpm"


def _install_deps():
    """Install dependencies if node_modules doesn't exist."""
    node_modules = Path(REPO) / "node_modules"
    if node_modules.exists():
        return

    pnpm = _ensure_pnpm()
    r = subprocess.run(
        [pnpm, "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    if r.returncode != 0:
        raise RuntimeError(f"Failed to install dependencies: {r.stderr[-1000:]}")


# [repo_tests] pass_to_pass — repo's Prettier format check
def test_repo_format_check():
    """Repo's Prettier format check passes (pass_to_pass)."""
    pnpm = _ensure_pnpm()
    _install_deps()
    r = subprocess.run(
        [pnpm, "format:check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — markdown component unit tests
def test_repo_markdown_unit_tests():
    """Markdown component unit tests pass (pass_to_pass)."""
    pnpm = _ensure_pnpm()
    _install_deps()

    # First build the client dependency
    r = subprocess.run(
        [pnpm, "--filter", "@gradio/client", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Client build failed:\n{r.stderr[-500:]}"

    # Run markdown-specific tests
    r = subprocess.run(
        [pnpm, "vitest", "run", "--config", ".config/vitest.config.ts", "js/markdown/Markdown.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Markdown unit tests failed:\n{r.stderr[-500:]}"

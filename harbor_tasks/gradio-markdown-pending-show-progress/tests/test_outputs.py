"""
Task: gradio-markdown-pending-show-progress
Repo: gradio-app/gradio @ a2bd6e1fb5d19e59ae694ab80c2874288e9982b8
PR:   #12958

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
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
# Anti-gaming (static) — expression must differ from buggy original
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_expression_differs_from_buggy():
    """The class:pending expression must not be the unchanged buggy original."""
    expr = _extract_pending_expr()
    normalized = expr.replace(" ", "")
    buggy = 'gradio.shared.loading_status?.status==="pending"'
    assert normalized != buggy, (
        "Expression is unchanged from the buggy original"
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

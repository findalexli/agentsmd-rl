"""
Task: openclaw-embeddings-http-write-scope
Repo: openclaw/openclaw @ 85647949a484957ba6bac00e47653b0acd4a92d7
PR:   #57721

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/openclaw")
SRC = REPO / "src/gateway/embeddings-http.ts"
BASE_COMMIT = "85647949a484957ba6bac00e47653b0acd4a92d7"

# AST-only because: TypeScript module with heavy Node/gateway deps; typescript
# compiler isn't installed in the container.  All checks use regex on the
# well-structured source, which is reliable for the patterns we're testing.


def _read_src() -> str:
    assert SRC.exists(), f"{SRC} not found"
    return SRC.read_text()


def _read_base_src() -> str:
    r = subprocess.run(
        ["git", "show", f"{BASE_COMMIT}:src/gateway/embeddings-http.ts"],
        capture_output=True, text=True, timeout=10, cwd=str(REPO),
    )
    assert r.returncode == 0, "Could not read base commit file"
    return r.stdout


def _extract_handler_body(content: str) -> str:
    """Extract the body of handleOpenAiEmbeddingsHttpRequest."""
    match = re.search(
        r'export\s+async\s+function\s+handleOpenAiEmbeddingsHttpRequest[^{]*\{',
        content,
    )
    assert match, "handleOpenAiEmbeddingsHttpRequest function not found"
    start = match.end()
    depth = 1
    pos = start
    while pos < len(content) and depth > 0:
        if content[pos] == '{':
            depth += 1
        elif content[pos] == '}':
            depth -= 1
        pos += 1
    return content[start:pos - 1]


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — file must exist and have content
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_ts_file_parses():
    """embeddings-http.ts exists and has meaningful content."""
    content = _read_src()
    assert len(content.strip()) > 500, "File is suspiciously short"
    # Basic structural check: balanced braces (within tolerance for template strings)
    opens = content.count("{")
    closes = content.count("}")
    assert abs(opens - closes) < 5, (
        f"Badly unbalanced braces: {opens} open vs {closes} close"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_embeddings_handler_enforces_scope():
    """handleGatewayPostJsonEndpoint call must include requiredOperatorMethod."""
    content = _read_src()
    assert "handleGatewayPostJsonEndpoint" in content, (
        "handleGatewayPostJsonEndpoint is not called in the handler"
    )
    # requiredOperatorMethod must be passed in the options object
    assert "requiredOperatorMethod" in content, (
        "requiredOperatorMethod not found — embeddings endpoint has no scope enforcement"
    )
    # Verify it's inside the handleGatewayPostJsonEndpoint call context
    body = _extract_handler_body(content)
    assert "requiredOperatorMethod" in body, (
        "requiredOperatorMethod is not in handleOpenAiEmbeddingsHttpRequest — "
        "it may be in the wrong function"
    )


# [pr_diff] fail_to_pass
def test_scope_method_is_chat_send():
    """requiredOperatorMethod must be 'chat.send' (the canonical write-gated method)."""
    content = _read_src()
    pattern = r"""requiredOperatorMethod\s*:\s*["']chat\.send["']"""
    assert re.search(pattern, content), (
        "requiredOperatorMethod is not set to 'chat.send'"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_handler_is_exported():
    """handleOpenAiEmbeddingsHttpRequest must remain an exported function."""
    content = _read_src()
    assert re.search(
        r'export\s+(async\s+)?function\s+handleOpenAiEmbeddingsHttpRequest',
        content,
    ), "handleOpenAiEmbeddingsHttpRequest is not an exported function"


# [pr_diff] pass_to_pass
def test_pathname_preserved():
    """Helper call must still register pathname '/v1/embeddings'."""
    body = _extract_handler_body(_read_src())
    assert re.search(
        r"""pathname\s*:\s*["']/v1/embeddings["']""",
        body,
    ), "pathname '/v1/embeddings' not found in handler"


# [static] pass_to_pass
def test_handler_not_stub():
    """Handler must retain substantial logic (not be gutted to a stub)."""
    body = _extract_handler_body(_read_src())
    lines = [l.strip() for l in body.splitlines() if l.strip()]
    assert len(lines) > 20, (
        f"Handler body has only {len(lines)} non-blank lines — likely a stub"
    )
    assert body.count("await ") >= 1, "Handler has no await — likely a stub"
    assert body.count("return ") >= 1, "Handler has no return — likely a stub"
    # Must make multiple calls (not just a single passthrough)
    call_count = len(re.findall(r'\w+\s*\(', body))
    assert call_count > 3, (
        f"Handler makes only {call_count} call(s) — likely a stub"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:146 @ 85647949a484957ba6bac00e47653b0acd4a92d7
def test_no_ts_nocheck():
    """Must not add @ts-nocheck directive (CLAUDE.md:146)."""
    content = _read_src()
    assert "@ts-nocheck" not in content, "@ts-nocheck found in embeddings-http.ts"


# [agent_config] pass_to_pass — CLAUDE.md:146 @ 85647949a484957ba6bac00e47653b0acd4a92d7
def test_no_lint_suppressions():
    """Must not add inline lint suppression comments (CLAUDE.md:146)."""
    content = _read_src()
    base_lines = set(_read_base_src().splitlines())
    new_lines = [l for l in content.splitlines() if l not in base_lines]
    suppressions = [
        pat for line in new_lines
        for pat in ("@ts-ignore", "@ts-expect-error", "eslint-disable", "oxlint-ignore")
        if pat in line
    ]
    assert not suppressions, (
        f"Lint suppression(s) found in new lines: {suppressions}"
    )


# [agent_config] pass_to_pass — CLAUDE.md:155 @ 85647949a484957ba6bac00e47653b0acd4a92d7
def test_no_mixed_dynamic_static_imports():
    """Must not mix await import() and static import for the same module (CLAUDE.md:155)."""
    content = _read_src()
    # Extract statically imported module specifiers
    static_modules = set(re.findall(
        r"""^import\s+.*?\s+from\s+["']([^"']+)["']""",
        content,
        re.MULTILINE,
    ))
    # Find any dynamic import() specifiers
    dynamic_modules = re.findall(
        r"""await\s+import\s*\(\s*["']([^"']+)["']\s*\)""",
        content,
    )
    conflicts = [m for m in dynamic_modules if m in static_modules]
    assert not conflicts, (
        f"Dynamic import() used for module(s) already statically imported: {conflicts}"
    )


# [agent_config] pass_to_pass — CLAUDE.md:144 @ 85647949a484957ba6bac00e47653b0acd4a92d7
def test_no_new_explicit_any():
    """Must not introduce new explicit 'any' type annotations (CLAUDE.md:144)."""
    content = _read_src()
    base_content = _read_base_src()
    # Count `: any` or `<any>` or `as any` patterns (type-position any)
    type_any_pattern = r'(?::\s*any\b|<any>|as\s+any\b)'
    current_count = len(re.findall(type_any_pattern, content))
    base_count = len(re.findall(type_any_pattern, base_content))
    assert current_count <= base_count, (
        f"New 'any' type annotations added: was {base_count}, now {current_count}"
    )


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates — verify repo's own checks pass
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's lint check (oxlint) passes on the codebase (pass_to_pass)."""
    # Install dependencies and run lint
    r = subprocess.run(
        ["bash", "-c", "pnpm install --frozen-lockfile >/dev/null 2>&1 && pnpm lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_embeddings_tests():
    """Repo's embeddings-http tests pass (pass_to_pass)."""
    # Install dependencies and run embeddings-specific tests
    r = subprocess.run(
        ["bash", "-c", "pnpm install --frozen-lockfile >/dev/null 2>&1 && pnpm exec vitest run --config vitest.gateway.config.ts src/gateway/embeddings-http.test.ts"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Embeddings tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    # Install dependencies and run TypeScript typecheck (tsgo is a fast Go-based TSC)
    r = subprocess.run(
        ["bash", "-c", "pnpm install --frozen-lockfile >/dev/null 2>&1 && ./node_modules/.bin/tsgo --noEmit"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"

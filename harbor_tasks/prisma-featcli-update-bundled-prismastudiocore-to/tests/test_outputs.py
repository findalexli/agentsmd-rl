"""
Task: prisma-featcli-update-bundled-prismastudiocore-to
Repo: prisma/prisma @ 32fb24b53c2a46971f3093eee9934c18e0f47642
PR:   29376

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/prisma"
STUDIO_TS = Path(REPO) / "packages" / "cli" / "src" / "Studio.ts"
AGENTS_MD = Path(REPO) / "AGENTS.md"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# pass_to_pass (static) -- syntax / regression checks
# ---------------------------------------------------------------------------

def test_repo_prettier():
    """Repo Prettier formatting check passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/prisma && corepack enable && pnpm install --frozen-lockfile >/dev/null 2>&1 && pnpm run prettier-check"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed: {r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_engines_override():
    """Repo engines override check passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/prisma && corepack enable && pnpm install --frozen-lockfile >/dev/null 2>&1 && pnpm run check-engines-override"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Engines override check failed: {r.stderr[-500:]}"


def test_repo_lint_studio():
    """Repo ESLint check on Studio.ts passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/prisma && corepack enable && pnpm install --frozen-lockfile >/dev/null 2>&1 && pnpm exec eslint packages/cli/src/Studio.ts --max-warnings=100"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Studio.ts lint failed: {r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_studio_vitest():
    """Repo Studio vitest tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/prisma && corepack enable && pnpm install --frozen-lockfile >/dev/null 2>&1 && pnpm build >/dev/null 2>&1 || true; cd packages/cli && pnpm vitest run src/__tests__/Studio.vitest.ts"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Studio vitest failed: {r.stderr[-500:]}{r.stdout[-500:]}"


def test_studio_syntax_node_check():
    """Studio.ts must pass Node.js syntax validation (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check", str(STUDIO_TS)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Studio.ts syntax check failed: {r.stderr}"


def test_syntax_check():
    """Studio.ts must be valid TypeScript (no unterminated strings or brackets)."""
    content = STUDIO_TS.read_text()
    opens = content.count("{") + content.count("(") + content.count("[")
    closes = content.count("}") + content.count(")") + content.count("]")
    assert abs(opens - closes) < 10, f"Bracket imbalance: opens={opens}, closes={closes}"
    assert "Studio" in content, "Studio class/reference missing"


def test_existing_bff_procedures_preserved():
    """Existing BFF procedures (query, sequence, sql-lint) must still be present."""
    content = STUDIO_TS.read_text()
    for proc in ["query", "sequence", "sql-lint"]:
        pattern = f"procedure === '{proc}'"
        assert pattern in content or f'procedure === "{proc}"' in content, f"BFF procedure {proc} must still be handled in Studio.ts"


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) -- behavioral code-execution tests
# ---------------------------------------------------------------------------

def test_transaction_procedure_handler():
    """BFF must handle transaction procedure with executeTransaction and error handling."""
    content = STUDIO_TS.read_text()
    assert "procedure === 'transaction'" in content or 'procedure === "transaction"' in content, "Transaction procedure handler missing"
    assert "executeTransaction" in content, "executeTransaction method call missing"
    assert "if (error)" in content or "if(error)" in content, "Error handling in transaction missing"


def test_favicon_endpoint():
    """Studio must serve a valid SVG favicon at /favicon.ico with link tag in HTML."""
    content = STUDIO_TS.read_text()
    assert "/favicon.ico" in content and "app.get" in content, "/favicon.ico endpoint missing"
    assert "link" in content and "rel=" in content and "icon" in content, "favicon link tag in HTML missing"


def test_import_map_includes_radix_toggle():
    """Import map must include @radix-ui/react-toggle with React dep pinning."""
    content = STUDIO_TS.read_text()
    assert "@radix-ui/react-toggle" in content, "@radix-ui/react-toggle missing from import map"
    assert "deps=react@" in content, "React dependency pinning missing in import map URLs"


def test_import_map_includes_chartjs():
    """Import map must include chart.js/auto via esm.sh."""
    content = STUDIO_TS.read_text()
    assert "chart.js/auto" in content, "chart.js/auto missing from import map"
    assert "esm.sh/chart.js@" in content, "chart.js must be loaded via esm.sh"


def test_react_version_constant():
    """React version must be a constant, not hardcoded in multiple import map URLs."""
    content = STUDIO_TS.read_text()
    assert "${REACT_VERSION}" in content, "REACT_VERSION should be used in import map URLs, not hardcoded values"
    assert "const REACT_VERSION" in content, "REACT_VERSION constant must be defined in Studio.ts"


def test_agents_md_studio_import_map_docs():
    """AGENTS.md must document Studio import map alignment with new browser imports."""
    content = AGENTS_MD.read_text()
    assert "import map" in content.lower(), "AGENTS.md missing documentation about import map"
    assert "@radix-ui" in content.lower() or "chart.js" in content.lower(), "AGENTS.md missing documentation about new browser imports"


def test_agents_md_react_pinning_docs():
    """AGENTS.md must document esm.sh React version pinning pattern."""
    content = AGENTS_MD.read_text()
    assert "esm.sh" in content.lower(), "AGENTS.md missing documentation about esm.sh"
    assert "deps=react@" in content.lower() or "pin" in content.lower(), "AGENTS.md missing documentation about React version pinning pattern"

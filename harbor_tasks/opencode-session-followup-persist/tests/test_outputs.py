"""
Task: opencode-session-followup-persist
Repo: anomalyco/opencode @ 3fb60d05e555dad020d3354602affe166ef0cc22
PR:   19421

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

SolidJS components cannot execute without a browser DOM.
All tests use file/AST analysis — justified for a UI component.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
FILE = Path(REPO) / "packages/app/src/pages/session.tsx"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_file():
    assert FILE.exists(), f"session.tsx not found at {FILE}"
    return FILE.read_text()


def _install_babel():
    """Install babel parser in /tmp to avoid pnpm catalog: protocol issues."""
    marker = Path("/tmp/babel-env/node_modules/@babel/parser")
    if not marker.exists():
        subprocess.run(
            "mkdir -p /tmp/babel-env && cd /tmp/babel-env && npm install @babel/parser",
            shell=True, capture_output=True, timeout=60,
        )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_parses_as_tsx():
    """session.tsx must parse as valid TypeScript+JSX."""
    _install_babel()
    code = _read_file()
    r = subprocess.run(
        ["node", "-e", """
const { parse } = require('@babel/parser');
const fs = require('fs');
parse(fs.readFileSync(process.argv[1], 'utf8'), {
  sourceType: 'module',
  plugins: ['typescript', 'jsx'],
});
console.log('ok');
""", str(FILE)],
        capture_output=True, timeout=30,
        env={"NODE_PATH": "/tmp/babel-env/node_modules", "PATH": "/usr/local/bin:/usr/bin:/bin"},
    )
    assert r.stdout.decode().strip() == "ok", (
        f"TypeScript parse failed: {r.stderr.decode()[:500]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_followup_store_wrapped_with_persistence():
    """Followup store must be wrapped with a persistence layer (persisted/makePersisted/custom)."""
    code = _read_file()
    lines = code.splitlines()

    # Collect names imported from any persist-related module
    persist_names = set()
    for line in lines:
        m = re.match(r'import\s+\{([^}]+)\}\s+from\s+["\']([^"\']*persist[^"\']*)["\']', line, re.I)
        if m:
            for name in m.group(1).split(","):
                persist_names.add(name.strip().split(" as ")[-1].strip())

    assert persist_names, "No imports from any persist-related module found"

    # Find the followup store declaration and check it uses a persist function
    found = False
    for i, line in enumerate(lines):
        if "followup" in line.lower() and ("createStore" in line or "=" in line):
            ctx = "\n".join(lines[max(0, i - 10):min(len(lines), i + 15)])
            for name in persist_names:
                if re.search(re.escape(name) + r"\s*[(<]", ctx):
                    found = True
                    break
        if found:
            break

    # Also check: any persist function near createStore + followup
    if not found:
        for i, line in enumerate(lines):
            for name in persist_names:
                if re.search(re.escape(name) + r"\s*[(<]", line):
                    ctx = "\n".join(lines[max(0, i - 10):min(len(lines), i + 10)])
                    if "createStore" in ctx and "followup" in ctx.lower():
                        found = True
                        break
            if found:
                break

    assert found, (
        f"Followup store not wrapped with persistence. "
        f"Found persist imports: {persist_names}"
    )


# [pr_diff] fail_to_pass
def test_persistence_workspace_scoped():
    """Persistence must be workspace-scoped (per-project), not global."""
    code = _read_file()
    lines = code.splitlines()

    found = False
    for i, line in enumerate(lines):
        ctx = "\n".join(lines[max(0, i - 8):min(len(lines), i + 8)])
        has_followup_context = "followup" in ctx.lower() or "persist" in ctx.lower()

        if not has_followup_context:
            continue

        # Strategy 1: Persist.workspace() API
        if re.search(r"\.\s*workspace\s*\(", line):
            found = True
            break

        # Strategy 2: workspace/directory path used as key near persistence
        if re.search(r"\b(?:workspace|directory|sdk\.dir)", line, re.I):
            if "persist" in ctx.lower():
                found = True
                break

        # Strategy 3: storage key includes scope/project reference
        if "persist" in line.lower() and "followup" in line.lower():
            if re.search(r"workspace|directory|project|scope", ctx, re.I):
                found = True
                break

    assert found, "Persistence is not workspace-scoped — followups would be lost on project switch"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_page_default_export():
    """Page function must remain the default export."""
    code = _read_file()
    assert re.search(r"export\s+default\s+function\s+Page", code), (
        "Page function is no longer default-exported"
    )


# [pr_diff] pass_to_pass
def test_followup_store_core_fields():
    """Followup store must retain its core fields: items, failed, paused, edit."""
    code = _read_file()
    required = ["items", "failed", "paused", "edit"]
    found = [f for f in required if re.search(rf'\b{f}\s*:', code) or f'"{f}"' in code or f"'{f}'" in code]
    assert len(found) >= 3, (
        f"Followup store missing fields. Found: {found}, need at least 3 of {required}"
    )


# [static] pass_to_pass
def test_file_not_stubbed():
    """session.tsx must retain original component complexity — not gutted."""
    code = _read_file()
    lines = code.splitlines()

    # Non-empty, non-comment lines
    code_lines = [
        l for l in lines
        if l.strip() and not l.strip().startswith("//") and not l.strip().startswith("/*") and not l.strip().startswith("*")
    ]
    assert len(code_lines) >= 100, f"Only {len(code_lines)} code lines — file appears gutted"

    # Multiple function definitions
    func_count = len(re.findall(
        r"(?:function\s+\w+|\b\w+\s*=\s*(?:async\s+)?\([^)]*\)\s*(?:=>|:))", code
    ))
    assert func_count >= 5, f"Only {func_count} functions — file appears stubbed"

    # Multiple SolidJS primitives
    primitives = ["createEffect", "createMemo", "createStore", "onCleanup", "onMount", "Show", "For", "createComputed"]
    found = sum(1 for p in primitives if p in code)
    assert found >= 3, f"Only {found} SolidJS primitives found — file appears stubbed"

    # Must contain JSX
    assert re.search(r"<\w+[\s/>]", code), "No JSX found — not a valid component"


# [static] pass_to_pass
def test_no_stub_markers_near_persistence():
    """No TODO/FIXME/stub markers near followup persistence code."""
    code = _read_file()
    lines = code.splitlines()
    markers = ["todo", "fixme", "stub", "not implemented", "placeholder"]
    for i, line in enumerate(lines):
        low = line.lower()
        if any(m in low for m in markers):
            ctx = "\n".join(lines[max(0, i - 10):i + 10]).lower()
            assert not ("followup" in ctx or "persist" in ctx), (
                f"Stub marker found near persistence code at line {i + 1}: {line.strip()}"
            )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:13 @ 3fb60d05e555dad020d3354602affe166ef0cc22
def test_no_any_type_in_followup_block():
    """No 'any' type usage in followup persistence block (AGENTS.md: 'Avoid using the any type')."""
    code = _read_file()
    # Find the followup store region (declaration through next top-level const/function)
    match = re.search(
        r"(?:persisted|const\s+\[followup).*?(?=\n(?:const |let |function |export |//\s*=)|\Z)",
        code, re.DOTALL,
    )
    if match:
        block = match.group(0)
        assert "as any" not in block, "'as any' found in followup persistence block"
        assert not re.search(r":\s*any[\s;,>)]", block), "': any' type annotation found in followup persistence block"


# [agent_config] pass_to_pass — packages/app/AGENTS.md:15 @ 3fb60d05e555dad020d3354602affe166ef0cc22
def test_followup_uses_create_store_not_signal():
    """Followup state must use createStore, not multiple createSignal calls (packages/app/AGENTS.md)."""
    code = _read_file()
    lines = code.splitlines()
    signal_near_followup = 0
    for i, line in enumerate(lines):
        if "createSignal" in line:
            ctx = "\n".join(lines[max(0, i - 3):i + 3])
            if any(kw in ctx.lower() for kw in ["followup", "items", "paused"]):
                signal_near_followup += 1
    assert signal_near_followup == 0, (
        f"createSignal used {signal_near_followup} times near followup state — use createStore instead"
    )


def _followup_region():
    """Extract ~30 lines starting from the followup store declaration."""
    code = _read_file()
    lines = code.splitlines()
    for i, line in enumerate(lines):
        if re.search(r'(?:persisted|const\s+\[followup)', line):
            return "\n".join(lines[i:min(len(lines), i + 30)])
    return ""


# [agent_config] pass_to_pass — AGENTS.md:12 @ 3fb60d05e555dad020d3354602affe166ef0cc22
def test_no_try_catch_in_followup_block():
    """No try/catch in followup persistence block (AGENTS.md: 'Avoid try/catch where possible')."""
    region = _followup_region()
    assert region, "Could not locate followup store region"
    assert not re.search(r'\btry\s*\{', region), "try/catch found in followup persistence block"


# [agent_config] pass_to_pass — AGENTS.md:84 @ 3fb60d05e555dad020d3354602affe166ef0cc22
def test_no_else_in_followup_block():
    """No 'else' statements in followup persistence block (AGENTS.md: 'Avoid else, prefer early returns')."""
    region = _followup_region()
    assert region, "Could not locate followup store region"
    assert not re.search(r'\belse\b', region), "else statement found in followup persistence block"


# [agent_config] pass_to_pass — AGENTS.md:17 @ 3fb60d05e555dad020d3354602affe166ef0cc22
def test_no_for_loop_in_followup_block():
    """No for loops in followup persistence block (AGENTS.md: 'Prefer functional array methods over for loops')."""
    region = _followup_region()
    assert region, "Could not locate followup store region"
    assert not re.search(r'\bfor\s*\(', region), "for loop found in followup persistence block — use functional methods"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_turbo_typecheck():
    """Repo's global turbo typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "apt-get update -qq && apt-get install -y -qq unzip 2>/dev/null && curl -fsSL https://bun.sh/install | bash 2>/dev/null && export PATH=\"/root/.bun/bin:\$PATH\" && bun install 2>&1 >/dev/null && bun turbo typecheck"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Global turbo typecheck failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier_check():
    """Repo's prettier formatting check passes for the modified file (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "apt-get update -qq && apt-get install -y -qq unzip 2>/dev/null && curl -fsSL https://bun.sh/install | bash 2>/dev/null && export PATH=\"/root/.bun/bin:\$PATH\" && bun install 2>&1 >/dev/null && bunx prettier --check packages/app/src/pages/session.tsx"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_app_build():
    """Repo's app package build passes (pass_to_pass)."""
    app_dir = Path(REPO) / "packages" / "app"
    r = subprocess.run(
        ["bash", "-c", "apt-get update -qq && apt-get install -y -qq unzip 2>/dev/null && curl -fsSL https://bun.sh/install | bash 2>/dev/null && export PATH=\"/root/.bun/bin:\$PATH\" && bun install 2>&1 >/dev/null && bun run build"],
        capture_output=True, text=True, timeout=300, cwd=app_dir,
    )
    assert r.returncode == 0, f"App build failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_app_typecheck():
    """Repo's app package TypeScript typecheck passes (pass_to_pass)."""
    app_dir = Path(REPO) / "packages" / "app"
    r = subprocess.run(
        ["bash", "-c", "apt-get update -qq && apt-get install -y -qq unzip 2>/dev/null && curl -fsSL https://bun.sh/install | bash 2>/dev/null && export PATH=\"/root/.bun/bin:\\$PATH\" && bun install 2>&1 >/dev/null && bun run typecheck"],
        capture_output=True, text=True, timeout=180, cwd=app_dir,
    )
    assert r.returncode == 0, f"App typecheck failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_app_unit_tests():
    """Repo's app package unit tests pass (pass_to_pass)."""
    app_dir = Path(REPO) / "packages" / "app"
    r = subprocess.run(
        ["bash", "-c", "apt-get update -qq && apt-get install -y -qq unzip 2>/dev/null && curl -fsSL https://bun.sh/install | bash 2>/dev/null && export PATH=\"/root/.bun/bin:\\$PATH\" && bun install 2>&1 >/dev/null && bun run test:unit"],
        capture_output=True, text=True, timeout=180, cwd=app_dir,
    )
    assert r.returncode == 0, f"App unit tests failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"

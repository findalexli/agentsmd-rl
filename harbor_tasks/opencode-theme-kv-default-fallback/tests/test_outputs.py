"""
Task: opencode-theme-kv-default-fallback
Repo: anomalyco/opencode @ 26382c6216797e65a1b43dea8646725332f62e07
PR:   506

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

WHY NODE EXEC: The target is a SolidJS createMemo callback inside a
ThemeProvider that requires the full reactive runtime, useKV/useRenderer
providers, and @opentui/core. None of these are installable without a
full monorepo build.  We extract the memo body and execute it in Node.js
with lightweight mocks for store, kv, and resolveTheme.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/repo"
FILE = f"{REPO}/packages/opencode/src/cli/cmd/tui/context/theme.tsx"


def _read_file():
    return Path(FILE).read_text()


def _extract_values_memo(src: str) -> str:
    """Extract the body of `const values = createMemo(...)` using brace counting.
    Comments are stripped to prevent comment-injection gaming."""
    stripped = re.sub(r"//[^\n]*", "", src)
    stripped = re.sub(r"/\*[\s\S]*?\*/", "", stripped)
    idx = stripped.find("const values = createMemo")
    if idx == -1:
        return ""
    brace = stripped.find("{", idx)
    if brace == -1:
        return ""
    depth = 1
    i = brace + 1
    while i < len(stripped) and depth > 0:
        if stripped[i] == "{":
            depth += 1
        elif stripped[i] == "}":
            depth -= 1
        i += 1
    return stripped[brace + 1 : i - 1]


def _run_memo(themes: dict, active: str, kv_theme, mode: str = "dark") -> str:
    """Execute the extracted memo body in Node.js with mocks.

    Each theme value is a unique marker string (e.g. "T:dracula").
    resolveTheme is an identity mock, so the return value tells us
    which theme was selected.
    """
    memo = _extract_values_memo(_read_file())
    assert memo, "Could not extract createMemo body"

    js = (
        "const store = {themes: %s, active: %s, mode: %s};\n"
        "const kv = {get(key) {return %s;}};\n"
        "function resolveTheme(t, m) {return t;}\n"
        "const result = (function() {\n%s\n})();\n"
        "console.log(result);\n"
        % (
            json.dumps(themes),
            json.dumps(active),
            json.dumps(mode),
            json.dumps(kv_theme),
            memo,
        )
    )

    r = subprocess.run(
        ["node"], input=js, capture_output=True, text=True, timeout=10
    )
    assert r.returncode == 0, f"Node.js execution failed:\n{r.stderr}"
    return r.stdout.strip()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_exists_and_not_stub():
    """Target file exists and has substantial content."""
    src = _read_file()
    assert len(src.splitlines()) >= 200, "File has too few lines — likely stubbed"


# [static] pass_to_pass
def test_syntax_balanced_braces():
    """File has balanced curly braces (basic syntax sanity)."""
    r = subprocess.run(
        [
            "node", "-e",
            "const s=require('fs').readFileSync(process.argv[1],'utf8');"
            "let d=0;for(const c of s){if(c==='{')d++;if(c==='}')d--;if(d<0)process.exit(1);}"
            "if(d!==0)process.exit(1);",
            FILE,
        ],
        capture_output=True, timeout=10,
    )
    assert r.returncode == 0, "File has unbalanced braces"


# [static] pass_to_pass
def test_memo_block_exists():
    """The `const values = createMemo` block exists and is non-trivial."""
    memo = _extract_values_memo(_read_file())
    assert len(memo) > 10, "createMemo 'values' block not found or too small"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_kv_fallback_when_active_missing():
    """When active theme is not in themes map, the KV-saved theme is used."""
    themes = {"opencode": "T:opencode", "dracula": "T:dracula"}
    result = _run_memo(themes, active="custom-removed", kv_theme="dracula")
    assert result == "T:dracula", (
        f"Expected KV-saved 'dracula' theme but got {result!r}"
    )


# [pr_diff] fail_to_pass
def test_kv_fallback_varied_themes():
    """KV fallback works with multiple different saved theme names."""
    for name in ["catppuccin", "nord", "solarized"]:
        themes = {"opencode": "T:opencode", name: f"T:{name}"}
        result = _run_memo(themes, active="deleted-theme", kv_theme=name)
        assert result == f"T:{name}", (
            f"Expected KV-saved '{name}' but got {result!r}"
        )


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — behavioral regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_active_theme_used_when_present():
    """When active theme exists in the map, it is used (KV ignored)."""
    for active_name in ["dracula", "nord", "opencode"]:
        themes = {
            "opencode": "T:opencode",
            "dracula": "T:dracula",
            "nord": "T:nord",
        }
        result = _run_memo(themes, active=active_name, kv_theme="solarized")
        assert result == f"T:{active_name}", (
            f"Expected active '{active_name}' but got {result!r}"
        )


# [pr_diff] pass_to_pass
def test_opencode_fallback_when_kv_invalid():
    """Falls back to opencode when active is missing AND KV names a
    theme not in the map."""
    themes = {"opencode": "T:opencode", "dracula": "T:dracula"}
    result = _run_memo(themes, active="gone", kv_theme="nonexistent")
    assert result == "T:opencode", (
        f"Expected 'opencode' fallback but got {result!r}"
    )


# [pr_diff] pass_to_pass
def test_opencode_fallback_when_kv_not_string():
    """Falls back to opencode when KV value is not a string."""
    themes = {"opencode": "T:opencode"}
    for kv_val in [None, 42, True]:
        result = _run_memo(themes, active="gone", kv_theme=kv_val)
        assert result == "T:opencode", (
            f"Expected 'opencode' for kv={kv_val!r} but got {result!r}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — export preservation
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_resolve_theme_exported():
    """resolveTheme function must still be exported."""
    assert "export function resolveTheme" in _read_file()


# [repo_tests] pass_to_pass
def test_use_theme_provider_exported():
    """useTheme and ThemeProvider must still be exported."""
    src = _read_file()
    assert re.search(
        r"use:\s*useTheme.*provider:\s*ThemeProvider"
        r"|provider:\s*ThemeProvider.*use:\s*useTheme",
        src,
    )


# [repo_tests] pass_to_pass
def test_default_themes_exported():
    """DEFAULT_THEMES record must still be exported."""
    assert "export const DEFAULT_THEMES" in _read_file()


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:13 @ 26382c6
def test_no_any_type_in_memo():
    """No 'any' type in the values memo (AGENTS.md: Avoid using the any type)."""
    memo = _extract_values_memo(_read_file())
    assert not re.search(r":\s*any\b|as\s+any\b|<any>", memo), (
        "'any' type found in values memo"
    )


# [agent_config] pass_to_pass — AGENTS.md:12 @ 26382c6
def test_no_try_catch_in_memo():
    """No try/catch in the values memo (AGENTS.md: Avoid try/catch)."""
    memo = _extract_values_memo(_read_file())
    assert not re.search(r"\btry\s*\{", memo), "try/catch found in values memo"


# [agent_config] pass_to_pass — AGENTS.md:17 @ 26382c6
def test_no_for_loops_in_memo():
    """No for/while loops in the values memo (AGENTS.md: prefer functional array methods over loops)."""
    memo = _extract_values_memo(_read_file())
    assert not re.search(r"\bfor\s*\(|\bwhile\s*\(", memo), (
        "for/while loop found in values memo — prefer functional array methods"
    )


# [agent_config] pass_to_pass — AGENTS.md:70 @ 26382c6
def test_prefer_const_in_memo():
    """No 'let' declarations in the values memo (AGENTS.md: Prefer const over let)."""
    memo = _extract_values_memo(_read_file())
    assert not re.search(r"\blet\s+\w+", memo), (
        "'let' found in values memo — prefer const with early returns"
    )


# ---------------------------------------------------------------------------
# Repo CI/CD (pass_to_pass) — ensure repo's own checks pass on base commit
# ---------------------------------------------------------------------------

def _ensure_bun_and_deps():
    """Ensure bun is installed and dependencies are available (installs if missing)."""
    bun_check = subprocess.run(["which", "bun"], capture_output=True)
    if bun_check.returncode != 0:
        # Install unzip first (required for bun install)
        subprocess.run(
            ["apt-get", "update", "-qq"],
            capture_output=True, timeout=60,
        )
        subprocess.run(
            ["apt-get", "install", "-y", "-qq", "unzip"],
            capture_output=True, timeout=60,
        )
        # Install bun
        install = subprocess.run(
            ["bash", "-c",
             "curl -fsSL https://bun.sh/install | bash && mv /root/.bun/bin/bun /usr/local/bin/bun"],
            capture_output=True, text=True, timeout=120,
        )
        assert install.returncode == 0, f"Bun install failed: {install.stderr}"

    # Check if node_modules exists at root (needed for workspace deps)
    if not Path(f"{REPO}/node_modules").exists():
        # Install dependencies at root
        r = subprocess.run(
            ["bun", "install"],
            capture_output=True, text=True, timeout=300, cwd=REPO,
        )
        assert r.returncode == 0, f"bun install failed: {r.stderr[-500:]}"

    return "/usr/local/bin/bun"


# [repo_tests] pass_to_pass — repo's TypeScript typecheck for opencode package
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes on packages/opencode (pass_to_pass).

    Installs Bun at runtime since the repo uses bun-specific features (catalog:).
    Uses tsgo which is the typecheck command defined in package.json.
    """
    opencode_dir = f"{REPO}/packages/opencode"
    _ensure_bun_and_deps()

    # Run typecheck via bun in the opencode package
    # The typecheck script runs: tsgo --noEmit
    r = subprocess.run(
        ["bun", "run", "typecheck"],
        capture_output=True, text=True, timeout=300, cwd=opencode_dir,
    )
    assert r.returncode == 0, f"Typecheck failed:\nstdout: {r.stdout[-1000:]}\nstderr: {r.stderr[-500:]}"


# [repo_tests] pass_to_pass — turbo typecheck at root (CI command)
def test_repo_turbo_typecheck():
    """Root turbo typecheck passes (CI command: bun turbo typecheck) (pass_to_pass).

    Matches the CI typecheck command from .github/workflows/typecheck.yml.
    """
    _ensure_bun_and_deps()

    # Run turbo typecheck from root (this is what CI runs)
    r = subprocess.run(
        ["bun", "turbo", "typecheck"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Turbo typecheck failed:\nstdout: {r.stdout[-1000:]}\nstderr: {r.stderr[-500:]}"


# [repo_tests] pass_to_pass — theme store tests specifically for modified theme.tsx
def test_repo_theme_store_tests():
    """Theme store unit tests pass (covers theme.tsx context) (pass_to_pass).

    Runs bun test on test/cli/tui/theme-store.test.ts which tests the
    same theme.tsx module that the PR modifies.
    """
    opencode_dir = f"{REPO}/packages/opencode"
    _ensure_bun_and_deps()

    # Run only theme-store tests which cover the modified theme.tsx file
    r = subprocess.run(
        ["bun", "test", "test/cli/tui/theme-store.test.ts", "--timeout", "30000"],
        capture_output=True, text=True, timeout=300, cwd=opencode_dir,
    )
    assert r.returncode == 0, f"Theme store tests failed:\nstdout: {r.stdout[-1000:]}\nstderr: {r.stderr[-500:]}"


# [repo_tests] pass_to_pass — all TUI tests (stable subset)
def test_repo_tui_tests():
    """All TUI unit tests pass (pass_to_pass).

    Runs bun test on test/cli/tui/ directory which covers TUI components
    including the theme.tsx context that the PR modifies.
    """
    opencode_dir = f"{REPO}/packages/opencode"
    _ensure_bun_and_deps()

    # Run all TUI tests - these are stable (43 tests pass)
    r = subprocess.run(
        ["bun", "test", "test/cli/tui/", "--timeout", "30000"],
        capture_output=True, text=True, timeout=300, cwd=opencode_dir,
    )
    assert r.returncode == 0, f"TUI tests failed:\nstdout: {r.stdout[-1000:]}\nstderr: {r.stderr[-500:]}"


# [repo_tests] pass_to_pass — prettier formatting check on theme.tsx
def test_repo_prettier_theme():
    """Prettier formatting check passes on theme.tsx (pass_to_pass).

    Runs npx prettier --check on the modified file to ensure code style compliance.
    """
    _ensure_bun_and_deps()

    # Run prettier check on the modified theme.tsx file
    r = subprocess.run(
        ["npx", "prettier", "--check", "packages/opencode/src/cli/cmd/tui/context/theme.tsx"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"

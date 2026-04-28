"""Behavioral and structural tests for the config-module split refactor.

The fail_to_pass tests assert that:
  * formatter.ts and lsp.ts exist as dedicated modules under
    packages/opencode/src/config/, follow the self-export pattern, and
    expose schemas with the same parse/refine behavior as before.
  * config.ts no longer holds the inline schemas, instead pulling them
    from the new modules.
  * The package's index.ts re-exports the new namespaces.
  * Both AGENTS.md files document the convention.

The pass_to_pass tests guard against accidentally breaking sibling config
modules (agent.ts, permission.ts) during the split.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/opencode")
CFG = REPO / "packages/opencode/src/config"
TESTS = Path("/tests")


def _run(cmd: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(REPO))


# ── fail_to_pass ──────────────────────────────────────────────────────────


def test_formatter_module_schema_behavior():
    r = _run(["bun", "run", str(TESTS / "probe_formatter.ts")], timeout=60)
    combined = (r.stdout or "") + "\n" + (r.stderr or "")
    assert r.returncode == 0, f"probe_formatter failed:\n{combined}"
    assert "FORMATTER_OK" in r.stdout, f"probe_formatter did not print FORMATTER_OK:\n{combined}"


def test_lsp_module_schema_behavior():
    r = _run(["bun", "run", str(TESTS / "probe_lsp.ts")], timeout=60)
    combined = (r.stdout or "") + "\n" + (r.stderr or "")
    assert r.returncode == 0, f"probe_lsp failed:\n{combined}"
    assert "LSP_OK" in r.stdout, f"probe_lsp did not print LSP_OK:\n{combined}"


def test_formatter_self_export_at_top():
    src = (CFG / "formatter.ts").read_text()
    first_nonempty = next((ln for ln in src.splitlines() if ln.strip()), "")
    assert re.fullmatch(
        r'\s*export\s*\*\s*as\s+ConfigFormatter\s+from\s+["\']\./formatter["\']\s*;?\s*',
        first_nonempty,
    ), f"formatter.ts must start with self-export pattern; got: {first_nonempty!r}"


def test_lsp_self_export_at_top():
    src = (CFG / "lsp.ts").read_text()
    first_nonempty = next((ln for ln in src.splitlines() if ln.strip()), "")
    assert re.fullmatch(
        r'\s*export\s*\*\s*as\s+ConfigLSP\s+from\s+["\']\./lsp["\']\s*;?\s*',
        first_nonempty,
    ), f"lsp.ts must start with self-export pattern; got: {first_nonempty!r}"


def test_index_reexports_new_modules():
    src = (CFG / "index.ts").read_text()
    assert re.search(
        r'export\s*\*\s*as\s+ConfigFormatter\s+from\s+["\']\./formatter["\']', src
    ), "index.ts must re-export ConfigFormatter from ./formatter"
    assert re.search(
        r'export\s*\*\s*as\s+ConfigLSP\s+from\s+["\']\./lsp["\']', src
    ), "index.ts must re-export ConfigLSP from ./lsp"


def test_config_ts_uses_imported_schemas():
    src = (CFG / "config.ts").read_text()
    assert "ConfigFormatter.Info" in src, \
        "config.ts must reference ConfigFormatter.Info from the new module"
    assert "ConfigLSP.Info" in src, \
        "config.ts must reference ConfigLSP.Info from the new module"


def test_config_ts_no_longer_has_inline_lsp_refine():
    src = (CFG / "config.ts").read_text()
    assert "For custom LSP servers, 'extensions' array is required." not in src, (
        "config.ts still defines the inline lsp refinement; "
        "that schema (and message) should live in the dedicated lsp.ts module"
    )
    # The inline `formatter:` schema in config.ts had a literal z.union with z.literal(false)
    # nested under it. After the refactor, config.ts should no longer import LSPServer at all.
    assert not re.search(
        r'import\s*\*\s*as\s+LSPServer\s+from\s+["\']\.\./lsp/server["\']', src
    ), "config.ts should no longer import LSPServer directly; it now lives in lsp.ts"


def test_root_agents_md_documents_self_export_pattern():
    md = (REPO / "AGENTS.md").read_text()
    assert "src/config" in md, "root AGENTS.md must mention src/config in the new rule"
    assert re.search(r"self[- ]export", md, re.IGNORECASE), \
        "root AGENTS.md must mention the self-export pattern"
    assert "export *" in md, \
        "root AGENTS.md must include the literal `export *` form (the pattern example)"


def test_pkg_agents_md_documents_self_export_pattern():
    md = (REPO / "packages/opencode/AGENTS.md").read_text()
    assert "src/config" in md, "packages/opencode/AGENTS.md must mention src/config"
    assert re.search(r"self[- ]export", md, re.IGNORECASE), \
        "packages/opencode/AGENTS.md must mention the self-export pattern"


# ── pass_to_pass ──────────────────────────────────────────────────────────


def test_other_config_modules_unchanged_self_export():
    """Sibling config modules' self-export pattern is preserved (regression guard)."""
    for name in ("agent", "command", "error", "parse", "paths", "permission",
                "managed", "keybinds", "variable"):
        src = (CFG / f"{name}.ts").read_text()
        first_nonempty = next((ln for ln in src.splitlines() if ln.strip()), "")
        # Some files lead with `import` (provider, mcp, etc.) — those aren't in this list.
        # The list above is restricted to files known to use self-export at base commit.
        expected_namespace = "Config" + name[0].upper() + name[1:]
        assert re.fullmatch(
            rf'\s*export\s*\*\s*as\s+{expected_namespace}\s+from\s+["\']\./{name}["\']\s*;?\s*',
            first_nonempty,
        ), f"{name}.ts self-export pattern was broken: {first_nonempty!r}"


def test_bun_can_resolve_formatter_module():
    """Bun can resolve and parse formatter.ts (catches syntax-level breakage).

    Uses --external='*' so transitive imports don't need to be installed; we
    just verify the file is valid TypeScript that bun can read.
    """
    r = _run(
        [
            "bun", "build",
            str(CFG / "formatter.ts"),
            "--target=node",
            "--external=*",
            "--outfile=/tmp/_formatter_build.js",
        ],
        timeout=60,
    )
    assert r.returncode == 0, f"bun build of formatter.ts failed:\n{r.stderr}"


def test_bun_can_resolve_lsp_module():
    r = _run(
        [
            "bun", "build",
            str(CFG / "lsp.ts"),
            "--target=node",
            "--external=*",
            "--outfile=/tmp/_lsp_build.js",
        ],
        timeout=60,
    )
    assert r.returncode == 0, f"bun build of lsp.ts failed:\n{r.stderr}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_typecheck_run_typecheck():
    """pass_to_pass | CI job 'typecheck' → step 'Run typecheck' (scoped to opencode package)"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/opencode typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_run_unit_tests():
    """pass_to_pass | CI job 'unit' → step 'Run unit tests' (scoped to config tests)"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/opencode test --timeout 30000 test/config/config.test.ts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
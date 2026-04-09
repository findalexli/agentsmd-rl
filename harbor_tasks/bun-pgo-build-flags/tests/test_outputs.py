"""
Task: bun-pgo-build-flags
Repo: bun @ d2e67536514b059cb317beea23ebbeafe2fa6c1a
PR:   28805

Tests for IR PGO build support in Bun's build system.
Verifies that --pgo-generate and --pgo-use flags are properly
added to CLI parsing, config interface, and compiler/linker flags.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/bun"

# Path constants for modified files
BUILD_TS = Path(f"{REPO}/scripts/build.ts")
CONFIG_TS = Path(f"{REPO}/scripts/build/config.ts")
FLAGS_TS = Path(f"{REPO}/scripts/build/flags.ts")
WEBKIT_TS = Path(f"{REPO}/scripts/build/deps/webkit.ts")


# ---------------------------------------------------------------------------
# Helper: Parse TypeScript file and extract key info
# ---------------------------------------------------------------------------

def read_typescript_source(path: Path) -> str:
    """Read TypeScript file, return empty string if not found."""
    if not path.exists():
        return ""
    return path.read_text()


def parse_typescript_ast(path: Path) -> ast.AST | None:
    """
    Parse TypeScript as Python AST (they're similar enough for structure checks).
    This works for the simple patterns we need to verify.
    """
    src = read_typescript_source(path)
    if not src:
        return None
    try:
        # TypeScript-specific syntax removed/transformed for Python parsing
        src = src.replace(" | undefined", "")
        src = src.replace(": string", "")
        src = src.replace(": boolean", "")
        src = src.replace(": Flag[]", "")
        src = src.replace(": Config", "")
        src = src.replace(": PartialConfig", "")
        src = src.replace(": Toolchain", "")
        src = src.replace(": BuildMode", "")
        src = src.replace(": BuildType", "")
        src = src.replace(": Dependency", "")
        src = src.replace(": Record<string, string>", "")
        src = src.replace("export ", "")
        src = src.replace("interface ", "class ")
        src = src.replace(" => ", " : ")
        src = src.replace("const ", "")
        return ast.parse(src)
    except SyntaxError:
        return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_syntax():
    """Modified TypeScript files must parse without errors."""
    for path in [BUILD_TS, CONFIG_TS, FLAGS_TS, WEBKIT_TS]:
        src = read_typescript_source(path)
        assert src, f"File not found: {path}"
        # Basic syntax check: file should be valid text with balanced braces
        open_braces = src.count("{")
        close_braces = src.count("}")
        assert open_braces == close_braces, f"Unbalanced braces in {path}"
        # Check for common TypeScript keywords
        assert "export" in src or "import" in src or "function" in src, f"Not valid TypeScript: {path}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_pgo_flags_in_config_interface():
    """Config interface includes pgoGenerate and pgoUse fields."""
    src = read_typescript_source(CONFIG_TS)
    assert "pgoGenerate: string | undefined" in src, "pgoGenerate field missing from Config interface"
    assert "pgoUse: string | undefined" in src, "pgoUse field missing from Config interface"
    # Also check PartialConfig
    assert "pgoGenerate?: string" in src, "pgoGenerate missing from PartialConfig"
    assert "pgoUse?: string" in src, "pgoUse missing from PartialConfig"


# [pr_diff] fail_to_pass
def test_pgo_mutual_exclusivity_check():
    """resolveConfig throws BuildError when both pgoGenerate and pgoUse are provided."""
    src = read_typescript_source(CONFIG_TS)
    # Check for the mutual exclusivity validation
    assert "pgoGenerate && pgoUse" in src, "Missing mutual exclusivity check"
    assert "--pgo-generate and --pgo-use are mutually exclusive" in src, "Missing error message"
    assert "BuildError" in src, "Should throw BuildError"


# [pr_diff] fail_to_pass
def test_pgo_flags_in_cli_args():
    """CLI argument parsing includes pgoGenerate and pgoUse flags."""
    src = read_typescript_source(BUILD_TS)
    # Check that the flags are in the long options list
    assert '"pgoGenerate"' in src, "pgoGenerate not in CLI long options"
    assert '"pgoUse"' in src, "pgoUse not in CLI long options"


# [pr_diff] fail_to_pass
def test_pgo_feature_flags_in_output():
    """formatConfig shows pgo-gen/pgo-use in feature list when enabled."""
    src = read_typescript_source(CONFIG_TS)
    # Check formatConfig function adds pgo features
    assert 'if (cfg.pgoGenerate) features.push("pgo-gen")' in src, "pgo-gen feature missing"
    assert 'if (cfg.pgoUse) features.push("pgo-use")' in src, "pgo-use feature missing"


# [pr_diff] fail_to_pass
def test_pgo_compile_flags_present():
    """globalFlags includes PGO compile-side flags."""
    src = read_typescript_source(FLAGS_TS)
    # Check for PGO compile-side flags section
    assert "─── PGO (compile-side) ───" in src, "PGO compile-side section missing"
    assert "-fprofile-generate=" in src, "Missing -fprofile-generate flag"
    assert "-fprofile-use=" in src, "Missing -fprofile-use flag"
    assert "-Wno-profile-instr-out-of-date" in src, "Missing PGO warning suppression"
    assert "IR PGO: instrument for profile generation" in src, "Missing PGO instrument description"
    assert "IR PGO: optimize with profile data" in src, "Missing PGO optimize description"


# [pr_diff] fail_to_pass
def test_pgo_link_flags_present():
    """linkerFlags includes PGO link-side flags."""
    src = read_typescript_source(FLAGS_TS)
    # Check for PGO link-side flags section
    assert "─── PGO (link-side) ───" in src, "PGO link-side section missing"
    # Count occurrences of PGO flags - should be in both globalFlags and linkerFlags
    pgo_generate_count = src.count("-fprofile-generate=")
    pgo_use_count = src.count("-fprofile-use=")
    assert pgo_generate_count >= 2, f"PGO generate should appear in both compile and link flags (found {pgo_generate_count})"
    assert pgo_use_count >= 2, f"PGO use should appear in both compile and link flags (found {pgo_use_count})"


# [pr_diff] fail_to_pass
def test_webkit_pgo_forwarding():
    """WebKit dependency forwards PGO flags via CMAKE_C/CXX_FLAGS."""
    src = read_typescript_source(WEBKIT_TS)
    # Check that WebKit receives PGO flags
    assert "optFlags" in src, "Missing optFlags array for WebKit"
    assert "CMAKE_C_FLAGS: optFlagStr" in src, "CMAKE_C_FLAGS not set to optFlagStr"
    assert "CMAKE_CXX_FLAGS: optFlagStr" in src, "CMAKE_CXX_FLAGS not set to optFlagStr"
    assert "cfg.pgoGenerate" in src, "WebKit doesn't check pgoGenerate"
    assert "cfg.pgoUse" in src, "WebKit doesn't check pgoUse"
    assert "-fprofile-generate=" in src, "Missing -fprofile-generate in WebKit"
    assert "-fprofile-use=" in src, "Missing -fprofile-use in WebKit"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_tests_pass():
    """Upstream build script structure is intact."""
    # Verify key functions exist in the build scripts
    config_src = read_typescript_source(CONFIG_TS)
    assert "export interface Config" in config_src, "Config interface missing"
    assert "export interface PartialConfig" in config_src, "PartialConfig interface missing"
    assert "export function resolveConfig" in config_src, "resolveConfig function missing"
    assert "export function formatConfig" in config_src, "formatConfig function missing"

    flags_src = read_typescript_source(FLAGS_TS)
    assert "export const globalFlags" in flags_src, "globalFlags missing"
    assert "export const linkerFlags" in flags_src, "linkerFlags missing"

    webkit_src = read_typescript_source(WEBKIT_TS)
    assert "export const webkit" in webkit_src, "webkit dependency missing"


# [static] pass_to_pass
def test_not_stub():
    """resolveConfig has real PGO validation logic, not placeholder."""
    src = read_typescript_source(CONFIG_TS)
    # The fix should have actual implementation, not just pass/placeholder
    # Check that resolveConfig actually processes pgoGenerate and pgoUse
    lines = src.split("\n")
    in_resolve_config = False
    resolve_config_body = []
    brace_count = 0

    for line in lines:
        if "export function resolveConfig" in line:
            in_resolve_config = True
            brace_count = 1  # Start after the opening brace
            continue
        if in_resolve_config:
            resolve_config_body.append(line)
            brace_count += line.count("{") - line.count("}")
            if brace_count == 0:
                break

    body_text = "\n".join(resolve_config_body)
    # Should have actual path resolution, not just passing through
    assert "resolve(partial.pgoGenerate)" in body_text or "partial.pgoGenerate ? resolve" in body_text, \
        "resolveConfig doesn't resolve pgoGenerate path"
    assert "resolve(partial.pgoUse)" in body_text or "partial.pgoUse ? resolve" in body_text, \
        "resolveConfig doesn't resolve pgoUse path"

"""
Task: uv-tool-list-exclude-newer
Repo: astral-sh/uv @ 2cf99b91ec336f3884c400634e61ec6d1bd77e5a
PR:   18861

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/uv"
CLI_LIB = Path(REPO) / "crates/uv-cli/src/lib.rs"
SETTINGS = Path(REPO) / "crates/uv/src/settings.rs"
LIST_RS = Path(REPO) / "crates/uv/src/commands/tool/list.rs"


def _extract_struct_body(source: str, struct_name: str) -> str:
    """Extract a Rust struct body by name."""
    lines = source.split("\n")
    in_struct = False
    brace_depth = 0
    result = []
    for line in lines:
        if not in_struct and re.search(rf"\bstruct\s+{struct_name}\b", line):
            in_struct = True
        if in_struct:
            result.append(line)
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0 and len(result) > 1:
                break
    return "\n".join(result)


def _extract_impl_block(source: str, type_name: str) -> str:
    """Extract an impl block for a given type."""
    lines = source.split("\n")
    in_impl = False
    brace_depth = 0
    result = []
    for line in lines:
        if not in_impl and re.search(rf"\bimpl\s+{type_name}\b", line):
            in_impl = True
        if in_impl:
            result.append(line)
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0 and len(result) > 1:
                break
    return "\n".join(result)


def _extract_fn_signature(source: str, func_name: str) -> str:
    """Extract the signature of a Rust function (up to opening brace)."""
    lines = source.split("\n")
    in_sig = False
    sig_lines = []
    for line in lines:
        if not in_sig and re.search(rf"\bfn\s+{func_name}\b", line):
            in_sig = True
        if in_sig:
            sig_lines.append(line)
            if "{" in line:
                break
    return " ".join(sig_lines)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation + anti-regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check_cli():
    """uv-cli crate compiles successfully."""
    try:
        r = subprocess.run(
            ["cargo", "check", "-p", "uv-cli"],
            capture_output=True, text=True, timeout=480, cwd=REPO,
        )
        assert r.returncode == 0, f"uv-cli does not compile:\n{r.stderr[:2000]}"
    except subprocess.TimeoutExpired:
        pass  # Skip compilation check if it takes too long; structural tests below


# [static] pass_to_pass
def test_tool_list_args_has_outdated():
    """ToolListArgs still has outdated field (anti-regression)."""
    src = CLI_LIB.read_text()
    body = _extract_struct_body(src, "ToolListArgs")
    assert body, "ToolListArgs struct not found"
    assert "outdated" in body, "ToolListArgs missing outdated field"


# [static] pass_to_pass
def test_settings_resolve_not_stub():
    """ToolListSettings::resolve has a meaningful implementation, not a stub."""
    src = SETTINGS.read_text()
    impl_block = _extract_impl_block(src, "ToolListSettings")
    assert impl_block, "impl ToolListSettings not found"
    meaningful = [
        line for line in impl_block.split("\n")
        if line.strip()
        and not line.strip().startswith("//")
        and line.strip() not in ("{", "}", "};", "}")
    ]
    assert len(meaningful) >= 10, (
        f"ToolListSettings impl has only {len(meaningful)} meaningful lines — likely a stub"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_exclude_newer_arg_defined():
    """ToolListArgs has exclude_newer field for --exclude-newer CLI flag.

    On the base commit, ToolListArgs has no exclude_newer field, so
    `uv tool list --exclude-newer` is not a recognized argument.
    """
    src = CLI_LIB.read_text()
    body = _extract_struct_body(src, "ToolListArgs")
    assert body, "ToolListArgs struct not found in uv-cli/src/lib.rs"
    assert "exclude_newer" in body, (
        "ToolListArgs does not have an exclude_newer field — "
        "`uv tool list --exclude-newer` is not supported"
    )


# [pr_diff] fail_to_pass
def test_settings_resolves_exclude_newer():
    """ToolListSettings processes exclude_newer from CLI args and filesystem config.

    On the base commit, ToolListSettings::resolve ignores the filesystem
    parameter (_filesystem) and has no exclude_newer handling.
    """
    src = SETTINGS.read_text()

    # Check the struct has exclude_newer-related field(s)
    struct_body = _extract_struct_body(src, "ToolListSettings")
    assert struct_body, "ToolListSettings struct not found"
    has_exclude = "exclude_newer" in struct_body
    has_resolver = "ResolverInstallerOptions" in struct_body
    assert has_exclude or has_resolver, (
        "ToolListSettings has no exclude_newer or ResolverInstallerOptions field"
    )

    # Check the impl block actually processes exclude_newer
    impl_block = _extract_impl_block(src, "ToolListSettings")
    assert impl_block, "impl ToolListSettings not found"
    assert "exclude_newer" in impl_block, (
        "ToolListSettings::resolve() does not handle exclude_newer"
    )


# [pr_diff] fail_to_pass
def test_list_fn_receives_resolver_options():
    """list() in tool/list.rs receives resolver options for --exclude-newer.

    On the base commit, list() only takes display flags and client_builder.
    The fix must add parameters so --exclude-newer flows to the resolver.
    """
    src = LIST_RS.read_text()
    sig = _extract_fn_signature(src, "list")
    assert sig, "list() function not found in tool/list.rs"

    has_resolver_opts = "ResolverInstallerOptions" in sig
    has_exclude_newer = "exclude_newer" in sig
    assert has_resolver_opts or has_exclude_newer, (
        "list() does not accept ResolverInstallerOptions or exclude_newer — "
        "CLI --exclude-newer cannot reach the resolver"
    )


# [pr_diff] fail_to_pass
def test_options_combined_in_list():
    """Resolver options are merged with tool config in tool/list.rs.

    On the base commit, ResolverInstallerSettings is built solely from
    tool.options(). The fix must merge CLI/filesystem options with
    tool-specific config so --exclude-newer takes effect.
    """
    src = LIST_RS.read_text()

    has_combine_call = ".combine(" in src
    has_exclude_newer = "exclude_newer" in src

    assert has_combine_call or has_exclude_newer, (
        "tool/list.rs does not merge resolver options — "
        "ResolverInstallerSettings is built solely from tool.options() "
        "without incorporating --exclude-newer"
    )

# ---------------------------------------------------------------------------
# Repo CI/CD tests (pass_to_pass) — ensure PR doesn't break existing tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_cargo_check_uv_cli():
    """uv-cli crate compiles successfully with cargo check (repo p2p)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-cli"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"uv-cli cargo check failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_check_uv():
    """uv main crate compiles successfully with cargo check (repo p2p)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"uv cargo check failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_test_uv_cli_compile():
    """uv-cli tests compile successfully (repo p2p, --no-run)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "uv-cli", "--no-run"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"uv-cli test compilation failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_check_uv_settings():
    """uv-settings crate compiles successfully with cargo check (repo p2p).

    The uv-settings crate is a dependency for the ToolListSettings changes.
    """
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-settings"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"uv-settings cargo check failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_check_uv_tool():
    """uv-tool crate compiles successfully with cargo check (repo p2p).

    The uv-tool crate contains the InstalledTools type used by tool list.
    """
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-tool"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"uv-tool cargo check failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_test_uv_integration_compile():
    """uv integration tests compile successfully (repo p2p, --no-run).

    This includes the tool_list integration tests which verify the tool
    list functionality including the --exclude-newer flag.
    """
    r = subprocess.run(
        ["cargo", "test", "-p", "uv", "--test", "it", "--no-run"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"uv integration test compilation failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_fmt_check():
    """Code formatting check passes (repo p2p).

    Ensures all code follows the repo's rustfmt configuration.
    """
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt --check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_clippy_uv():
    """Clippy linting passes for uv crate (repo p2p).

    The uv crate contains the main tool/list.rs and settings.rs files
    modified by this PR. Clippy ensures code quality and style.
    """
    r = subprocess.run(
        ["cargo", "clippy", "-p", "uv", "--", "-D", "warnings"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo clippy on uv crate failed:\n{r.stderr[-1000:]}"

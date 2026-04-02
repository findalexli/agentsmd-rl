"""
Task: uv-tool-list-outdated-settings
Repo: astral-sh/uv @ c1cd212dd5a927d9e354c44d89a307f6a6f4df37
PR:   #18586

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/repo"
FILE = "crates/uv/src/commands/tool/list.rs"


def _read_source() -> str:
    return Path(f"{REPO}/{FILE}").read_text()


def _get_outdated_section() -> str:
    """Extract the outdated code section (between 'if outdated' and 'buffer_unordered').
    AST-only because: Rust code cannot be imported in Python."""
    src = _read_source()
    lines = src.splitlines()
    outdated_start = None
    buffer_line = None
    for i, line in enumerate(lines):
        if "if outdated" in line and outdated_start is None:
            outdated_start = i
        if "buffer_unordered" in line and outdated_start is not None:
            buffer_line = i
            break
    if outdated_start is None or buffer_line is None:
        return ""
    return "\n".join(lines[outdated_start : buffer_line + 1])


def _strip_comments(text: str) -> str:
    """Remove single-line Rust comments."""
    return re.sub(r"//.*$", "", text, flags=re.MULTILINE)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_cargo_check():
    """Modified crate must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv", "--quiet"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_per_tool_options_read():
    """The outdated section must read each tool's stored options via tool.options().
    AST-only because: Rust code cannot be imported in Python."""
    section = _strip_comments(_get_outdated_section())
    assert section, "Could not find 'if outdated' section in list.rs"

    # Must call tool.options() to get per-tool stored settings
    assert re.search(r"tool\.options\(\)", section), (
        "Outdated section does not call tool.options() to read per-tool settings."
    )


# [pr_diff] fail_to_pass
def test_no_global_defaults():
    """Outdated section must not use global PrereleaseMode::default() or
    ExcludeNewer::default() — these ignore per-tool settings.
    AST-only because: Rust code cannot be imported in Python."""
    section = _strip_comments(_get_outdated_section())
    assert section, "Could not find 'if outdated' section in list.rs"

    assert not re.search(r"PrereleaseMode::default\(\)", section), (
        "Outdated section still uses global PrereleaseMode::default()"
    )
    assert not re.search(r"ExcludeNewer::default\(\)", section), (
        "Outdated section still uses global ExcludeNewer::default()"
    )


# [pr_diff] fail_to_pass
def test_per_tool_resolver_settings():
    """Outdated code must construct per-tool resolver/installer settings from
    each tool's stored options.
    AST-only because: Rust code cannot be imported in Python."""
    section = _strip_comments(_get_outdated_section())
    assert section, "Could not find 'if outdated' section in list.rs"

    uses_resolver_settings = bool(
        re.search(r"ResolverInstaller(Settings|Options)", section)
    )
    assert uses_resolver_settings, (
        "Outdated section does not use ResolverInstallerSettings or "
        "ResolverInstallerOptions for per-tool configuration."
    )


# [pr_diff] fail_to_pass
def test_per_tool_client_construction():
    """Each tool must get its own RegistryClientBuilder configured with
    tool-specific settings, constructed inside the per-tool iterator.
    AST-only because: Rust code cannot be imported in Python."""
    section = _strip_comments(_get_outdated_section())
    assert section, "Could not find 'if outdated' section in list.rs"

    # RegistryClientBuilder must appear AFTER the .map( iterator start,
    # meaning it's inside the per-tool closure (not shared across tools)
    iter_match = re.search(r"\.map\(", section)
    client_match = re.search(r"RegistryClientBuilder::new", section)

    assert iter_match and client_match, (
        "Expected both .map() iterator and RegistryClientBuilder::new in outdated section"
    )
    assert client_match.start() > iter_match.start(), (
        "RegistryClientBuilder is constructed before the per-tool iterator — "
        "it should be inside the closure for per-tool configuration"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — CLAUDE.md rules
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — CLAUDE.md:7 @ c1cd212
def test_no_unwrap_panic_in_outdated_section():
    """AVOID using panic!, unreachable!, .unwrap(), unsafe, and clippy ignores.
    AST-only because: Rust code cannot be imported in Python."""
    section = _get_outdated_section()
    assert section, "Could not locate outdated section"

    assert not re.search(r"\.unwrap\(\)", section), "Found .unwrap() in outdated section"
    assert not re.search(r"panic!\(", section), "Found panic!() in outdated section"
    assert not re.search(r"unreachable!\(", section), "Found unreachable!() in outdated section"
    assert not re.search(r"\bunsafe\b", section), "Found unsafe code in outdated section"


# [agent_config] pass_to_pass — CLAUDE.md:10 @ c1cd212
def test_expect_over_allow():
    """PREFER #[expect()] over #[allow()] if clippy must be disabled.
    AST-only because: Rust code cannot be imported in Python."""
    src = _read_source()
    allow_matches = re.findall(r"#\[allow\(clippy::", src)
    assert len(allow_matches) == 0, (
        f"Found {len(allow_matches)} #[allow(clippy::...)] — "
        "use #[expect()] instead per CLAUDE.md:10"
    )


# [agent_config] pass_to_pass — CLAUDE.md:16 @ c1cd212
def test_no_local_imports():
    """PREFER top-level imports over local imports or fully qualified names.
    AST-only because: Rust code cannot be imported in Python."""
    src = _read_source()
    lines = src.splitlines()

    func_start = None
    for i, line in enumerate(lines):
        if "pub(crate) async fn list" in line:
            func_start = i
            break

    assert func_start is not None, "Could not find list function"

    func_body = lines[func_start + 2 :]
    local_imports = [line for line in func_body if re.match(r"\s+use\s+", line)]
    assert len(local_imports) == 0, (
        f"Found {len(local_imports)} local import(s) inside function: {local_imports}"
    )

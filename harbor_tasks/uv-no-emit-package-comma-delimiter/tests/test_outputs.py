"""
Task: uv-no-emit-package-comma-delimiter
Repo: astral-sh/uv @ 5e25583c42b01fe8b1fae3b8ef05057cfdb4090c
PR:   #18565

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/repo"
CLI_FILE = f"{REPO}/crates/uv-cli/src/lib.rs"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_arg_block_for_field(content: str, struct_name: str, field_name: str) -> str:
    """Extract the #[arg(...)] block + field line for a specific field in a struct.

    Returns the ~20 lines preceding the field declaration within the struct,
    which contains the #[arg(...)] attribute.
    """
    lines = content.splitlines()

    # Find the struct definition
    struct_idx = None
    for i, line in enumerate(lines):
        if re.search(rf"\bstruct\s+{struct_name}\b", line):
            struct_idx = i
            break
    assert struct_idx is not None, f"Struct '{struct_name}' not found in lib.rs"

    # Find the field within the struct (search forward)
    field_idx = None
    brace_depth = 0
    for i in range(struct_idx, min(struct_idx + 500, len(lines))):
        brace_depth += lines[i].count("{") - lines[i].count("}")
        if re.search(rf"\b{field_name}\s*:", lines[i]):
            field_idx = i
            break
        if brace_depth < 0:
            break
    assert field_idx is not None, (
        f"Field '{field_name}' not found in struct '{struct_name}'"
    )

    start = max(struct_idx, field_idx - 20)
    return "\n".join(lines[start : field_idx + 1])


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """uv-cli crate must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-cli"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — value_delimiter on three arg fields
# Source inspection because: full Rust compilation too slow in E2B sandbox
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_export_no_emit_package_comma_delimiter():
    """ExportArgs no_emit_package accepts comma-separated values via value_delimiter."""
    content = Path(CLI_FILE).read_text()
    block = _get_arg_block_for_field(content, "ExportArgs", "no_emit_package")
    assert re.search(r"value_delimiter\s*=\s*','", block), (
        f"ExportArgs::no_emit_package missing value_delimiter = ',' in #[arg(...)]\n"
        f"Arg block:\n{block}"
    )


# [pr_diff] fail_to_pass
def test_export_only_emit_package_comma_delimiter():
    """ExportArgs only_emit_package accepts comma-separated values via value_delimiter."""
    content = Path(CLI_FILE).read_text()
    block = _get_arg_block_for_field(content, "ExportArgs", "only_emit_package")
    assert re.search(r"value_delimiter\s*=\s*','", block), (
        f"ExportArgs::only_emit_package missing value_delimiter = ',' in #[arg(...)]\n"
        f"Arg block:\n{block}"
    )


# [pr_diff] fail_to_pass
def test_pipcompile_no_emit_package_comma_delimiter():
    """PipCompileArgs no_emit_package accepts comma-separated values via value_delimiter."""
    content = Path(CLI_FILE).read_text()
    block = _get_arg_block_for_field(content, "PipCompileArgs", "no_emit_package")
    assert re.search(r"value_delimiter\s*=\s*','", block), (
        f"PipCompileArgs::no_emit_package missing value_delimiter = ',' in #[arg(...)]\n"
        f"Arg block:\n{block}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_existing_aliases_preserved():
    """Existing aliases (no-install-package, only-install-package, unsafe-package) still present."""
    content = Path(CLI_FILE).read_text()
    assert "no-install-package" in content, "no-install-package alias missing from ExportArgs"
    assert "only-install-package" in content, "only-install-package alias missing from ExportArgs"
    assert "unsafe-package" in content, "unsafe-package alias missing from PipCompileArgs"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:7 @ 5e25583c42b01fe8b1fae3b8ef05057cfdb4090c
def test_no_prohibited_patterns_in_changes():
    """No .unwrap(), panic!, unreachable!, or unsafe introduced in modified code."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--", CLI_FILE],
        cwd=REPO, capture_output=True, timeout=30,
    )
    diff = r.stdout.decode()
    added_lines = [l for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]

    prohibited = [".unwrap()", "panic!", "unreachable!", "unsafe "]
    for pattern in prohibited:
        hits = [l for l in added_lines if pattern in l]
        assert len(hits) == 0, (
            f"Found prohibited pattern '{pattern}' in added lines:\n" +
            "\n".join(hits)
        )


# [agent_config] pass_to_pass — CLAUDE.md:10 @ 5e25583c42b01fe8b1fae3b8ef05057cfdb4090c
def test_no_allow_attribute_in_changes():
    """Uses #[expect()] instead of #[allow()] for clippy suppressions."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--", CLI_FILE],
        cwd=REPO, capture_output=True, timeout=30,
    )
    diff = r.stdout.decode()
    added_lines = [l for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
    allow_hits = [l for l in added_lines if "#[allow(" in l]
    assert len(allow_hits) == 0, (
        f"Found #[allow()] in added lines (use #[expect()] instead):\n" +
        "\n".join(allow_hits)
    )

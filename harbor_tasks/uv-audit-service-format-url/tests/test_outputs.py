"""
Task: uv-audit-service-format-url
Repo: astral-sh/uv @ 685a79876028a83976acafffd94e8abe3295d72a
PR:   18571

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = Path("/repo")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def strip_rust_comments(code: str) -> str:
    """Remove // and /* */ comments from Rust source."""
    code = re.sub(r"//[^\n]*", "", code)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    return code


def read_stripped(path: Path) -> str:
    return strip_rust_comments(path.read_text())


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — compilation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compilation():
    """All three affected crates (uv-audit, uv-cli, uv) must compile."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-audit", "-p", "uv-cli", "-p", "uv"],
        cwd=REPO, capture_output=True, timeout=480,
    )
    assert r.returncode == 0, (
        f"Compilation failed:\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_enum_copy_clone_debug():
    """VulnerabilityServiceFormat::Osv exists with Copy, Clone, Debug derives."""
    # Compilation gate proves the code works; here we verify the enum shape.
    code = read_stripped(REPO / "crates/uv-audit/src/service/mod.rs")

    assert "enum VulnerabilityServiceFormat" in code, (
        "service/mod.rs must define VulnerabilityServiceFormat enum"
    )

    # Must have Osv variant
    assert re.search(
        r"enum\s+VulnerabilityServiceFormat\s*\{[^}]*\bOsv\b", code, re.DOTALL
    ), "VulnerabilityServiceFormat must have an Osv variant"

    # Collect all derive() attributes in the ~300 chars before the enum keyword
    enum_pos = code.find("enum VulnerabilityServiceFormat")
    derive_region = code[max(0, enum_pos - 300):enum_pos]
    derives = " ".join(re.findall(r"derive\(([^)]+)\)", derive_region))
    for trait_name in ("Copy", "Clone", "Debug"):
        assert trait_name in derives, (
            f"VulnerabilityServiceFormat must derive {trait_name}. "
            f"Found derives: {derives}"
        )


# [pr_diff] fail_to_pass
def test_cli_fields_typed():
    """AuditArgs has service_format (VulnerabilityServiceFormat) and service_url (Option<String>)."""
    code = read_stripped(REPO / "crates/uv-cli/src/lib.rs")

    # Locate AuditArgs struct body
    m = re.search(r"pub\s+struct\s+AuditArgs\s*\{", code)
    assert m, "AuditArgs struct not found in uv-cli/src/lib.rs"
    # Grab text from struct opening to the next top-level closing brace
    body = code[m.end():]

    # service_format field with correct type
    assert re.search(r"service_format\s*:\s*VulnerabilityServiceFormat\b", body), (
        "AuditArgs must have field `service_format: VulnerabilityServiceFormat`"
    )
    # service_url field with correct type
    assert re.search(r"service_url\s*:\s*Option\s*<\s*String\s*>", body), (
        "AuditArgs must have field `service_url: Option<String>`"
    )


# [pr_diff] fail_to_pass
def test_audit_fn_accepts_service_params():
    """audit() uses VulnerabilityServiceFormat, service_url, and API_BASE fallback."""
    code = read_stripped(REPO / "crates/uv/src/commands/project/audit.rs")

    fn_match = re.search(r"async\s+fn\s+audit\s*\(", code)
    assert fn_match, "audit() function not found in audit.rs"
    fn_region = code[fn_match.start():]

    assert "VulnerabilityServiceFormat" in fn_region, (
        "VulnerabilityServiceFormat must be used within the audit function"
    )
    assert "service_url" in fn_region, (
        "service_url must be used within the audit function"
    )
    # The default URL fallback must reference the existing API_BASE constant
    assert "API_BASE" in fn_region, (
        "audit.rs must use API_BASE as the default URL fallback"
    )


# [pr_diff] fail_to_pass
def test_settings_wires_service_fields():
    """AuditSettings includes and wires service_format and service_url."""
    code = read_stripped(REPO / "crates/uv/src/settings.rs")

    # Verify fields exist in the struct
    m = re.search(r"struct\s+AuditSettings\s*\{", code)
    assert m, "AuditSettings struct not found in settings.rs"
    struct_body = code[m.end():]

    assert "service_format" in struct_body[:2000], (
        "AuditSettings must have a service_format field"
    )
    assert "VulnerabilityServiceFormat" in struct_body[:2000], (
        "service_format must be of type VulnerabilityServiceFormat"
    )
    assert "service_url" in struct_body[:2000], (
        "AuditSettings must have a service_url field"
    )

    # Verify VulnerabilityServiceFormat is imported at module level
    assert "VulnerabilityServiceFormat" in code, (
        "settings.rs must reference VulnerabilityServiceFormat"
    )


# [pr_diff] fail_to_pass
def test_clap_optional_dependency():
    """uv-audit Cargo.toml has clap listed as an optional dependency."""
    cargo_toml = (REPO / "crates/uv-audit/Cargo.toml").read_text()
    lines = [l for l in cargo_toml.splitlines() if not l.strip().startswith("#")]
    text = "\n".join(lines)

    assert "clap" in text, "uv-audit Cargo.toml must list clap as a dependency"
    # Find the clap line and check it includes 'optional'
    clap_idx = text.index("clap")
    clap_line = text[clap_idx:].split("\n")[0]
    assert "optional" in clap_line, (
        "clap dependency in uv-audit must be marked as optional"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:7 @ 685a79876028a83976acafffd94e8abe3295d72a
def test_no_unwrap_in_audit():
    """No bare .unwrap() calls in audit.rs (CLAUDE.md: AVOID .unwrap())."""
    code = read_stripped(REPO / "crates/uv/src/commands/project/audit.rs")
    # Match .unwrap() but not .unwrap_or(), .unwrap_or_else(), .unwrap_or_default()
    matches = re.findall(r"\.unwrap\(\)", code)
    assert len(matches) == 0, (
        f"Found {len(matches)} bare .unwrap() call(s) in audit.rs. "
        "Use .expect() with a message, or handle the error with ? or if let."
    )


# [agent_config] fail_to_pass — CLAUDE.md:16 @ 685a79876028a83976acafffd94e8abe3295d72a
def test_top_level_imports():
    """VulnerabilityServiceFormat imported at top of files that use it."""
    # CLAUDE.md line 16: "PREFER top-level imports over local imports"
    files_to_check = [
        (REPO / "crates/uv/src/commands/project/audit.rs", 40),
        (REPO / "crates/uv/src/settings.rs", 20),
    ]
    for path, max_line in files_to_check:
        top_lines = path.read_text().splitlines()[:max_line]
        found = any(
            "VulnerabilityServiceFormat" in re.sub(r"//.*", "", line)
            and "use " in line
            for line in top_lines
        )
        assert found, (
            f"VulnerabilityServiceFormat not imported in top {max_line} lines "
            f"of {path.name}. CLAUDE.md requires top-level imports."
        )


# [agent_config] pass_to_pass — CLAUDE.md:7 @ 685a79876028a83976acafffd94e8abe3295d72a
def test_no_panic_in_new_code():
    """No panic! or unreachable! macros in service/mod.rs."""
    code = read_stripped(REPO / "crates/uv-audit/src/service/mod.rs")
    assert "panic!" not in code, "service/mod.rs must not contain panic!"
    assert "unreachable!" not in code, "service/mod.rs must not contain unreachable!"
    assert "unsafe " not in code, "service/mod.rs must not contain unsafe code"

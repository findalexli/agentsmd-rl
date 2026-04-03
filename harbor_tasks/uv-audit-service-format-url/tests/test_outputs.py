"""
Task: uv-audit-service-format-url
Repo: astral-sh/uv @ 685a79876028a83976acafffd94e8abe3295d72a
PR:   18571

Add configurable vulnerability service backend (--service-format, --service-url)
to `uv audit`.  All checks are structural (file inspection) because uv is a
200+ crate Rust workspace whose `cargo check` exceeds test-timeout budgets.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
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
# Fail-to-pass (pr_diff) — core structural tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_enum_copy_clone_debug():
    """VulnerabilityServiceFormat::Osv exists with Copy, Clone, Debug derives."""
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
def test_enum_clap_valueenum():
    """VulnerabilityServiceFormat has cfg_attr for clap::ValueEnum."""
    code = read_stripped(REPO / "crates/uv-audit/src/service/mod.rs")

    # The enum must be usable as a clap ValueEnum behind a feature gate
    enum_pos = code.find("enum VulnerabilityServiceFormat")
    assert enum_pos != -1, "VulnerabilityServiceFormat enum not found"

    attr_region = code[max(0, enum_pos - 400):enum_pos]
    assert re.search(r"cfg_attr.*clap.*ValueEnum", attr_region), (
        "VulnerabilityServiceFormat must have a cfg_attr for clap::ValueEnum "
        "(e.g. #[cfg_attr(feature = \"clap\", derive(clap::ValueEnum))])"
    )


# [pr_diff] fail_to_pass
def test_cli_fields_typed():
    """AuditArgs has service_format (VulnerabilityServiceFormat) and service_url (Option<String>)."""
    code = read_stripped(REPO / "crates/uv-cli/src/lib.rs")

    # Locate AuditArgs struct body
    m = re.search(r"pub\s+struct\s+AuditArgs\s*\{", code)
    assert m, "AuditArgs struct not found in uv-cli/src/lib.rs"
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
def test_cli_arg_attributes():
    """service_format has value_enum + default_value, service_url has ValueHint::Url."""
    raw = (REPO / "crates/uv-cli/src/lib.rs").read_text()

    # Locate AuditArgs
    m = re.search(r"pub\s+struct\s+AuditArgs\s*\{", raw)
    assert m, "AuditArgs not found"
    body = raw[m.end():]

    # service_format should be annotated as a value_enum with default "osv"
    sf_match = re.search(r"service_format\s*:", body)
    assert sf_match, "service_format field not found"
    sf_region = body[:sf_match.start()]  # attrs are above the field
    # Look in the last 500 chars before the field for arg attributes
    sf_attrs = sf_region[-500:]
    assert "value_enum" in sf_attrs, (
        "service_format #[arg] must include value_enum"
    )
    assert re.search(r'default_value\s*=\s*"osv"', sf_attrs), (
        'service_format #[arg] must have default_value = "osv"'
    )

    # service_url should use ValueHint::Url
    su_match = re.search(r"service_url\s*:", body)
    assert su_match, "service_url field not found"
    su_attrs = body[:su_match.start()][-500:]
    assert "ValueHint::Url" in su_attrs or "value_hint = ValueHint::Url" in su_attrs, (
        "service_url #[arg] must use ValueHint::Url"
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


# [pr_diff] fail_to_pass
def test_uv_cli_depends_on_uv_audit():
    """uv-cli Cargo.toml depends on uv-audit with clap feature enabled."""
    cargo_toml = (REPO / "crates/uv-cli/Cargo.toml").read_text()
    lines = [l for l in cargo_toml.splitlines() if not l.strip().startswith("#")]
    text = "\n".join(lines)

    assert "uv-audit" in text, (
        "uv-cli Cargo.toml must list uv-audit as a dependency"
    )
    # Find the uv-audit line and verify clap feature is enabled
    idx = text.index("uv-audit")
    uv_audit_line = text[idx:].split("\n")[0]
    assert "clap" in uv_audit_line, (
        'uv-cli must depend on uv-audit with features = ["clap"]'
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

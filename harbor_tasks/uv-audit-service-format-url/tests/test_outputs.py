"""
Task: uv-audit-service-format-url
Repo: astral-sh/uv @ 685a79876028a83976acafffd94e8abe3295d72a
PR:   18571

Add configurable vulnerability service backend (--service-format, --service-url)
to `uv audit`.  All checks are structural (file inspection) because uv is a
200+ crate Rust workspace whose full `cargo check` exceeds test-timeout budgets.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = Path("/repo")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core structural tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_enum_exists_with_derives():
    """VulnerabilityServiceFormat enum exists with Copy, Clone, Debug derives."""
    code = (REPO / "crates/uv-audit/src/service/mod.rs").read_text()

    assert "enum VulnerabilityServiceFormat" in code, (
        "service/mod.rs must define VulnerabilityServiceFormat enum"
    )

    # Must have Osv variant
    assert re.search(
        r"enum\s+VulnerabilityServiceFormat\s*\{[^}]*\bOsv\b", code, re.DOTALL
    ), "VulnerabilityServiceFormat must have an Osv variant"

    # Collect derive attributes in the region before the enum keyword
    enum_pos = code.find("enum VulnerabilityServiceFormat")
    derive_region = code[max(0, enum_pos - 400):enum_pos]
    derives = " ".join(re.findall(r"derive\(([^)]+)\)", derive_region))
    for trait_name in ("Copy", "Clone", "Debug"):
        assert trait_name in derives, (
            f"VulnerabilityServiceFormat must derive {trait_name}. "
            f"Found derives: {derives}"
        )


# [pr_diff] fail_to_pass
def test_enum_clap_valueenum():
    """VulnerabilityServiceFormat has cfg_attr for clap::ValueEnum."""
    code = (REPO / "crates/uv-audit/src/service/mod.rs").read_text()

    enum_pos = code.find("enum VulnerabilityServiceFormat")
    assert enum_pos != -1, "VulnerabilityServiceFormat enum not found"

    attr_region = code[max(0, enum_pos - 400):enum_pos]
    # Accept both cfg_attr(feature="clap", derive(clap::ValueEnum)) and
    # a plain derive(clap::ValueEnum) — either makes it a ValueEnum
    has_cfg_attr = re.search(r"cfg_attr.*clap.*ValueEnum", attr_region)
    has_plain_derive = re.search(r"derive\([^)]*clap::ValueEnum", attr_region)
    assert has_cfg_attr or has_plain_derive, (
        "VulnerabilityServiceFormat must be usable as a clap ValueEnum "
        "(e.g. #[cfg_attr(feature = \"clap\", derive(clap::ValueEnum))])"
    )


# [pr_diff] fail_to_pass
def test_cli_service_format_field():
    """AuditArgs has service_format field typed as VulnerabilityServiceFormat."""
    code = (REPO / "crates/uv-cli/src/lib.rs").read_text()

    m = re.search(r"pub\s+struct\s+AuditArgs\s*\{", code)
    assert m, "AuditArgs struct not found in uv-cli/src/lib.rs"
    body = code[m.end():]

    assert re.search(r"service_format\s*:\s*VulnerabilityServiceFormat\b", body), (
        "AuditArgs must have field `service_format: VulnerabilityServiceFormat`"
    )


# [pr_diff] fail_to_pass
def test_cli_service_url_field():
    """AuditArgs has service_url field typed as Option<String>."""
    code = (REPO / "crates/uv-cli/src/lib.rs").read_text()

    m = re.search(r"pub\s+struct\s+AuditArgs\s*\{", code)
    assert m, "AuditArgs struct not found in uv-cli/src/lib.rs"
    body = code[m.end():]

    assert re.search(r"service_url\s*:\s*Option\s*<\s*String\s*>", body), (
        "AuditArgs must have field `service_url: Option<String>`"
    )


# [pr_diff] fail_to_pass
def test_cli_arg_attributes():
    """service_format has value_enum + default_value osv, service_url has ValueHint::Url."""
    raw = (REPO / "crates/uv-cli/src/lib.rs").read_text()

    m = re.search(r"pub\s+struct\s+AuditArgs\s*\{", raw)
    assert m, "AuditArgs not found"
    body = raw[m.end():]

    # service_format should be annotated as a value_enum with default "osv"
    sf_match = re.search(r"service_format\s*:", body)
    assert sf_match, "service_format field not found"
    sf_attrs = body[:sf_match.start()][-600:]
    assert "value_enum" in sf_attrs, (
        "service_format #[arg] must include value_enum"
    )
    assert re.search(r'default_value\s*=\s*"osv"', sf_attrs), (
        'service_format #[arg] must have default_value = "osv"'
    )

    # service_url should use ValueHint::Url
    su_match = re.search(r"pub\s+service_url\s*:", body)
    assert su_match, "service_url field not found"
    su_attrs = body[:su_match.start()][-600:]
    assert re.search(r"ValueHint\s*::\s*Url", su_attrs), (
        "service_url #[arg] must use ValueHint::Url"
    )


# [pr_diff] fail_to_pass
def test_audit_fn_accepts_service_params():
    """audit() uses VulnerabilityServiceFormat, service_url, and API_BASE fallback."""
    code = (REPO / "crates/uv/src/commands/project/audit.rs").read_text()

    fn_match = re.search(r"(pub\s*(\(crate\)\s*)?)?async\s+fn\s+audit\s*\(", code)
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
    code = (REPO / "crates/uv/src/settings.rs").read_text()

    m = re.search(r"struct\s+AuditSettings\s*\{", code)
    assert m, "AuditSettings struct not found in settings.rs"
    # Look at the struct body (next ~2000 chars)
    struct_body = code[m.end():m.end() + 2000]

    assert "service_format" in struct_body, (
        "AuditSettings must have a service_format field"
    )
    assert "VulnerabilityServiceFormat" in struct_body, (
        "service_format must be of type VulnerabilityServiceFormat"
    )
    assert "service_url" in struct_body, (
        "AuditSettings must have a service_url field"
    )


# [pr_diff] fail_to_pass
def test_clap_optional_dependency():
    """uv-audit Cargo.toml has clap listed as an optional dependency."""
    cargo_toml = (REPO / "crates/uv-audit/Cargo.toml").read_text()
    # Remove comment lines
    lines = [l for l in cargo_toml.splitlines() if not l.strip().startswith("#")]
    text = "\n".join(lines)

    assert "clap" in text, "uv-audit Cargo.toml must list clap as a dependency"
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
    idx = text.index("uv-audit")
    uv_audit_line = text[idx:].split("\n")[0]
    assert "clap" in uv_audit_line, (
        'uv-cli must depend on uv-audit with features = ["clap"]'
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:7 @ 685a79876028a83976acafffd94e8abe3295d72a
def test_no_unwrap_in_new_service_code():
    """No bare .unwrap() in the new service-handling code in audit.rs."""
    code = (REPO / "crates/uv/src/commands/project/audit.rs").read_text()
    # Only check the region the agent adds: from VulnerabilityServiceFormat usage
    # to the end of the match/block. Existing code already has .unwrap() elsewhere.
    vsf_pos = code.find("VulnerabilityServiceFormat")
    if vsf_pos == -1:
        # If enum isn't used in audit.rs yet, nothing to check (vacuous pass)
        return
    # Check the last 800 chars of the file starting from VulnerabilityServiceFormat
    new_region = code[vsf_pos:vsf_pos + 800]
    new_region = re.sub(r"//[^\n]*", "", new_region)
    matches = re.findall(r"\.unwrap\(\)", new_region)
    assert len(matches) == 0, (
        f"Found {len(matches)} bare .unwrap() call(s) in new service code. "
        "Use .expect() with a message, .unwrap_or(), or handle with ? or if let."
    )


# [agent_config] fail_to_pass — CLAUDE.md:16 @ 685a79876028a83976acafffd94e8abe3295d72a
def test_top_level_imports():
    """VulnerabilityServiceFormat imported at top of files that use it."""
    # CLAUDE.md line 16: "PREFER top-level imports over local imports"
    files_to_check = [
        (REPO / "crates/uv/src/commands/project/audit.rs", 50),
        (REPO / "crates/uv/src/settings.rs", 30),
    ]
    for path, max_line in files_to_check:
        lines = path.read_text().splitlines()[:max_line]
        found = any(
            "VulnerabilityServiceFormat" in line and "use " in line
            for line in lines
        )
        assert found, (
            f"VulnerabilityServiceFormat not imported in top {max_line} lines "
            f"of {path.name}. CLAUDE.md requires top-level imports."
        )


# [agent_config] pass_to_pass — CLAUDE.md:7 @ 685a79876028a83976acafffd94e8abe3295d72a
def test_no_panic_in_new_code():
    """No panic! or unreachable! macros in service/mod.rs."""
    code = (REPO / "crates/uv-audit/src/service/mod.rs").read_text()
    # Strip comments to avoid false positives
    code_no_comments = re.sub(r"//[^\n]*", "", code)
    code_no_comments = re.sub(r"/\*.*?\*/", "", code_no_comments, flags=re.DOTALL)
    assert "panic!" not in code_no_comments, "service/mod.rs must not contain panic!"
    assert "unreachable!" not in code_no_comments, "service/mod.rs must not contain unreachable!"
    assert "unsafe " not in code_no_comments, "service/mod.rs must not contain unsafe code"

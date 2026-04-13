"""
Task: uv-audit-service-format-url
Repo: astral-sh/uv @ 685a79876028a83976acafffd94e8abe3295d72a
PR:   18571

Add configurable vulnerability service backend (--service-format, --service-url)
to `uv audit`.  Tests include behavioral (cargo compilation) and structural
(file inspection) checks.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = Path("/repo")


# ---------------------------------------------------------------------------
# Behavioral fail-to-pass (pr_diff) — subprocess execution
# ---------------------------------------------------------------------------


def test_uv_audit_clap_feature_compiles():
    """uv-audit compiles with the clap feature enabled (validates optional dep + ValueEnum derive)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-audit", "--features", "clap"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=str(REPO),
    )
    assert r.returncode == 0, (
        f"cargo check -p uv-audit --features clap failed:\n{r.stderr}"
    )


def test_vulnerability_service_format_is_public():
    """VulnerabilityServiceFormat is public with Osv variant and Copy+Clone+Debug derives."""
    test_dir = REPO / "crates/uv-audit/tests"
    test_dir.mkdir(parents=True, exist_ok=True)
    test_file = test_dir / "behavioral_check.rs"

    test_file.write_text(
        """
use uv_audit::service::VulnerabilityServiceFormat;

#[test]
fn check_enum() {
    let fmt = VulnerabilityServiceFormat::Osv;
    // Copy: can use after assignment
    let _copy = fmt;
    let _still_valid = fmt; // Copy means fmt is still usable
    // Debug: can format
    let _s = format!("{:?}", fmt);
}
"""
    )
    try:
        r = subprocess.run(
            [
                "cargo",
                "test",
                "-p",
                "uv-audit",
                "--test",
                "behavioral_check",
                "--",
                "--nocapture",
            ],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=str(REPO),
        )
        assert r.returncode == 0, (
            f"Behavioral test failed (compilation or runtime):\n{r.stderr}\n{r.stdout}"
        )
    finally:
        test_file.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Structural fail-to-pass (pr_diff) — file inspection
# ---------------------------------------------------------------------------


def test_cli_service_format_field():
    """AuditArgs has service_format field typed as VulnerabilityServiceFormat."""
    code = (REPO / "crates/uv-cli/src/lib.rs").read_text()

    m = re.search(r"pub\s+struct\s+AuditArgs\s*\{", code)
    assert m, "AuditArgs struct not found in uv-cli/src/lib.rs"
    body = code[m.end() :]

    assert re.search(
        r"service_format\s*:\s*VulnerabilityServiceFormat\b", body
    ), "AuditArgs must have field `service_format: VulnerabilityServiceFormat`"


def test_cli_service_url_field():
    """AuditArgs has service_url field typed as Option<String>."""
    code = (REPO / "crates/uv-cli/src/lib.rs").read_text()

    m = re.search(r"pub\s+struct\s+AuditArgs\s*\{", code)
    assert m, "AuditArgs struct not found in uv-cli/src/lib.rs"
    body = code[m.end() :]

    assert re.search(r"service_url\s*:\s*Option\s*<\s*String\s*>", body), (
        "AuditArgs must have field `service_url: Option<String>`"
    )


def test_cli_arg_attributes():
    """service_format has value_enum + default_value osv; service_url has ValueHint::Url."""
    raw = (REPO / "crates/uv-cli/src/lib.rs").read_text()

    m = re.search(r"pub\s+struct\s+AuditArgs\s*\{", raw)
    assert m, "AuditArgs not found"
    body = raw[m.end() :]

    # service_format should be annotated as a value_enum with default "osv"
    sf_match = re.search(r"service_format\s*:", body)
    assert sf_match, "service_format field not found"
    sf_attrs = body[: sf_match.start()][-600:]
    assert "value_enum" in sf_attrs, "service_format #[arg] must include value_enum"
    assert re.search(r'default_value\s*=\s*"osv"', sf_attrs), (
        'service_format #[arg] must have default_value = "osv"'
    )

    # service_url should use ValueHint::Url
    su_match = re.search(r"pub\s+service_url\s*:", body)
    assert su_match, "service_url field not found"
    su_attrs = body[: su_match.start()][-600:]
    assert re.search(r"ValueHint\s*::\s*Url", su_attrs), (
        "service_url #[arg] must use ValueHint::Url"
    )


def test_audit_fn_accepts_service_params():
    """audit() uses VulnerabilityServiceFormat, service_url, and API_BASE fallback."""
    code = (REPO / "crates/uv/src/commands/project/audit.rs").read_text()

    fn_match = re.search(
        r"(pub\s*(\(crate\)\s*)?)?async\s+fn\s+audit\s*\(", code
    )
    assert fn_match, "audit() function not found in audit.rs"
    fn_region = code[fn_match.start() :]

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


def test_settings_wires_service_fields():
    """AuditSettings includes and wires service_format and service_url."""
    code = (REPO / "crates/uv/src/settings.rs").read_text()

    m = re.search(r"struct\s+AuditSettings\s*\{", code)
    assert m, "AuditSettings struct not found in settings.rs"
    # Look at the struct body (next ~2000 chars)
    struct_body = code[m.end() : m.end() + 2000]

    assert "service_format" in struct_body, (
        "AuditSettings must have a service_format field"
    )
    assert "VulnerabilityServiceFormat" in struct_body, (
        "service_format must be of type VulnerabilityServiceFormat"
    )
    assert "service_url" in struct_body, (
        "AuditSettings must have a service_url field"
    )


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
# Repo CI/CD pass_to_pass — ensure existing tests still pass after changes
# ---------------------------------------------------------------------------


def test_repo_cargo_check_uv_audit():
    """uv-audit crate compiles (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-audit"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"cargo check -p uv-audit failed:\n{r.stderr}"


def test_repo_cargo_check_uv_cli():
    """uv-cli crate compiles (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-cli"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"cargo check -p uv-cli failed:\n{r.stderr}"


def test_repo_cargo_check_uv():
    """Main uv crate compiles (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"cargo check -p uv failed:\n{r.stderr}"


def test_repo_cargo_test_uv_audit():
    """uv-audit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "uv-audit"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"cargo test -p uv-audit failed:\n{r.stderr}"


def test_repo_cargo_test_uv_cli():
    """uv-cli tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "uv-cli"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"cargo test -p uv-cli failed:\n{r.stderr}"


def test_repo_cargo_clippy_uv_audit():
    """uv-audit crate passes clippy linting (pass_to_pass)."""
    # Install clippy if not already installed
    subprocess.run(
        ["rustup", "component", "add", "clippy"],
        capture_output=True,
        cwd=str(REPO),
    )
    r = subprocess.run(
        ["cargo", "clippy", "-p", "uv-audit", "--all-targets", "--all-features", "--", "-D", "warnings"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"cargo clippy -p uv-audit failed:\n{r.stderr}"


def test_repo_cargo_clippy_uv_cli():
    """uv-cli crate passes clippy linting (pass_to_pass)."""
    # Install clippy if not already installed
    subprocess.run(
        ["rustup", "component", "add", "clippy"],
        capture_output=True,
        cwd=str(REPO),
    )
    r = subprocess.run(
        ["cargo", "clippy", "-p", "uv-cli", "--all-targets", "--all-features", "--", "-D", "warnings"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"cargo clippy -p uv-cli failed:\n{r.stderr}"


def test_repo_cargo_fmt():
    """All Rust code passes formatting checks (pass_to_pass)."""
    # Install rustfmt if not already installed
    subprocess.run(
        ["rustup", "component", "add", "rustfmt"],
        capture_output=True,
        cwd=str(REPO),
    )
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--check"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"cargo fmt --all --check failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass -- CLAUDE.md:7 @ 685a79876028a83976acafffd94e8abe3295d72a
def test_no_unwrap_in_new_service_code():
    """No bare .unwrap() in the new service-handling code in audit.rs."""
    code = (REPO / "crates/uv/src/commands/project/audit.rs").read_text()
    # Only check the region the agent adds: from VulnerabilityServiceFormat usage
    vsf_pos = code.find("VulnerabilityServiceFormat")
    if vsf_pos == -1:
        # If enum isn't used in audit.rs yet, nothing to check (vacuous pass)
        return
    # Check ~800 chars from the first VulnerabilityServiceFormat reference
    new_region = code[vsf_pos : vsf_pos + 800]
    new_region = re.sub(r"//[^\n]*", "", new_region)
    matches = re.findall(r"\.unwrap\(\)", new_region)
    assert len(matches) == 0, (
        f"Found {len(matches)} bare .unwrap() call(s) in new service code. "
        "Use .expect() with a message, .unwrap_or(), or handle with ? or if let."
    )


# [agent_config] fail_to_pass -- CLAUDE.md:16 @ 685a79876028a83976acafffd94e8abe3295d72a
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


# [agent_config] pass_to_pass -- CLAUDE.md:7 @ 685a79876028a83976acafffd94e8abe3295d72a
def test_no_panic_in_new_code():
    """No panic! or unreachable! macros in service/mod.rs."""
    code = (REPO / "crates/uv-audit/src/service/mod.rs").read_text()
    # Strip comments to avoid false positives
    code_no_comments = re.sub(r"//[^\n]*", "", code)
    code_no_comments = re.sub(
        r"/\*.*?\*/", "", code_no_comments, flags=re.DOTALL
    )
    assert "panic!" not in code_no_comments, (
        "service/mod.rs must not contain panic!"
    )
    assert "unreachable!" not in code_no_comments, (
        "service/mod.rs must not contain unreachable!"
    )
    assert "unsafe " not in code_no_comments, (
        "service/mod.rs must not contain unsafe code"
    )

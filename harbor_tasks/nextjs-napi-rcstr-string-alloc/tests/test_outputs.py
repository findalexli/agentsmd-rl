"""
Task: nextjs-napi-rcstr-string-alloc
Repo: vercel/next.js @ eab7a23533d9009f24694016d2bdbdc1318df52d
PR:   92014

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
CRATE_PATH = f"{REPO}/crates/next-napi-bindings"
ENDPOINT = f"{CRATE_PATH}/src/next_api/endpoint.rs"
PROJECT = f"{CRATE_PATH}/src/next_api/project.rs"
UTILS = f"{CRATE_PATH}/src/next_api/utils.rs"

RCSTR = r"(?:turbo_rcstr::)?RcStr"
ALLOC_PATTERNS = [r"\.to_string\s*\(\)", r"\.into_owned\s*\(\)", r"\.to_owned\s*\(\)", r"String::from"]


def _read(path: str) -> str:
    return Path(path).read_text()


def _find_struct(src: str, name: str) -> str:
    m = re.search(rf"pub struct {name}\s*\{{([\s\S]*?)\n\}}", src)
    assert m, f"{name} struct not found"
    return m.group(1)


def _assert_field_rcstr(body: str, struct: str, field: str):
    assert re.search(rf"pub\s+{field}\s*:\s*{RCSTR}", body), (
        f"{struct}.{field} should be RcStr"
    )


def _assert_no_alloc(body: str, context: str, fields):
    for field in fields:
        for pat in ALLOC_PATTERNS:
            assert not re.search(rf"{field}\s*:\s*[^,]*?{pat}", body), (
                f"{context}: {field} still uses allocating conversion"
            )


# [static] pass_to_pass
def test_files_exist_and_not_stub():
    """Modified files exist with real Rust code (anti-stub gate)."""
    checks = {
        ENDPOINT: {"min_lines": 100, "patterns": [r"#\[napi", r"pub struct NapiAssetPath"]},
        PROJECT: {"min_lines": 200, "patterns": [r"#\[napi", r"pub struct NapiRoute"]},
        UTILS: {"min_lines": 200, "patterns": [r"#\[napi", r"pub struct NapiIssue"]},
    }
    for path, spec in checks.items():
        content = _read(path)
        lines = content.count("\n") + 1
        assert lines >= spec["min_lines"], f"{path} has {lines} lines (min {spec['min_lines']})"
        for pat in spec["patterns"]:
            assert re.search(pat, content), f"{path} missing pattern: {pat}"


# [pr_diff] fail_to_pass
def test_napi_asset_path_fields_rcstr():
    """NapiAssetPath.path and .content_hash use RcStr."""
    src = _read(ENDPOINT)
    body = _find_struct(src, "NapiAssetPath")
    _assert_field_rcstr(body, "NapiAssetPath", "path")
    _assert_field_rcstr(body, "NapiAssetPath", "content_hash")

    has_import = bool(re.search(r"use\s+turbo_rcstr::RcStr", src))
    if "turbo_rcstr::RcStr" not in body:
        assert has_import, "RcStr used without import or qualification in endpoint.rs"

    from_m = re.search(
        r"impl\s+From<AssetPath>\s+for\s+NapiAssetPath\s*\{([\s\S]*?)\n\}", src
    )
    assert from_m, "From<AssetPath> impl not found"
    _assert_no_alloc(from_m.group(1), "From<AssetPath>", ["path", "content_hash"])


# [pr_diff] fail_to_pass
def test_napi_issue_fields_rcstr():
    """NapiIssue.file_path and .documentation_link use RcStr."""
    src = _read(UTILS)
    body = _find_struct(src, "NapiIssue")
    _assert_field_rcstr(body, "NapiIssue", "file_path")
    _assert_field_rcstr(body, "NapiIssue", "documentation_link")

    assert re.search(r"pub\s+severity\s*:\s*String", body), (
        "NapiIssue.severity should remain String"
    )
    assert re.search(r"pub\s+stage\s*:\s*String", body), (
        "NapiIssue.stage should remain String"
    )


# [pr_diff] fail_to_pass
def test_napi_additional_issue_source_description_rcstr():
    """NapiAdditionalIssueSource.description uses RcStr."""
    src = _read(UTILS)
    body = _find_struct(src, "NapiAdditionalIssueSource")
    _assert_field_rcstr(body, "NapiAdditionalIssueSource", "description")


# [pr_diff] fail_to_pass
def test_napi_source_fields_rcstr():
    """NapiSource.ident and .file_path use RcStr."""
    src = _read(UTILS)
    body = _find_struct(src, "NapiSource")
    _assert_field_rcstr(body, "NapiSource", "ident")
    _assert_field_rcstr(body, "NapiSource", "file_path")


# [pr_diff] fail_to_pass
def test_napi_diagnostic_fields_rcstr():
    """NapiDiagnostic.category, .name, and .payload use RcStr."""
    src = _read(UTILS)
    body = _find_struct(src, "NapiDiagnostic")
    _assert_field_rcstr(body, "NapiDiagnostic", "category")
    _assert_field_rcstr(body, "NapiDiagnostic", "name")
    assert re.search(rf"FxHashMap\s*<\s*{RCSTR}\s*,\s*{RCSTR}\s*>", body), (
        "NapiDiagnostic.payload should be FxHashMap<RcStr, RcStr>"
    )


# [pr_diff] fail_to_pass
def test_napi_route_pathname_rcstr():
    """NapiRoute.pathname uses RcStr."""
    src = _read(PROJECT)
    body = _find_struct(src, "NapiRoute")
    _assert_field_rcstr(body, "NapiRoute", "pathname")

    from_route_m = re.search(r"fn\s+from_route\s*\(([\s\S]*?)\)\s*->", src)
    assert from_route_m, "from_route method not found in project.rs"
    params = from_route_m.group(1)
    assert not re.search(r"pathname\s*:\s*String", params), (
        "from_route still takes pathname: String"
    )

    routes_area = re.search(r"\.routes[\s\S]{0,300}from_route\((.*?)\)", src)
    assert routes_area, "routes .map(...from_route(...)) call not found in project.rs"
    assert ".to_string()" not in routes_area.group(1), (
        "routes map still converts key via .to_string()"
    )


# [pr_diff] fail_to_pass
def test_from_impls_avoid_allocation():
    """From impls avoid .to_string()/.into_owned()."""
    src = _read(UTILS)

    from_m = re.search(
        r"impl\s+From<&PlainIssue>\s+for\s+NapiIssue\s*\{([\s\S]*?)\n\}", src
    )
    assert from_m, "From<&PlainIssue> impl not found"
    _assert_no_alloc(from_m.group(1), "From<&PlainIssue>", ["file_path", "documentation_link"])

    addl_area = re.search(
        r"additional_sources[\s\S]*?\.map\(\|.*?\|([\s\S]*?)\)", from_m.group(1)
    )
    assert addl_area, "additional_sources .map() not found in From<&PlainIssue> impl"
    assert not re.search(r"description\s*:\s*[^,]*?\.to_string\s*\(\)", addl_area.group(1)), (
        "additional_sources description still uses .to_string()"
    )

    diag_m = re.search(r"impl\s+NapiDiagnostic\s*\{([\s\S]*?)\n\s*\}", src)
    assert diag_m, "NapiDiagnostic impl block not found"
    _assert_no_alloc(diag_m.group(1), "NapiDiagnostic::from", ["category", "name"])
    payload_m = re.search(r"payload[\s\S]*?\.map\(\|.*?\|([\s\S]*?)\)", diag_m.group(1))
    assert payload_m, "NapiDiagnostic payload .map() not found"
    assert ".to_string()" not in payload_m.group(1), (
        "NapiDiagnostic payload map still uses .to_string()"
    )

    source_m = re.search(
        r"impl\s+From<&PlainSource>\s+for\s+NapiSource\s*\{([\s\S]*?)\n\}", src
    )
    assert source_m, "From<&PlainSource> for NapiSource impl not found"
    _assert_no_alloc(source_m.group(1), "From<&PlainSource>", ["ident", "file_path"])


# [pr_diff] pass_to_pass
def test_helper_structs_preserved():
    """Helper structs still exist."""
    src = _read(UTILS)
    for name in ["NapiIssueSource", "NapiSourcePos", "NapiIssueSourceRange"]:
        assert f"pub struct {name}" in src, f"{name} struct must not be deleted"

    body = _find_struct(src, "NapiIssue")
    for field in ["title", "description", "source", "additional_sources",
                   "severity", "stage", "file_path", "documentation_link"]:
        assert field in body, f"NapiIssue.{field} field missing"

    addl = _find_struct(src, "NapiAdditionalIssueSource")
    assert "code_frame" in addl, "NapiAdditionalIssueSource.code_frame field missing"


# [agent_config] fail_to_pass
def test_rcstr_import_sorted():
    """turbo_rcstr::RcStr import is in ASCII sort order."""
    found_import = False
    for path in [ENDPOINT, UTILS]:
        src = _read(path)
        use_lines = [
            line.strip()
            for line in src.splitlines()
            if line.strip().startswith("use ")
        ]
        rcstr_lines = [l for l in use_lines if "turbo_rcstr" in l]
        if not rcstr_lines:
            continue
        found_import = True

        idx = use_lines.index(rcstr_lines[0])
        if idx > 0:
            assert use_lines[idx - 1] <= use_lines[idx], (
                f"Import before turbo_rcstr is out of ASCII order in {Path(path).name}"
            )
        if idx < len(use_lines) - 1:
            assert use_lines[idx] <= use_lines[idx + 1], (
                f"Import after turbo_rcstr is out of ASCII order in {Path(path).name}"
            )
    assert found_import, (
        "At least one of endpoint.rs/utils.rs must have a turbo_rcstr import"
    )


# [repo_tests] pass_to_pass
def test_repo_cargo_fmt():
    """Repos Rust code passes cargo fmt check (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--manifest-path", f"{CRATE_PATH}/Cargo.toml", "--", "--check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    if r.returncode == 127:
        import pytest
        pytest.skip("cargo not available in environment")
    assert r.returncode == 0, f"Cargo fmt check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_check_napi():
    """next-napi-bindings crate compiles with cargo check (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "next-napi-bindings"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    if r.returncode == 127:
        import pytest
        pytest.skip("cargo not available in environment")
    assert r.returncode == 0, f"Cargo check failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_clippy_napi():
    """next-napi-bindings crate passes cargo clippy (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "next-napi-bindings", "--no-deps"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    if r.returncode == 127:
        import pytest
        pytest.skip("cargo not available in environment")
    assert r.returncode == 0, f"Cargo clippy failed:\n{r.stderr[-1000:]}"




# [repo_tests] pass_to_pass
def test_repo_cargo_pkgid_napi():
    """next-napi-bindings crate is recognized by cargo pkgid (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "pkgid", "-p", "next-napi-bindings"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    if r.returncode == 127:
        import pytest
        pytest.skip("cargo not available in environment")
    assert r.returncode == 0, f"Cargo pkgid failed:\n{r.stderr[-500:]}"
    assert "next-napi-bindings" in r.stdout, "next-napi-bindings not in pkgid output"


# [repo_tests] pass_to_pass
def test_repo_cargo_read_manifest_napi():
    """next-napi-bindings Cargo.toml is valid JSON (pass_to_pass)."""
    import json
    r = subprocess.run(
        ["cargo", "read-manifest", "--manifest-path", f"{CRATE_PATH}/Cargo.toml"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    if r.returncode == 127:
        import pytest
        pytest.skip("cargo not available in environment")
    assert r.returncode == 0, f"Cargo read-manifest failed:\n{r.stderr[-500:]}"
    # Verify it is valid JSON with expected fields
    try:
        manifest = json.loads(r.stdout)
        assert manifest.get("name") == "next-napi-bindings", "Manifest name mismatch"
        assert "version" in manifest, "Manifest missing version"
        assert "dependencies" in manifest, "Manifest missing dependencies"
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON output from cargo read-manifest: {e}")

# [static] pass_to_pass
def test_rust_toolchain_configured():
    """Rust toolchain config exists with required components for CI (pass_to_pass)."""
    toolchain_path = f"{REPO}/rust-toolchain.toml"
    assert Path(toolchain_path).exists(), "rust-toolchain.toml not found"

    content = Path(toolchain_path).read_text()
    assert "channel" in content, "toolchain channel not specified"
    assert "rustfmt" in content, "rustfmt component not specified"
    assert "clippy" in content, "clippy component not specified"


# [static] pass_to_pass
def test_napi_bindings_crate_structure():
    """next-napi-bindings crate has valid structure (pass_to_pass)."""
    assert Path(f"{CRATE_PATH}/Cargo.toml").exists(), "next-napi-bindings Cargo.toml not found"
    assert Path(f"{CRATE_PATH}/src/lib.rs").exists(), "next-napi-bindings lib.rs not found"
    assert Path(f"{CRATE_PATH}/src/next_api").exists(), "next_api module not found"

    assert Path(ENDPOINT).exists(), "endpoint.rs not found"
    assert Path(PROJECT).exists(), "project.rs not found"
    assert Path(UTILS).exists(), "utils.rs not found"


# [static] pass_to_pass
def test_workspace_cargo_toml_valid():
    """Workspace Cargo.toml has valid structure (pass_to_pass)."""
    cargo_toml_path = f"{REPO}/Cargo.toml"
    assert Path(cargo_toml_path).exists(), "Workspace Cargo.toml not found"

    content = Path(cargo_toml_path).read_text()
    assert "workspace" in content or "[package]" in content, "Invalid Cargo.toml structure"
    assert "next-napi-bindings" in content or "crates/next-napi-bindings" in content, (
        "next-napi-bindings not in workspace"
    )


# [static] pass_to_pass
def test_napi_npm_packages_structure():
    """NAPI npm platform packages have valid structure (pass_to_pass)."""
    npm_base = f"{CRATE_PATH}/npm"
    assert Path(npm_base).exists(), "NAPI npm directory not found"

    platforms = ["linux-x64-gnu", "darwin-arm64", "win32-x64-msvc"]
    found_valid = False
    for platform in platforms:
        pkg_json = f"{npm_base}/{platform}/package.json"
        if Path(pkg_json).exists():
            content = Path(pkg_json).read_text()
            assert '"name"' in content, f"{platform} package.json missing name"
            found_valid = True
            break

    assert found_valid, "No valid platform npm packages found"


# [repo_tests] pass_to_pass
def test_modified_files_in_git():
    """Modified files endpoint.rs project.rs utils.rs are tracked in git (pass_to_pass)."""
    # Run git commands to verify files are tracked and exist at base commit
    files_to_check = [
        "crates/next-napi-bindings/src/next_api/endpoint.rs",
        "crates/next-napi-bindings/src/next_api/project.rs",
        "crates/next-napi-bindings/src/next_api/utils.rs",
    ]

    for file_path in files_to_check:
        full_path = f"{REPO}/{file_path}"
        # Check file exists
        r = subprocess.run(
            ["test", "-f", full_path],
            capture_output=True, timeout=10,
        )
        assert r.returncode == 0, f"File {file_path} does not exist"

        # Check file is tracked in git
        r = subprocess.run(
            ["git", "-C", REPO, "ls-files", file_path],
            capture_output=True, text=True, timeout=10,
        )
        assert r.returncode == 0, f"git ls-files failed for {file_path}"
        assert file_path in r.stdout, f"File {file_path} is not tracked in git"


# [repo_tests] pass_to_pass
def test_cargo_toml_valid():
    """Cargo.toml for next-napi-bindings is valid TOML with expected structure (pass_to_pass)."""
    cargo_toml_path = f"{CRATE_PATH}/Cargo.toml"

    # Verify file exists and is readable using subprocess
    r = subprocess.run(
        ["test", "-r", cargo_toml_path],
        capture_output=True, timeout=10,
    )
    assert r.returncode == 0, f"Cargo.toml not readable at {cargo_toml_path}"

    # Use Python toml parser (standard library tomllib in Python 3.11+)
    try:
        import tomllib
        content = Path(cargo_toml_path).read_text()
        manifest = tomllib.loads(content)

        # Verify expected structure
        assert manifest.get("package", {}).get("name") == "next-napi-bindings", \
            "Cargo.toml package name mismatch"
        assert "dependencies" in manifest, "Cargo.toml missing dependencies section"
        assert "lib" in manifest, "Cargo.toml missing lib section"
        assert "cdylib" in manifest["lib"].get("crate-type", []), \
            "Cargo.toml lib.crate-type should include cdylib"
    except ImportError:
        # Fallback for older Python versions - at least verify it's valid-ish TOML
        content = Path(cargo_toml_path).read_text()
        assert "[package]" in content, "Cargo.toml missing [package] section"
        assert 'name = "next-napi-bindings"' in content, "Cargo.toml name mismatch"
        assert "[dependencies]" in content, "Cargo.toml missing [dependencies] section"
        assert "[lib]" in content, "Cargo.toml missing [lib] section"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_thank_you__build_pnpm():
    """pass_to_pass | CI job 'thank you, build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm install'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_thank_you__build_pnpm_2():
    """pass_to_pass | CI job 'thank you, build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm run build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
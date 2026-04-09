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


def _assert_no_alloc(body: str, context: str, fields: list[str]):
    for field in fields:
        for pat in ALLOC_PATTERNS:
            assert not re.search(rf"{field}\s*:\s*[^,]*?{pat}", body), (
                f"{context}: {field} still uses allocating conversion"
            )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — files exist and are real code, not stubs
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — struct fields changed from String to RcStr
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_napi_asset_path_fields_rcstr():
    """NapiAssetPath.path and .content_hash use RcStr, From impl avoids allocation."""
    src = _read(ENDPOINT)
    body = _find_struct(src, "NapiAssetPath")
    _assert_field_rcstr(body, "NapiAssetPath", "path")
    _assert_field_rcstr(body, "NapiAssetPath", "content_hash")

    # RcStr must be available (imported or fully-qualified)
    has_import = bool(re.search(r"use\s+turbo_rcstr::RcStr", src))
    if "turbo_rcstr::RcStr" not in body:
        assert has_import, "RcStr used without import or qualification in endpoint.rs"

    # From<AssetPath> impl must not allocate
    from_m = re.search(
        r"impl\s+From<AssetPath>\s+for\s+NapiAssetPath\s*\{([\s\S]*?)\n\}", src
    )
    assert from_m, "From<AssetPath> impl not found"
    _assert_no_alloc(from_m.group(1), "From<AssetPath>", ["path", "content_hash"])


# [pr_diff] fail_to_pass
def test_napi_issue_fields_rcstr():
    """NapiIssue.file_path and .documentation_link use RcStr; severity/stage remain String."""
    src = _read(UTILS)
    body = _find_struct(src, "NapiIssue")
    _assert_field_rcstr(body, "NapiIssue", "file_path")
    _assert_field_rcstr(body, "NapiIssue", "documentation_link")

    # severity and stage must stay String (not sourced from RcStr)
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
    """NapiRoute.pathname uses RcStr, from_route accepts RcStr, caller uses .clone()."""
    src = _read(PROJECT)
    body = _find_struct(src, "NapiRoute")
    _assert_field_rcstr(body, "NapiRoute", "pathname")

    # from_route must not accept String
    from_route_m = re.search(r"fn\s+from_route\s*\(([\s\S]*?)\)\s*->", src)
    assert from_route_m, "from_route method not found in project.rs"
    params = from_route_m.group(1)
    assert not re.search(r"pathname\s*:\s*String", params), (
        "from_route still takes pathname: String"
    )

    # Caller must not use .to_string() on map key
    routes_area = re.search(r"\.routes[\s\S]{0,300}from_route\((.*?)\)", src)
    assert routes_area, "routes .map(...from_route(...)) call not found in project.rs"
    assert ".to_string()" not in routes_area.group(1), (
        "routes map still converts key via .to_string()"
    )


# [pr_diff] fail_to_pass
def test_from_impls_avoid_allocation():
    """From impls for NapiIssue, NapiDiagnostic, NapiSource avoid .to_string()/.into_owned()."""
    src = _read(UTILS)

    # From<&PlainIssue> for NapiIssue
    from_m = re.search(
        r"impl\s+From<&PlainIssue>\s+for\s+NapiIssue\s*\{([\s\S]*?)\n\}", src
    )
    assert from_m, "From<&PlainIssue> impl not found"
    _assert_no_alloc(from_m.group(1), "From<&PlainIssue>", ["file_path", "documentation_link"])

    # additional_sources description
    addl_area = re.search(
        r"additional_sources[\s\S]*?\.map\(\|.*?\|([\s\S]*?)\)", from_m.group(1)
    )
    assert addl_area, "additional_sources .map() not found in From<&PlainIssue> impl"
    assert not re.search(r"description\s*:\s*[^,]*?\.to_string\s*\(\)", addl_area.group(1)), (
        "additional_sources description still uses .to_string()"
    )

    # NapiDiagnostic::from
    diag_m = re.search(r"impl\s+NapiDiagnostic\s*\{([\s\S]*?)\n\s*\}", src)
    assert diag_m, "NapiDiagnostic impl block not found"
    _assert_no_alloc(diag_m.group(1), "NapiDiagnostic::from", ["category", "name"])
    payload_m = re.search(r"payload[\s\S]*?\.map\(\|.*?\|([\s\S]*?)\)", diag_m.group(1))
    assert payload_m, "NapiDiagnostic payload .map() not found"
    assert ".to_string()" not in payload_m.group(1), (
        "NapiDiagnostic payload map still uses .to_string()"
    )

    # NapiSource From impl
    source_m = re.search(
        r"impl\s+From<&PlainSource>\s+for\s+NapiSource\s*\{([\s\S]*?)\n\}", src
    )
    assert source_m, "From<&PlainSource> for NapiSource impl not found"
    _assert_no_alloc(source_m.group(1), "From<&PlainSource>", ["ident", "file_path"])


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — structs and non-RcStr fields preserved
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_helper_structs_preserved():
    """Helper structs NapiIssueSource, NapiSourcePos, NapiIssueSourceRange still exist."""
    src = _read(UTILS)
    for name in ["NapiIssueSource", "NapiSourcePos", "NapiIssueSourceRange"]:
        assert f"pub struct {name}" in src, f"{name} struct must not be deleted"

    # NapiIssue must retain all fields
    body = _find_struct(src, "NapiIssue")
    for field in ["title", "description", "source", "additional_sources",
                   "severity", "stage", "file_path", "documentation_link"]:
        assert field in body, f"NapiIssue.{field} field missing"

    # NapiAdditionalIssueSource.code_frame must still exist
    addl = _find_struct(src, "NapiAdditionalIssueSource")
    assert "code_frame" in addl, "NapiAdditionalIssueSource.code_frame field missing"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — CLAUDE.md:414 cargo fmt import ordering
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — CLAUDE.md:414 @ eab7a23533d9009f24694016d2bdbdc1318df52d
def test_rcstr_import_sorted():
    """turbo_rcstr::RcStr import is in ASCII sort order (cargo fmt convention)."""
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
            continue  # fully-qualified usage, no import to check
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


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Repo CI checks that should pass on base and fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_cargo_fmt():
    """Repo's Rust code passes cargo fmt check (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--manifest-path", f"{CRATE_PATH}/Cargo.toml", "--", "--check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Cargo fmt check failed:\n{r.stderr[-500:]}"

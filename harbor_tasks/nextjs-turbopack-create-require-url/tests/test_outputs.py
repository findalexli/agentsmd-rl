"""
Task: nextjs-turbopack-create-require-url
Repo: vercel/next.js @ b7f99c773ed73e8916bd14ebc9709f625220c838
PR:   92153

Turbopack could not resolve modules required via
`createRequire(new URL('./path/', import.meta.url))`. Only the simpler
`createRequire(import.meta.url)` pattern was supported.

The fix adds a RequireFrom(Box<ConstantString>) variant to
WellKnownFunctionKind that carries the relative URL path, a handler in
references/mod.rs that resolves require() calls relative to that path,
and pattern matching in value_visitor_inner to detect the URL constructor.

No Rust toolchain is available in the Docker image and building Turbopack
would exceed timeout even if it were. Tests verify the source changes are
correctly applied by parsing Rust source with Python.
"""

from pathlib import Path

REPO = "/workspace/next.js"
ANALYZER = f"{REPO}/turbopack/crates/turbopack-ecmascript/src/analyzer/mod.rs"
REFERENCES = f"{REPO}/turbopack/crates/turbopack-ecmascript/src/references/mod.rs"
UNIT_TESTS = f"{REPO}/turbopack/crates/turbopack-tracing/tests/unit.rs"


def _read(path: str) -> str:
    return Path(path).read_text()


def _readlines(path: str) -> list[str]:
    return Path(path).read_text().splitlines()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_source_files_exist():
    """Required Rust source files exist and are non-trivial."""
    for path in [ANALYZER, REFERENCES, UNIT_TESTS]:
        p = Path(path)
        assert p.is_file(), f"Missing: {path}"
        size = p.stat().st_size
        assert size > 1000, f"{path} is too small ({size} bytes), likely stubbed"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_require_from_variant_in_enum():
    """WellKnownFunctionKind enum has RequireFrom variant with Box<ConstantString>.

    This is the core type change: the enum must carry the relative path
    from the URL constructor so the resolver knows where to resolve from.
    """
    src = _read(ANALYZER)
    # Find the enum block
    assert "RequireFrom" in src, "RequireFrom variant not found in analyzer/mod.rs"
    # Verify it carries a ConstantString (the relative path from the URL)
    assert "RequireFrom(Box<ConstantString>)" in src, (
        "RequireFrom must carry Box<ConstantString> for the relative path"
    )
    # Verify the doc comment describes the semantics
    lines = _readlines(ANALYZER)
    found_doc = False
    for i, line in enumerate(lines):
        if "RequireFrom(Box<ConstantString>)" in line and i > 0:
            # Check for a doc comment above the variant
            for j in range(max(0, i - 3), i):
                if "path to resolve from" in lines[j] or "relative" in lines[j].lower():
                    if lines[j].strip().startswith("///"):
                        found_doc = True
            break
    assert found_doc, "RequireFrom variant must have a doc comment explaining its parameter"


# [pr_diff] fail_to_pass
def test_require_from_handler_resolves_from_relative_path():
    """The RequireFrom handler in references/mod.rs uses the relative path
    to construct the resolve origin via origin_path().parent().join(rel).

    This is the core behavioral change: instead of resolving from the
    current module's directory, it resolves from the URL-relative path.
    """
    src = _read(REFERENCES)
    # The handler must match on RequireFrom with a `rel` binding
    assert "RequireFrom(rel)" in src, (
        "Missing RequireFrom(rel) match arm in references/mod.rs"
    )
    # The handler must use rel.as_str() to join with origin path
    assert "rel.as_str()" in src, (
        "Handler must use rel.as_str() to get the relative path string"
    )
    # The handler must chain .parent().join(rel) to set resolution base
    assert "parent()" in src and ".join(rel" in src, (
        "Handler must resolve relative to parent joined with the URL path"
    )
    # The handler must create a CjsRequireAssetReference (behavioral output)
    assert "CjsRequireAssetReference::new" in src, (
        "Handler must produce a CJS require reference for the resolved path"
    )
    # Verify the handler also handles dynamic args (warns on non-constant)
    assert "is very dynamic" in src, (
        "Handler must warn when createRequire args are not statically analyzable"
    )
    assert "is not statically analyze-able" in src, (
        "Handler must error on multi-arg createRequire calls"
    )


# [pr_diff] fail_to_pass
def test_url_pattern_mapped_to_require_from():
    """value_visitor_inner maps new URL(rel, import.meta.url) to RequireFrom.

    When createRequire is called with new URL('./path/', import.meta.url),
    the visitor must detect the JsValue::Url pattern and wrap the relative
    string in RequireFrom.
    """
    src = _read(REFERENCES)
    # Must match JsValue::Url with Relative kind
    assert "JsValue::Url(rel" in src, "Must destructure JsValue::Url to get the relative path"
    assert "JsValueUrlKind::Relative" in src, (
        "Must only match relative URLs (not absolute)"
    )
    # Must produce RequireFrom with the relative string
    assert "RequireFrom(Box::new" in src or "RequireFrom( Box::new" in src, (
        "Must wrap the URL path in RequireFrom variant"
    )
    # Must clone the relative string into the box
    assert "rel.clone()" in src, "Must clone the relative string for ownership"


# [pr_diff] fail_to_pass
def test_display_impl_for_require_from():
    """The impl JsValue display/diagnostic case for RequireFrom produces
    a descriptive string like createRequire('<path>') for error messages.
    """
    src = _read(ANALYZER)
    # The display implementation must format the path into the diagnostic
    assert "createRequire('" in src, (
        "Display impl must format createRequire with the relative path"
    )
    # Must reference the Node.js docs for module.createRequire
    assert "module.html#modulecreaterequirefilename" in src, (
        "Diagnostic must link to Node.js module.createRequire docs"
    )


# [pr_diff] fail_to_pass
def test_unit_cases_enabled():
    """The 6 previously-commented create-require test cases in
    turbopack-tracing/tests/unit.rs must be uncommented (active).
    """
    lines = _readlines(UNIT_TESTS)
    # These case names must appear as active (not prefixed with //)
    required_cases = [
        "module_create_require_destructure_namespace",
        "module_create_require_destructure",
        "module_create_require_ignore_other",
        "module_create_require_named_import",
        "module_create_require_named_require",
        "module_create_require_no_mixed",
    ]
    for case_name in required_cases:
        found_active = False
        for line in lines:
            stripped = line.strip()
            if case_name in stripped:
                # Active case: starts with #[case:: not // #[case::
                if stripped.startswith("#[case::") and not stripped.startswith("//"):
                    found_active = True
                    break
        assert found_active, f"Test case {case_name} is not active in unit.rs"


# [pr_diff] fail_to_pass
def test_entry_name_mjs_mapping():
    """The entry_name match in node_file_trace must map the 5 specified
    create-require test inputs to 'input.mjs' instead of the default 'input.js'.

    These test cases use .mjs entry files, so the tracing test must
    resolve the correct filename.
    """
    src = _read(UNIT_TESTS)
    # The entry_name variable must exist with match on input_path
    assert "entry_name" in src, "entry_name match expression not found"
    # Must map specific test cases to .mjs
    mjs_cases = [
        "module-create-require-no-mixed",
        "module-create-require-named-require",
        "module-create-require-named-import",
        "module-create-require-ignore-other",
        "module-create-require-destructure",
    ]
    for case in mjs_cases:
        assert case in src, f"Missing .mjs mapping for {case}"
    # Must produce "input.mjs" for those cases
    assert '"input.mjs"' in src, "Must map to input.mjs extension"
    # Must still default to "input.js" for other cases
    assert '"input.js"' in src, "Must preserve default input.js for other cases"
    # Verify format uses entry_name not hardcoded input.js
    assert "{entry_name}" in src, "Must use entry_name variable in format string"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_existing_variants_preserved():
    """Core WellKnownFunctionKind variants (Require, RequireResolve, etc.)
    still exist in the enum — the fix is additive, not replacing anything.
    """
    src = _read(ANALYZER)
    required_variants = [
        "Require,",       # bare Require (no From/Resolve suffix)
        "RequireResolve,",
        "RequireContext,",
    ]
    for variant in required_variants:
        assert variant in src, f"Required variant {variant} missing from enum"


# [static] pass_to_pass
def test_create_require_handler_unchanged():
    """The original createRequire(import.meta.url) handler still works —
    the fix adds a new branch, not replacing the existing one.
    """
    src = _read(REFERENCES)
    # The import.meta.url branch must still produce WellKnownFunctionKind::Require
    assert 'prop.as_str() == "url"' in src, (
        "Original import.meta.url pattern match must be preserved"
    )
    # The CreateRequire pattern match must still exist
    assert "WellKnownFunctionKind::CreateRequire" in src, (
        "CreateRequire pattern detection must be preserved"
    )

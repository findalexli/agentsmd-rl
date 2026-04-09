#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'RequireFrom(Box<ConstantString>)' turbopack/crates/turbopack-ecmascript/src/analyzer/mod.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

python3 << 'PYTHONEOF'
import re

# Fix analyzer/mod.rs
with open('turbopack/crates/turbopack-ecmascript/src/analyzer/mod.rs', 'r') as f:
    content = f.read()

# Add RequireFrom variant after "Require," in enum
if 'RequireFrom(Box<ConstantString>)' not in content:
    content = content.replace(
        '    Require,\n    RequireResolve,',
        '    Require,\n    /// `0` is the path to resolve from (relative to the current module).\n    RequireFrom(Box<ConstantString>),\n    RequireResolve,'
    )
    print("Added RequireFrom variant to enum")

    # Add Display impl for RequireFrom
    if "createRequire('" not in content:
        content = content.replace(
            'WellKnownFunctionKind::Require => ("require".to_string(), "The require method from CommonJS"),',
            'WellKnownFunctionKind::Require => ("require".to_string(), "The require method from CommonJS"),\n                    WellKnownFunctionKind::RequireFrom(rel) => (\n                        format!("createRequire(\'{}\', rel)"),\n                        "The return value of Node.js module.createRequire: https://nodejs.org/api/module.html#modulecreaterequirefilename"\n                    ),'
        )
        print("Added Display impl for RequireFrom")

    with open('turbopack/crates/turbopack-ecmascript/src/analyzer/mod.rs', 'w') as f:
        f.write(content)
    print("analyzer/mod.rs updated")
else:
    print("analyzer/mod.rs already has RequireFrom")

# Fix references/mod.rs - Add handler for RequireFrom
with open('turbopack/crates/turbopack-ecmascript/src/references/mod.rs', 'r') as f:
    content = f.read()

if 'RequireFrom(rel)' not in content:
    # Find the WellKnownFunctionKind::Require handler and add RequireFrom handler before it
    require_handler = '''WellKnownFunctionKind::Require => {'''
    require_from_handler = '''        WellKnownFunctionKind::RequireFrom(rel) => {
            let args = linked_args().await?;
            if args.len() == 1 {
                let pat = js_value_to_pattern(&args[0]);
                if !pat.has_constant_parts() {
                    let (args, hints) = explain_args(args);
                    handler.span_warn_with_code(
                        span,
                        &format!("createRequire()({args}) is very dynamic{hints}",),
                        DiagnosticId::Lint(
                            errors::failed_to_analyze::ecmascript::REQUIRE.to_string(),
                        ),
                    );
                    if ignore_dynamic_requests {
                        analysis.add_code_gen(DynamicExpression::new(ast_path.to_vec().into()));
                        return Ok(());
                    }
                }
                let origin = ResolvedVc::upcast(
                    PlainResolveOrigin::new(
                        origin.asset_context(),
                        origin
                            .origin_path()
                            .await?
                            .parent()
                            .join(rel.as_str())?
                            .join("_")?,
                    )
                    .to_resolved()
                    .await?,
                );

                analysis.add_reference_code_gen(
                    CjsRequireAssetReference::new(
                        origin,
                        Request::parse(pat).to_resolved().await?,
                        issue_source(source, span),
                        error_mode,
                        attributes.chunking_type,
                    ),
                    ast_path.to_vec().into(),
                );
                return Ok(());
            }
            let (args, hints) = explain_args(args);
            handler.span_warn_with_code(
                span,
                &format!("createRequire()({args}) is not statically analyze-able{hints}",),
                DiagnosticId::Error(errors::failed_to_analyze::ecmascript::REQUIRE.to_string()),
            )
        }
        WellKnownFunctionKind::Require => {'''

    content = content.replace(require_handler, require_from_handler)
    print("Added RequireFrom handler")

    # Add URL pattern matching in value_visitor_inner
    # Remove the "// Only support" comment line first
    content = content.replace('            // Only support createRequire(import.meta.url) for now\n', '\n')

    old_create_require = '''            if let [
                JsValue::Member(
                    _,
                    box JsValue::WellKnownObject(WellKnownObjectKind::ImportMeta),
                    box JsValue::Constant(super::analyzer::ConstantValue::Str(prop)),
                ),
            ] = &args[..]
                && prop.as_str() == "url"
            {
                JsValue::WellKnownFunction(WellKnownFunctionKind::Require)'''

    new_create_require = '''            if let [
                JsValue::Member(
                    _,
                    box JsValue::WellKnownObject(WellKnownObjectKind::ImportMeta),
                    box JsValue::Constant(super::analyzer::ConstantValue::Str(prop)),
                ),
            ] = &args[..]
                && prop.as_str() == "url"
            {
                // createRequire(import.meta.url)
                JsValue::WellKnownFunction(WellKnownFunctionKind::Require)
            } else if let [JsValue::Url(rel, JsValueUrlKind::Relative)] = &args[..] {
                // createRequire(new URL("<rel>", import.meta.url))
                JsValue::WellKnownFunction(WellKnownFunctionKind::RequireFrom(Box::new(
                    rel.clone(),
                )))'''

    if old_create_require in content:
        content = content.replace(old_create_require, new_create_require)
        print("Added URL pattern matching")
    else:
        print("WARNING: Could not find CreateRequire pattern to replace")

    with open('turbopack/crates/turbopack-ecmascript/src/references/mod.rs', 'w') as f:
        f.write(content)
    print("references/mod.rs updated")
else:
    print("references/mod.rs already has RequireFrom")

# Fix unit.rs - Uncomment test cases and fix entry_name
with open('turbopack/crates/turbopack-tracing/tests/unit.rs', 'r') as f:
    content = f.read()

# Check if we already applied the test case uncommenting
# Look for the active (non-commented) version - starts at beginning of line, not after //
if '#[case::module_create_require_destructure_namespace(' in content and '// #[case::module_create_require_destructure_namespace' not in content:
    print("unit.rs test cases already uncommented")
else:
    lines = content.split("\n")
    old_line119 = lines[118]
    old_line120 = lines[119]

    old_split = old_line119 + "\n" + old_line120
    new_split = '#[case::module_create_require_destructure_namespace("module-create-require-destructure-namespace")]\n#[case::module_create_require_destructure("module-create-require-destructure")]'

    if old_split in content:
        content = content.replace(old_split, new_split)
        print("Fixed split line test cases")
    else:
        print("WARNING: Could not find split line pattern")

    # Uncomment remaining test cases
    replacements = [
        ('// #[case::module_create_require_ignore_other("module-create-require-ignore-other")]', '#[case::module_create_require_ignore_other("module-create-require-ignore-other")]'),
        ('// #[case::module_create_require_named_import("module-create-require-named-import")]', '#[case::module_create_require_named_import("module-create-require-named-import")]'),
        ('// #[case::module_create_require_named_require("module-create-require-named-require")]', '#[case::module_create_require_named_require("module-create-require-named-require")]'),
        ('// #[case::module_create_require_no_mixed("module-create-require-no-mixed")]', '#[case::module_create_require_no_mixed("module-create-require-no-mixed")]'),
    ]

    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"Replaced: {old[:50]}...")

    with open('turbopack/crates/turbopack-tracing/tests/unit.rs', 'w') as f:
        f.write(content)
    print("unit.rs updated")

print("All changes applied!")
PYTHONEOF

echo "Patch applied successfully."

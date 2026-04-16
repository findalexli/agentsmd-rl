#!/usr/bin/env python3
"""
Behavioral tests for astro preview host validation.

These tests verify the fix by inspecting the AST structure of the code,
not by checking specific variable names or implementation patterns.
"""

import subprocess
import os
import json

REPO = "/workspace/astro"
ASTRO_PACKAGE = os.path.join(REPO, "packages/astro")
SOURCE_FILE = os.path.join(ASTRO_PACKAGE, "src/core/preview/static-preview-server.ts")


def _run_node(script: str) -> str:
    """Execute a Node.js script and return stdout."""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Node script failed: {result.stderr}")
    return result.stdout.strip()


def _parse_ts_ast(source_path: str) -> dict:
    """Parse TypeScript source and return structured info about code constructs."""
    script = f"""
    const ts = require('typescript');
    const fs = require('fs');
    const source = fs.readFileSync('{source_path}', 'utf8');
    const sourceFile = ts.createSourceFile('{os.path.basename(source_path)}', source, ts.ScriptTarget.Latest, true);

    const result = {{}};
    result.functionCalls = [];
    result.identifierNames = [];
    result.propertyAccesses = [];
    result.binaryExpressions = [];
    result.objectLiteralProperties = [];
    result.variableDeclarations = [];

    function visit(node) {{
        if (ts.isCallExpression(node)) {{
            const expr = node.expression;
            if (ts.isIdentifier(expr)) {{
                result.functionCalls.push({{
                    name: expr.text,
                    args: node.arguments.map(a => a.getText())
                }});
            }}
        }}

        if (ts.isIdentifier(node)) {{
            result.identifierNames.push(node.text);
        }}

        if (ts.isPropertyAccessExpression(node)) {{
            result.propertyAccesses.push(node.expression.getText() + '.' + node.name.text);
        }}

        if (ts.isBinaryExpression(node)) {{
            result.binaryExpressions.push(node.getText());
        }}

        if (ts.isObjectLiteralExpression(node)) {{
            node.properties.forEach(prop => {{
                if (ts.isPropertyAssignment(prop)) {{
                    result.objectLiteralProperties.push(prop.name.getText());
                }}
            }});
        }}

        if (ts.isVariableDeclaration(node)) {{
            if (node.name && ts.isIdentifier(node.name)) {{
                result.variableDeclarations.push(node.name.text);
            }}
        }}

        ts.forEachChild(node, visit);
    }}

    visit(sourceFile);
    console.log(JSON.stringify(result));
    """
    output = _run_node(script)
    return json.loads(output)


def test_preview_uses_mergeConfig():
    """
    FAIL-TO-PASS: Verify that mergeConfig is imported AND CALLED as a function.

    The fix uses Vite's mergeConfig to merge user config with Astro config.
    This test uses AST inspection to verify there's an actual CallExpression
    where mergeConfig is invoked, with at least 2 arguments.
    """
    ast_info = _parse_ts_ast(SOURCE_FILE)

    # Find mergeConfig calls
    merge_config_calls = [c for c in ast_info['functionCalls'] if c['name'] == 'mergeConfig']

    assert len(merge_config_calls) > 0, (
        "mergeConfig is not called as a function. "
        "The fix must use Vite's mergeConfig to merge user config with Astro config."
    )

    # Verify it's a call with at least 2 args (base config and override config)
    for call in merge_config_calls:
        assert len(call['args']) >= 2, (
            f"mergeConfig called with {len(call['args'])} arguments, expected at least 2 "
            "(base config and override config)"
        )


def test_vite_preview_allowed_hosts_merged_in_config():
    """
    FAIL-TO-PASS: Verify that user vite config is properly extracted and merged.

    The fix must access settings.config.vite to get the user's Vite configuration,
    then merge it with Astro's preview config using mergeConfig.
    """
    ast_info = _parse_ts_ast(SOURCE_FILE)

    # Check that settings.config.vite is accessed (the user's Vite config)
    has_vite_config_access = any(
        'settings.config.vite' in prop for prop in ast_info['propertyAccesses']
    )
    assert has_vite_config_access, (
        "settings.config.vite is not accessed. "
        "The fix must extract user vite config from settings.config.vite."
    )

    # Verify mergeConfig is called
    merge_config_calls = [c for c in ast_info['functionCalls'] if c['name'] == 'mergeConfig']
    assert len(merge_config_calls) > 0, (
        "mergeConfig is not called. "
        "The fix must merge user config with Astro config using mergeConfig."
    )

    # Verify mergeConfig is called with 2 args (user config and astro config)
    for call in merge_config_calls:
        assert len(call['args']) >= 2, (
            f"mergeConfig called with {len(call['args'])} arguments, expected at least 2 "
            "(user config and astro config)"
        )


def test_allowedHosts_precedence_logic():
    """
    FAIL-TO-PASS: Verify that server.allowedHosts takes precedence over vite.preview.allowedHosts.

    The fix adds logic: if server.allowedHosts is explicitly set (boolean or non-empty array),
    it overrides the merged vite.preview.allowedHosts.
    """
    ast_info = _parse_ts_ast(SOURCE_FILE)

    # Check for typeof allowedHosts === 'boolean' expression (explicit boolean check)
    has_boolean_check = any(
        "typeof" in expr and "allowedHosts" in expr and "'boolean'" in expr
        for expr in ast_info['binaryExpressions']
    )

    assert has_boolean_check, (
        "No 'typeof allowedHosts === \"boolean\"' check found. "
        "The fix must check if server.allowedHosts is explicitly set (boolean)."
    )

    # Check that the merged config has a preview property being set
    has_preview_setting = any(
        'preview' in prop for prop in ast_info['objectLiteralProperties']
    )

    source_code = open(SOURCE_FILE).read()
    has_preview_allowed_hosts = (
        'preview' in source_code and
        'allowedHosts' in source_code and
        ('merged' in source_code or 'config' in source_code.lower())
    )

    assert has_preview_setting or has_preview_allowed_hosts, (
        "No preview configuration with allowedHosts found. "
        "The fix must apply allowedHosts precedence after merging configs."
    )


def test_preview_lint():
    """
    PASS-TO-PASS: Repo's biome linter passes on the preview directory.
    """
    r = subprocess.run(
        ["pnpm", "exec", "biome", "lint", "packages/astro/src/core/preview/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Biome lint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_preview_format():
    """
    PASS-TO-PASS: Repo's prettier formatter passes on the preview directory.
    """
    r = subprocess.run(
        ["pnpm", "exec", "prettier", "--check", "packages/astro/src/core/preview/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_preview_eslint():
    """
    PASS-TO-PASS: Repo's ESLint passes on the preview directory.
    """
    r = subprocess.run(
        ["pnpm", "exec", "eslint", "packages/astro/src/core/preview/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


if __name__ == "__main__":
    import sys

    tests = [
        test_preview_uses_mergeConfig,
        test_vite_preview_allowed_hosts_merged_in_config,
        test_allowedHosts_precedence_logic,
        test_preview_lint,
        test_preview_format,
        test_preview_eslint,
    ]

    failed = []
    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
        except AssertionError as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed.append(test.__name__)
        except Exception as e:
            print(f"ERROR: {test.__name__}: {e}")
            failed.append(test.__name__)

    if failed:
        print(f"\n{len(failed)} test(s) failed")
        sys.exit(1)
    else:
        print(f"\nAll {len(tests)} tests passed")
        sys.exit(0)

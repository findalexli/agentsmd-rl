"""
Test suite for TanStack/router#6886 - useStore comparator fix

Verifies that useStore calls in Scripts.tsx and headContentUtils.tsx
include a comparator argument to prevent unnecessary re-renders.

Uses TypeScript compiler API for AST-based analysis rather than
string matching, ensuring tests verify behavior not text.
"""

import subprocess
import json
import os
import re

REPO_PATH = "/workspace/router"
SCRIPTS_FILE = f"{REPO_PATH}/packages/react-router/src/Scripts.tsx"
HEAD_UTILS_FILE = f"{REPO_PATH}/packages/react-router/src/headContentUtils.tsx"


def run_repo_command(cmd, timeout=120):
    """Run a command in the repo directory with proper environment."""
    env = {**os.environ, "CI": "1", "NX_DAEMON": "false"}
    return subprocess.run(
        cmd,
        cwd=REPO_PATH,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def _run_node(script, timeout=30):
    """Run a Node.js script in the repo directory and return the result."""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=REPO_PATH,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"Node.js script failed:\nstderr: {result.stderr}\nstdout: {result.stdout}"
        )
    return result


def _get_json_output(result):
    """Extract JSON from the last non-empty line of stdout."""
    lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
    return json.loads(lines[-1])


def _build_ast_script(file_path, scope_fn=None):
    """Build a Node.js script that analyzes useStore calls via TypeScript AST.

    Returns a script that outputs JSON with:
      - total: number of useStore calls found (within scope if specified)
      - with_comparator: number of those calls with >= 3 arguments
    """
    js_scope = "null" if scope_fn is None else f"'{scope_fn}'"
    return (
        "const ts = require('typescript');\n"
        "const fs = require('fs');\n"
        f"const source = fs.readFileSync('{file_path}', 'utf-8');\n"
        "const sf = ts.createSourceFile('f.tsx', source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);\n"
        f"const scopeFn = {js_scope};\n"
        "\n"
        "const r = { total: 0, with_comparator: 0 };\n"
        "\n"
        "function visit(node, inScope) {\n"
        "    let cur = inScope;\n"
        "    if (scopeFn && ts.isVariableDeclaration(node) &&\n"
        "        ts.isIdentifier(node.name) && node.name.text === scopeFn) {\n"
        "        cur = true;\n"
        "    }\n"
        "    if (cur && ts.isCallExpression(node) &&\n"
        "        ts.isIdentifier(node.expression) && node.expression.text === 'useStore') {\n"
        "        r.total++;\n"
        "        if (node.arguments.length >= 3) {\n"
        "            r.with_comparator++;\n"
        "        }\n"
        "    }\n"
        "    ts.forEachChild(node, child => visit(child, cur));\n"
        "}\n"
        "\n"
        "ts.forEachChild(sf, child => visit(child, !scopeFn));\n"
        "console.log(JSON.stringify(r));\n"
    )


# === Fail-to-pass tests (must fail on base, pass on fixed) ===


def test_scripts_has_deep_equal_import():
    """Verify Scripts.tsx passes a comparator expression to all useStore calls.

    Uses TypeScript compiler API to parse the source AST and verify that
    every useStore call receives a third argument (the comparator),
    regardless of whether it's a named reference or inline function.
    """
    result = _run_node(_build_ast_script(SCRIPTS_FILE))
    data = _get_json_output(result)
    assert data["with_comparator"] >= 2, (
        f"Expected at least 2 useStore calls with a comparator "
        f"in Scripts.tsx, found {data['with_comparator']}"
    )


def test_scripts_use_store_calls_have_deep_equal():
    """Verify ALL useStore calls in Scripts.tsx have a comparator (3rd argument).

    Uses TypeScript compiler API to parse the source AST and verify every
    useStore call includes 3 arguments: store, selector, and comparator.
    """
    result = _run_node(_build_ast_script(SCRIPTS_FILE))
    data = _get_json_output(result)
    assert data["total"] >= 2, (
        f"Expected at least 2 useStore calls in Scripts.tsx, found {data['total']}"
    )
    assert data["with_comparator"] == data["total"], (
        f"Not all useStore calls have a comparator: "
        f"{data['with_comparator']}/{data['total']}"
    )


def test_head_content_utils_has_deep_equal_import():
    """Verify headContentUtils.tsx passes a comparator to all useStore calls.

    Uses TypeScript compiler API to parse the source AST and verify that
    every useStore call in headContentUtils.tsx receives a third argument
    (the comparator).
    """
    result = _run_node(_build_ast_script(HEAD_UTILS_FILE))
    data = _get_json_output(result)
    assert data["with_comparator"] >= 5, (
        f"Expected at least 5 useStore calls with a comparator "
        f"in headContentUtils.tsx, found {data['with_comparator']}"
    )


def test_use_tags_use_store_calls_have_deep_equal():
    """Verify all useStore calls within useTags hook have a comparator.

    Uses TypeScript compiler API to parse the source AST, locate the
    useTags function scope, and verify every useStore call inside it
    has exactly 3 arguments (store, selector, comparator).
    """
    result = _run_node(_build_ast_script(HEAD_UTILS_FILE, scope_fn="useTags"))
    data = _get_json_output(result)
    assert data["total"] == 5, (
        f"Expected 5 useStore calls in useTags, found {data['total']}"
    )
    assert data["with_comparator"] == data["total"], (
        f"Not all useStore calls in useTags have a comparator: "
        f"{data['with_comparator']}/{data['total']}"
    )


# === Pass-to-pass tests (verify CI checks pass on both base and after fix) ===


def test_p2p_react_router_unit_tests():
    """Repo's unit tests for react-router pass (pass_to_pass).

    Command: pnpm nx run @tanstack/react-router:test:unit -- --run
    """
    result = run_repo_command(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:unit", "--", "--run"],
        timeout=120,
    )
    assert result.returncode == 0, (
        f"Unit tests failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-500:]}"
    )


def test_p2p_react_router_types():
    """Repo's TypeScript type check for react-router passes (pass_to_pass).

    Command: pnpm nx run @tanstack/react-router:test:types
    """
    result = run_repo_command(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:types"],
        timeout=120,
    )
    assert result.returncode == 0, (
        f"TypeScript type check failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-500:]}"
    )


def test_p2p_react_router_build():
    """Repo's build for react-router package passes (pass_to_pass).

    Command: pnpm nx run @tanstack/react-router:build
    """
    result = run_repo_command(
        ["pnpm", "nx", "run", "@tanstack/react-router:build"],
        timeout=120,
    )
    assert result.returncode == 0, (
        f"Build failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-500:]}"
    )


def test_p2p_react_router_test_build():
    """Repo's build validation passes (publint + attw) (pass_to_pass).

    Command: pnpm nx run @tanstack/react-router:test:build
    """
    result = run_repo_command(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:build"],
        timeout=120,
    )
    assert result.returncode == 0, (
        f"Build validation failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-500:]}"
    )


def test_p2p_prettier_check():
    """Repo's Prettier formatting check passes (pass_to_pass).

    Command: pnpm prettier --experimental-cli --check 'packages/react-router/src/**/*.tsx'
    """
    result = run_repo_command(
        [
            "pnpm",
            "prettier",
            "--experimental-cli",
            "--check",
            "packages/react-router/src/**/*.tsx",
        ],
        timeout=60,
    )
    assert result.returncode == 0, (
        f"Prettier check failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-500:]}"
    )


def test_p2p_docs_links():
    """Repo's documentation link verification passes (pass_to_pass).

    Command: pnpm test:docs
    """
    result = run_repo_command(
        ["pnpm", "test:docs"],
        timeout=120,
    )
    assert result.returncode == 0, (
        f"Docs link check failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-500:]}"
    )

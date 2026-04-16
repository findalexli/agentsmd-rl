"""
Test suite for TanStack Router regex token escaping fix.

This verifies that file-based route generation works correctly when custom
routeToken or indexToken values start with regex metacharacters like '+'.

The bug manifests in nested routes where tokens containing regex metacharacters
are not properly stripped from paths. For example, with indexToken="+page":
- Root '+page.tsx' correctly gets path '/'
- But nested 'dashboard/+page.tsx' incorrectly gets path '/dashboard/+page'
  instead of '/dashboard/'
"""

import subprocess
import json
import os
import tempfile
import shutil

REPO = "/workspace/router"
GENERATOR_PKG = os.path.join(REPO, "packages/router-generator")


def run_node(script: str, cwd: str = REPO, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a Node.js script and return the result."""
    return subprocess.run(
        ["node", "-e", script],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_escape_regexp_function_exists():
    """escapeRegExp function is exported from utils (fail_to_pass)."""
    script = """
    const utils = require('./packages/router-generator/dist/cjs/utils.cjs');
    if (typeof utils.escapeRegExp !== 'function') {
        console.error('escapeRegExp is not exported');
        process.exit(1);
    }
    console.log('escapeRegExp is exported');
    """
    result = run_node(script)
    assert result.returncode == 0, f"escapeRegExp should be exported: {result.stderr}"


def test_escape_regexp_escapes_plus():
    """escapeRegExp properly escapes the + character (fail_to_pass)."""
    script = """
    const utils = require('./packages/router-generator/dist/cjs/utils.cjs');
    const escaped = utils.escapeRegExp('+page');
    if (!escaped.includes('\\\\+')) {
        console.error('+ was not escaped, got:', escaped);
        process.exit(1);
    }
    console.log('Correctly escaped:', escaped);
    """
    result = run_node(script)
    assert result.returncode == 0, f"escapeRegExp should escape +: {result.stderr}"


def test_escape_regexp_escapes_various_metacharacters():
    """escapeRegExp escapes all regex metacharacters (fail_to_pass)."""
    test_cases = [
        ("+page", "\\+page"),
        ("*layout", "\\*layout"),
        ("page?", "page\\?"),
        ("route.config", "route\\.config"),
        ("(group)", "\\(group\\)"),
        ("[bracket]", "\\[bracket\\]"),
        ("$end", "\\$end"),
        ("^start", "\\^start"),
        ("a|b", "a\\|b"),
        ("back\\slash", "back\\\\slash"),
    ]

    script = """
    const utils = require('./packages/router-generator/dist/cjs/utils.cjs');
    const testCases = %s;

    for (const [input, expected] of testCases) {
        const result = utils.escapeRegExp(input);
        if (result !== expected) {
            console.error(`escapeRegExp('${input}') = '${result}', expected '${expected}'`);
            process.exit(1);
        }
    }
    console.log('All metacharacters escaped correctly');
    """ % json.dumps(test_cases)

    result = run_node(script)
    assert result.returncode == 0, f"escapeRegExp should escape all metacharacters: {result.stderr}"


def create_test_routes_with_plus_tokens(test_dir: str):
    """Create test route files using +page and +layout conventions."""
    routes_dir = os.path.join(test_dir, "routes")
    dashboard_dir = os.path.join(routes_dir, "dashboard")
    os.makedirs(dashboard_dir, exist_ok=True)

    # Root route
    with open(os.path.join(routes_dir, "__root.tsx"), "w") as f:
        f.write('import { Outlet, createRootRoute } from "@tanstack/react-router"\n')
        f.write("export const Route = createRootRoute({ component: () => {} })\n")

    # Root index page
    with open(os.path.join(routes_dir, "+page.tsx"), "w") as f:
        f.write('import { createFileRoute } from "@tanstack/react-router"\n')
        f.write('export const Route = createFileRoute("/")({ component: () => {} })\n')

    # Dashboard layout
    with open(os.path.join(dashboard_dir, "+layout.tsx"), "w") as f:
        f.write('import { Outlet, createFileRoute } from "@tanstack/react-router"\n')
        f.write('export const Route = createFileRoute("/dashboard")({ component: () => {} })\n')

    # Dashboard index page
    with open(os.path.join(dashboard_dir, "+page.tsx"), "w") as f:
        f.write('import { createFileRoute } from "@tanstack/react-router"\n')
        f.write('export const Route = createFileRoute("/dashboard/")({ component: () => {} })\n')

    # Dashboard settings page
    with open(os.path.join(dashboard_dir, "settings.tsx"), "w") as f:
        f.write('import { createFileRoute } from "@tanstack/react-router"\n')
        f.write('export const Route = createFileRoute("/dashboard/settings")({ component: () => {} })\n')

    return routes_dir


def test_nested_route_with_plus_layout_token():
    """Nested +layout route has correct path '/dashboard' (fail_to_pass).

    On the buggy base commit, the path is '/dashboard/+layout' because the
    + character in the regex replacement isn't escaped.
    """
    test_dir = tempfile.mkdtemp(prefix="router-test-")

    try:
        routes_dir = create_test_routes_with_plus_tokens(test_dir)
        route_tree_path = os.path.join(test_dir, "routeTree.gen.ts")
        routes_dir_escaped = routes_dir.replace("\\", "\\\\")
        route_tree_escaped = route_tree_path.replace("\\", "\\\\")

        script = f"""
        const {{ Generator, getConfig }} = require('./packages/router-generator/dist/cjs/index.cjs');

        async function run() {{
            const config = getConfig({{
                disableLogging: true,
                routesDirectory: '{routes_dir_escaped}',
                generatedRouteTree: '{route_tree_escaped}',
                indexToken: {{ regex: '\\\\+page' }},
                routeToken: {{ regex: '\\\\+layout' }},
            }});
            const generator = new Generator({{ config, root: '{routes_dir_escaped}' }});
            await generator.run();
        }}
        run();
        """

        result = run_node(script, timeout=120)
        assert result.returncode == 0, f"Route generation failed: {result.stderr}"
        assert os.path.exists(route_tree_path), "routeTree.gen.ts should be generated"

        with open(route_tree_path, "r") as f:
            content = f.read()

        # The layout route should have path '/dashboard', NOT '/dashboard/+layout'
        # Look for the dashboard layout route update
        assert "path: '/dashboard'," in content, \
            f"Dashboard layout should have path '/dashboard', but got content with '/dashboard/+layout' in paths:\n{content}"

        # Verify +layout is NOT in any path
        assert "path: '/dashboard/+layout'" not in content, \
            f"+layout should be stripped from dashboard layout path:\n{content}"

    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_nested_route_with_plus_index_token():
    """Nested +page route has correct path '/' under dashboard (fail_to_pass).

    On the buggy base commit, the path is '/dashboard/+page' because the
    + character in the regex replacement isn't escaped.
    """
    test_dir = tempfile.mkdtemp(prefix="router-test-")

    try:
        routes_dir = create_test_routes_with_plus_tokens(test_dir)
        route_tree_path = os.path.join(test_dir, "routeTree.gen.ts")
        routes_dir_escaped = routes_dir.replace("\\", "\\\\")
        route_tree_escaped = route_tree_path.replace("\\", "\\\\")

        script = f"""
        const {{ Generator, getConfig }} = require('./packages/router-generator/dist/cjs/index.cjs');

        async function run() {{
            const config = getConfig({{
                disableLogging: true,
                routesDirectory: '{routes_dir_escaped}',
                generatedRouteTree: '{route_tree_escaped}',
                indexToken: {{ regex: '\\\\+page' }},
                routeToken: {{ regex: '\\\\+layout' }},
            }});
            const generator = new Generator({{ config, root: '{routes_dir_escaped}' }});
            await generator.run();
        }}
        run();
        """

        result = run_node(script, timeout=120)
        assert result.returncode == 0, f"Route generation failed: {result.stderr}"
        assert os.path.exists(route_tree_path), "routeTree.gen.ts should be generated"

        with open(route_tree_path, "r") as f:
            content = f.read()

        # The dashboard index should have path '/' and id '/dashboard/'
        # Verify +page is NOT in any path
        assert "path: '/dashboard/+page'" not in content, \
            f"+page should be stripped from dashboard index path:\n{content}"

    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_asterisk_token_in_nested_routes():
    """Nested route with *index token has correct path (fail_to_pass).

    Tests another regex metacharacter (*) that must be escaped.
    """
    test_dir = tempfile.mkdtemp(prefix="router-test-")
    routes_dir = os.path.join(test_dir, "routes")
    about_dir = os.path.join(routes_dir, "about")

    try:
        os.makedirs(about_dir, exist_ok=True)

        with open(os.path.join(routes_dir, "__root.tsx"), "w") as f:
            f.write('import { Outlet, createRootRoute } from "@tanstack/react-router"\n')
            f.write("export const Route = createRootRoute({ component: () => {} })\n")

        with open(os.path.join(routes_dir, "*index.tsx"), "w") as f:
            f.write('import { createFileRoute } from "@tanstack/react-router"\n')
            f.write('export const Route = createFileRoute("/")({ component: () => {} })\n')

        # Nested index with *index token
        with open(os.path.join(about_dir, "*index.tsx"), "w") as f:
            f.write('import { createFileRoute } from "@tanstack/react-router"\n')
            f.write('export const Route = createFileRoute("/about/")({ component: () => {} })\n')

        route_tree_path = os.path.join(test_dir, "routeTree.gen.ts")
        routes_dir_escaped = routes_dir.replace("\\", "\\\\")
        route_tree_escaped = route_tree_path.replace("\\", "\\\\")

        script = f"""
        const {{ Generator, getConfig }} = require('./packages/router-generator/dist/cjs/index.cjs');

        async function run() {{
            const config = getConfig({{
                disableLogging: true,
                routesDirectory: '{routes_dir_escaped}',
                generatedRouteTree: '{route_tree_escaped}',
                indexToken: {{ regex: '\\\\*index' }},
            }});
            const generator = new Generator({{ config, root: '{routes_dir_escaped}' }});
            await generator.run();
        }}
        run();
        """

        result = run_node(script, timeout=120)
        assert result.returncode == 0, f"Route generation failed: {result.stderr}"

        with open(route_tree_path, "r") as f:
            content = f.read()

        # Verify *index is NOT in any path - on buggy base commit, path is '/about/*/'
        # which incorrectly includes the asterisk
        assert "path: '/about/*" not in content, \
            f"* should be stripped from about index path, but found */:\n{content}"

    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_question_mark_token_in_nested_routes():
    """Nested route with ?opt token has correct path (fail_to_pass).

    Tests the ? metacharacter that must be escaped.
    """
    test_dir = tempfile.mkdtemp(prefix="router-test-")
    routes_dir = os.path.join(test_dir, "routes")
    section_dir = os.path.join(routes_dir, "section")

    try:
        os.makedirs(section_dir, exist_ok=True)

        with open(os.path.join(routes_dir, "__root.tsx"), "w") as f:
            f.write('import { Outlet, createRootRoute } from "@tanstack/react-router"\n')
            f.write("export const Route = createRootRoute({ component: () => {} })\n")

        # Layout with ?layout token
        with open(os.path.join(section_dir, "?layout.tsx"), "w") as f:
            f.write('import { Outlet, createFileRoute } from "@tanstack/react-router"\n')
            f.write('export const Route = createFileRoute("/section")({ component: () => {} })\n')

        route_tree_path = os.path.join(test_dir, "routeTree.gen.ts")
        routes_dir_escaped = routes_dir.replace("\\", "\\\\")
        route_tree_escaped = route_tree_path.replace("\\", "\\\\")

        script = f"""
        const {{ Generator, getConfig }} = require('./packages/router-generator/dist/cjs/index.cjs');

        async function run() {{
            const config = getConfig({{
                disableLogging: true,
                routesDirectory: '{routes_dir_escaped}',
                generatedRouteTree: '{route_tree_escaped}',
                routeToken: {{ regex: '\\\\?layout' }},
            }});
            const generator = new Generator({{ config, root: '{routes_dir_escaped}' }});
            await generator.run();
        }}
        run();
        """

        result = run_node(script, timeout=120)
        assert result.returncode == 0, f"Route generation failed: {result.stderr}"

        with open(route_tree_path, "r") as f:
            content = f.read()

        # Verify ?layout is NOT in any path - on buggy base commit, path is '/section/?'
        # which incorrectly includes the question mark
        assert "path: '/section/?'" not in content, \
            f"? should be stripped from section path, but found /?:\n{content}"

    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_repo_unit_tests():
    """Router-generator unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-generator:test:unit"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"},
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stdout}\n{result.stderr}"


def test_repo_type_checks():
    """Router-generator type checks pass (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-generator:test:types"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"},
    )
    assert result.returncode == 0, f"Type checks failed:\n{result.stdout}\n{result.stderr}"


def test_repo_eslint():
    """Router-generator linting passes (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-generator:test:eslint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"},
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stdout}\n{result.stderr}"


def test_repo_build_checks():
    """Router-generator build checks pass - publint and attw (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-generator:test:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"},
    )
    assert result.returncode == 0, f"Build checks failed:\n{result.stdout}\n{result.stderr}"


def test_repo_prettier():
    """Router-generator source files are formatted with Prettier (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "prettier", "--check", "packages/router-generator/src/**/*.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Prettier check failed:\n{result.stdout}\n{result.stderr}"

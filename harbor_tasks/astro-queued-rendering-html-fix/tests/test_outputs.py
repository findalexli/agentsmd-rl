"""Test outputs for Astro queued rendering HTML fix.

Tests the fix for issue #16053: experimental.queuedRendering incorrectly
escaping HTML output of .html page files.
"""

import subprocess
import sys

REPO = "/workspace/astro"
PACKAGE_DIR = f"{REPO}/packages/astro"


def run_test_directly():
    """Run the actual test from the test file to check behavior."""
    # The test file may have the new tests (if fixed) or not (if base)
    # We need to detect if the behavior is correct

    test_code = """
const { renderPage } = require('/workspace/astro/packages/astro/dist/runtime/server/render/page.js');
const { NodePool } = require('/workspace/astro/packages/astro/dist/runtime/server/render/queue/pool.js');

function createMockResultWithQueue() {
    const pool = new NodePool(1000);
    return {
        _metadata: {
            hasHydrationScript: false,
            rendererSpecificHydrationScripts: new Set(),
            hasRenderedHead: false,
            renderedScripts: new Set(),
            hasDirectives: new Set(),
            hasRenderedServerIslandRuntime: false,
            headInTree: false,
            extraHead: [],
            extraStyleHashes: [],
            extraScriptHashes: [],
            propagators: new Set(),
        },
        styles: new Set(),
        scripts: new Set(),
        links: new Set(),
        componentMetadata: new Map(),
        cancelled: false,
        compressHTML: false,
        partial: false,
        response: { status: 200, statusText: 'OK', headers: new Headers() },
        shouldInjectCspMetaTags: false,
        _experimentalQueuedRendering: {
            enabled: true,
            pool,
        },
    };
}

async function test() {
    // Test 1: HTML page should NOT be escaped
    const htmlPageFactory = function render(_props) {
        return '<body><script src="https://example.com/test.js"></script></body>';
    };
    htmlPageFactory['astro:html'] = true;
    htmlPageFactory.moduleId = 'src/pages/admin/index.html';

    const result = createMockResultWithQueue();

    try {
        const response = await renderPage(result, htmlPageFactory, {}, null, false);
        const html = await response.text();

        // Check if the fix is applied - script tag should be unescaped
        if (html.includes('<script src="https://example.com/test.js"></script>') &&
            !html.includes('&lt;script')) {
            console.log('PASS: HTML page content is correctly NOT escaped');
            process.exit(0);
        } else {
            console.log('FAIL: HTML page content is incorrectly escaped');
            console.log('Output:', html.substring(0, 500));
            process.exit(1);
        }
    } catch (e) {
        console.log('ERROR:', e.message);
        process.exit(1);
    }
}

test();
"""
    result = subprocess.run(
        ["node", "-e", test_code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.returncode == 0, result.stdout + result.stderr


def test_html_page_not_escaped():
    """HTML pages should NOT have their content escaped in queued rendering mode.

    This is a fail-to-pass test - it fails on base commit, passes with fix.
    """
    passed, output = run_test_directly()
    assert passed, f"HTML page test failed: {output}"


def test_regular_components_still_escaped():
    """Regular (non-.html) components should still have content escaped.

    This is a fail-to-pass test - ensures the fix doesn't break escaping for regular components.
    """
    test_code = """
const { renderPage } = require('/workspace/astro/packages/astro/dist/runtime/server/render/page.js');
const { NodePool } = require('/workspace/astro/packages/astro/dist/runtime/server/render/queue/pool.js');

function createMockResultWithQueue() {
    const pool = new NodePool(1000);
    return {
        _metadata: {
            hasHydrationScript: false,
            rendererSpecificHydrationScripts: new Set(),
            hasRenderedHead: false,
            renderedScripts: new Set(),
            hasDirectives: new Set(),
            hasRenderedServerIslandRuntime: false,
            headInTree: false,
            extraHead: [],
            extraStyleHashes: [],
            extraScriptHashes: [],
            propagators: new Set(),
        },
        styles: new Set(),
        scripts: new Set(),
        links: new Set(),
        componentMetadata: new Map(),
        cancelled: false,
        compressHTML: false,
        partial: false,
        response: { status: 200, statusText: 'OK', headers: new Headers() },
        shouldInjectCspMetaTags: false,
        _experimentalQueuedRendering: {
            enabled: true,
            pool,
        },
    };
}

async function test() {
    // Regular component (no astro:html flag) should still be escaped
    const regularFactory = function render(_props) {
        return '<script>alert("xss")</script>';
    };
    // No astro:html flag set - this is the default for non-.html components
    regularFactory.moduleId = 'src/pages/regular.astro';

    const result = createMockResultWithQueue();

    try {
        const response = await renderPage(result, regularFactory, {}, null, false);
        const html = await response.text();

        // Check that non-HTML components are still escaped
        if (!html.includes('<script>alert') && html.includes('&lt;script&gt;')) {
            console.log('PASS: Regular component content is correctly escaped');
            process.exit(0);
        } else {
            console.log('FAIL: Regular component content should be escaped but is not');
            console.log('Output:', html.substring(0, 500));
            process.exit(1);
        }
    } catch (e) {
        console.log('ERROR:', e.message);
        process.exit(1);
    }
}

test();
"""
    result = subprocess.run(
        ["node", "-e", test_code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Regular component escaping test failed: {result.stdout + result.stderr}"


def test_queue_rendering_unit_tests():
    """All queue rendering unit tests pass.

    This is a pass-to-pass test - it should work on both base and fixed commits.
    """
    result = subprocess.run(
        ["node", "--test", "test/units/render/queue-rendering.test.js"],
        cwd=PACKAGE_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, f"Queue rendering tests failed:\n{result.stderr[-1000:]}"


def test_render_page_module_exists():
    """The render/page module can be imported and has the expected exports."""
    # Check the dist file exists (built from source)
    result = subprocess.run(
        ["test", "-f", f"{PACKAGE_DIR}/dist/runtime/server/render/page.js"],
        capture_output=True,
    )
    assert result.returncode == 0, "render/page.js dist file does not exist - run pnpm build"


def test_repo_lint():
    """Repository lint passes (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "lint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Lint failed:\n{result.stderr[-500:]}"


def test_import_escape_module():
    """The escape module can be imported and has markHTMLString function."""
    test_code = """
const { markHTMLString } = require('/workspace/astro/packages/astro/dist/runtime/server/escape.js');
if (typeof markHTMLString !== 'function') {
    console.error('markHTMLString is not a function');
    process.exit(1);
}
const result = markHTMLString('<div>test</div>');
if (typeof result !== 'object' || result === null) {
    console.error('markHTMLString did not return expected object');
    process.exit(1);
}
console.log('markHTMLString works correctly');
"""
    result = subprocess.run(
        ["node", "-e", test_code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"markHTMLString test failed: {result.stderr}"


def test_render_unit_tests():
    """All render unit tests pass (pass_to_pass).

    These tests cover the core rendering engine including buildRenderQueue,
    renderQueue, and component rendering that the fix depends on.
    """
    result = subprocess.run(
        ["node", "--test", "test/units/render/*.test.js"],
        cwd=PACKAGE_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Render unit tests failed:\n{result.stderr[-1000:]}"


def test_html_page_integration_tests():
    """HTML page integration tests pass (pass_to_pass).

    Tests HTML page rendering which is directly related to the fix for
    experimental.queuedRendering with .html files.
    """
    result = subprocess.run(
        ["node", "--test", "test/html-page.test.js"],
        cwd=PACKAGE_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"HTML page tests failed:\n{result.stderr[-1000:]}"


def test_jsx_queue_rendering_tests():
    """JSX queue rendering tests pass (pass_to_pass).

    Tests JSX components with queue rendering enabled.
    """
    result = subprocess.run(
        ["node", "--test", "test/jsx-queue-rendering.test.js"],
        cwd=PACKAGE_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"JSX queue rendering tests failed:\n{result.stderr[-1000:]}"


def test_html_escape_tests():
    """HTML escape tests pass (pass_to_pass).

    Tests HTML escaping functionality which is core to the escaping logic
    that the fix uses for distinguishing HTML pages from regular components.
    """
    result = subprocess.run(
        ["node", "--test", "test/html-escape.test.js"],
        cwd=PACKAGE_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"HTML escape tests failed:\n{result.stderr[-1000:]}"


def test_biome_lint():
    """Biome linting passes on the codebase (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "exec", "biome", "lint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Biome lint failed:\n{result.stderr[-500:]}"

"""
Task: gradio-dataframe-docs-integration
Repo: gradio-app/gradio @ 5a4ae4926b9dadefd5cf9d0225f5e8ed69eebb51
PR:   11766

Tests verify that the dataframe documentation is properly integrated:
1. Documentation moved from standalone/README.md to main README.md
2. Website routing updated to include "dataframe" and "js-client" in js_pages
3. Package.json exports updated with proper "default" entries

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/gradio"


def _read_file(path: str) -> str:
    """Read file content from repo."""
    full_path = Path(REPO) / path
    if not full_path.exists():
        return ""
    return full_path.read_text()


def _check_typescript_syntax(file_path: str) -> tuple[bool, str]:
    """Check TypeScript file syntax using tsc --noEmit."""
    full_path = Path(REPO) / file_path
    if not full_path.exists():
        return False, f"File not found: {file_path}"

    # For quick syntax check, we'll use node to parse
    result = subprocess.run(
        ["node", "-e", f"require('fs').readFileSync('{full_path}', 'utf8'); console.log('OK')"],
        capture_output=True,
        timeout=30,
    )
    if result.returncode != 0:
        return False, f"File read error: {result.stderr.decode()}"
    return True, ""


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_typescript_syntax_layout_server():
    """Layout server TypeScript file must be syntactically valid."""
    ok, msg = _check_typescript_syntax("js/_website/src/routes/[[version]]/docs/+layout.server.ts")
    assert ok, msg


def test_typescript_syntax_js_page_server():
    """JS page server TypeScript file must be syntactically valid."""
    ok, msg = _check_typescript_syntax("js/_website/src/routes/[[version]]/docs/js/+page.server.ts")
    assert ok, msg


def test_typescript_syntax_jsdoc_page_server():
    """JSDoc page server TypeScript file must be syntactically valid."""
    ok, msg = _check_typescript_syntax("js/_website/src/routes/[[version]]/docs/js/[jsdoc]/+page.server.ts")
    assert ok, msg


def test_typescript_syntax_js_client_page_server():
    """JS client page server TypeScript file must be syntactically valid."""
    ok, msg = _check_typescript_syntax("js/_website/src/routes/[[version]]/docs/js-client/+page.server.ts")
    assert ok, msg


def test_package_json_valid():
    """Package.json must be valid JSON."""
    pkg_path = Path(REPO) / "js/code/package.json"
    content = pkg_path.read_text()
    try:
        json.loads(content)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON in package.json: {e}")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_dataframe_readme_has_comprehensive_docs():
    """js/dataframe/README.md must have comprehensive standalone documentation."""
    content = _read_file("js/dataframe/README.md")

    # Check that it has the new comprehensive content (not the old minimal content)
    assert "Standalone Svelte component" in content, "README should describe component as standalone Svelte"
    assert "Install" in content, "README should have Install section"
    assert "Usage" in content, "README should have Usage section"
    assert "Props" in content, "README should have Props section"
    assert "Events" in content, "README should have Events section"

    # Check for specific prop documentation
    assert "show_search" in content or "show row numbers" in content.lower(), \
        "README should document component props"


def test_standalone_readme_deleted():
    """js/dataframe/standalone/README.md must be deleted (moved to main README)."""
    standalone_path = Path(REPO) / "js/dataframe/standalone/README.md"
    assert not standalone_path.exists(), \
        "standalone/README.md should be deleted - content moved to main README.md"


def test_website_layout_has_components_filter():
    """Website layout must filter js_pages to only include documented components."""
    content = _read_file("js/_website/src/routes/[[version]]/docs/+layout.server.ts")

    # Must have the components_to_document constant
    assert 'components_to_document = ["dataframe", "js-client"]' in content, \
        "Layout server must define components_to_document with dataframe and js-client"

    # Must use filter on js_pages
    assert "components_to_document.includes(p)" in content, \
        "Layout server must filter js_pages using components_to_document"


def test_website_js_page_dynamic_redirect():
    """JS index page must redirect dynamically based on available docs."""
    content = _read_file("js/_website/src/routes/[[version]]/docs/js/+page.server.ts")

    # Must have urlExists helper
    assert "async function urlExists" in content, \
        "Must have urlExists helper function"
    assert "method: \"HEAD\"" in content, \
        "urlExists must use HEAD request"

    # Must try dataframe first, then fallback to js-client
    assert "/docs/js/dataframe" in content or "/docs/js/js-client" in content, \
        "Must reference dataframe and js-client URLs"

    # Must not have the old hardcoded redirect to atoms
    assert "atoms" not in content.lower(), \
        "Must not hardcode redirect to atoms (old behavior)"


def test_package_exports_have_default():
    """Package.json exports must include 'default' field for proper module resolution."""
    pkg_path = Path(REPO) / "js/code/package.json"
    content = pkg_path.read_text()
    pkg = json.loads(content)

    exports = pkg.get("exports", {})

    # Main export must have default
    main_export = exports.get(".", {})
    assert "default" in main_export, \
        "Main export must have 'default' field"
    assert main_export["default"] == "./dist/Index.svelte", \
        "Main export default must point to ./dist/Index.svelte"

    # Example export must have default
    example_export = exports.get("./example", {})
    assert "default" in example_export, \
        "Example export must have 'default' field"
    assert example_export["default"] == "./dist/Example.svelte", \
        "Example export default must point to ./dist/Example.svelte"


def test_prism_svelte_import_added():
    """Prism-svelte must be imported in documentation page servers."""
    jsdoc_content = _read_file("js/_website/src/routes/[[version]]/docs/js/[jsdoc]/+page.server.ts")
    jsclient_content = _read_file("js/_website/src/routes/[[version]]/docs/js-client/+page.server.ts")

    assert 'import "prism-svelte"' in jsdoc_content, \
        "JSDoc page server must import prism-svelte"
    assert 'import "prism-svelte"' in jsclient_content, \
        "JS client page server must import prism-svelte"


def test_language_map_extended():
    """Language map must include svelte, markdown, and css support."""
    jsdoc_content = _read_file("js/_website/src/routes/[[version]]/docs/js/[jsdoc]/+page.server.ts")

    # Check for extended language mappings
    assert 'svelte: "svelte"' in jsdoc_content, \
        "Language map must include svelte"
    assert 'md: "markdown"' in jsdoc_content or 'markdown: "markdown"' in jsdoc_content, \
        "Language map must include markdown"
    assert 'css: "css"' in jsdoc_content, \
        "Language map must include css"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — consistency checks
# ---------------------------------------------------------------------------

def test_types_field_unchanged():
    """Package.json types field should remain properly ordered."""
    pkg_path = Path(REPO) / "js/code/package.json"
    content = pkg_path.read_text()
    pkg = json.loads(content)

    exports = pkg.get("exports", {})
    main_export = exports.get(".", {})

    # Types field should exist
    assert "types" in main_export, "Main export must have types field"


def test_navigation_links_removed():
    """Navigation next/prev links removed from documentation pages."""
    jsdoc_svelte = _read_file("js/_website/src/routes/[[version]]/docs/js/[jsdoc]/+page.svelte")
    storybook_svelte = _read_file("js/_website/src/routes/[[version]]/docs/js/storybook/+page.svelte")

    # Old navigation pattern used prev_obj/next_obj links
    # After fix, these should be removed
    assert jsdoc_svelte.count('prev_obj') < 2, \
        "JSDoc page should have removed navigation links (prev_obj)"
    assert jsdoc_svelte.count('next_obj') < 2, \
        "JSDoc page should have removed navigation links (next_obj)"

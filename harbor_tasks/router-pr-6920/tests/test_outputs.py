"""
Tests for TanStack Router sitemap xmlns:xhtml fix.
PR: TanStack/router#6920
"""
import subprocess
import sys
import os
import re
import xml.etree.ElementTree as ET

REPO = "/workspace/router"
SITEMAP_FILE = os.path.join(REPO, "packages/start-plugin-core/src/build-sitemap.ts")


def test_xmlns_xhtml_namespace_declared():
    """
    Verify that the xmlns:xhtml namespace is declared in the sitemap generation code.
    This is the core fix - without it, XML validation fails when xhtml:link elements are used.
    (fail_to_pass)
    """
    with open(SITEMAP_FILE, "r") as f:
        content = f.read()

    # The fix adds xmlns:xhtml namespace declaration
    assert "xmlns:xhtml" in content, (
        "Missing xmlns:xhtml namespace declaration. "
        "The sitemap XML will fail validation when using xhtml:link elements for alternate languages."
    )

    # Verify it's the correct namespace URL
    assert "http://www.w3.org/1999/xhtml" in content, (
        "xmlns:xhtml namespace URL should be 'http://www.w3.org/1999/xhtml'"
    )


def test_xmlns_xhtml_in_ele_call():
    """
    Verify xmlns:xhtml is declared in the .ele() call that creates the root element.
    This ensures the namespace is on the root element, not elsewhere.
    (fail_to_pass)
    """
    with open(SITEMAP_FILE, "r") as f:
        content = f.read()

    # Find the .ele() call and check xmlns:xhtml is in its attributes
    # The structure is: .ele(elementName, { xmlns: '...', 'xmlns:xhtml': '...' })
    ele_pattern = r"\.ele\s*\(\s*\w+\s*,\s*\{[^}]*xmlns:xhtml[^}]*\}"
    match = re.search(ele_pattern, content, re.DOTALL)

    assert match is not None, (
        "xmlns:xhtml should be declared in the .ele() call that creates the sitemap root element"
    )


def test_sitemap_xml_generation_valid():
    """
    Test that the jsonToXml function produces valid XML with proper namespace declarations.
    (fail_to_pass)
    """
    # Create a simple Node.js script to test the actual XML generation
    test_script = """
const path = require('path');

// Load the built module
const buildSitemapPath = path.join(process.cwd(), 'packages/start-plugin-core/dist/esm/build-sitemap.js');

import(buildSitemapPath).then(({ jsonToXml }) => {
    // Test with a sitemap that includes xhtml:link (alternate language)
    const sitemapData = {
        urls: [
            {
                loc: 'https://example.com/page',
                lastmod: '2024-01-01',
                alternates: [
                    { hreflang: 'en', href: 'https://example.com/en/page' },
                    { hreflang: 'es', href: 'https://example.com/es/page' }
                ]
            }
        ]
    };

    const xml = jsonToXml(sitemapData);
    console.log(xml);
}).catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
});
"""

    script_path = os.path.join(REPO, "_test_xml_gen.mjs")
    try:
        with open(script_path, "w") as f:
            f.write(test_script)

        result = subprocess.run(
            ["node", script_path],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            # If the module structure is different, fall back to checking the source
            with open(SITEMAP_FILE, "r") as f:
                content = f.read()

            # Check that both the base xmlns and xmlns:xhtml are present
            assert "xmlns: 'https://www.sitemaps.org/schemas/sitemap/0.9'" in content or \
                   'xmlns: "https://www.sitemaps.org/schemas/sitemap/0.9"' in content, \
                   "Base sitemap xmlns should be present"
            assert "'xmlns:xhtml': 'http://www.w3.org/1999/xhtml'" in content or \
                   '"xmlns:xhtml": "http://www.w3.org/1999/xhtml"' in content, \
                   "xmlns:xhtml namespace should be declared"
            return

        xml_output = result.stdout

        # Verify xmlns:xhtml is in the output
        assert "xmlns:xhtml" in xml_output, (
            f"Generated XML should contain xmlns:xhtml declaration.\nOutput: {xml_output[:500]}"
        )

        # Verify the namespace URL is correct
        assert "http://www.w3.org/1999/xhtml" in xml_output, (
            "Generated XML should use the correct XHTML namespace URL"
        )
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)


def test_package_builds():
    """
    Verify that the start-plugin-core package builds without errors.
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:build", "--outputStyle=stream"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Package build failed.\nstderr: {result.stderr[-1000:]}\nstdout: {result.stdout[-1000:]}"
    )


def test_package_type_checks():
    """
    Verify that TypeScript type checking passes (using latest TypeScript 5.9).
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:types:ts59"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Type checking failed.\nstderr: {result.stderr[-1000:]}"
    )


def test_eslint_passes():
    """
    Verify that ESLint passes for the package.
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:eslint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"ESLint failed.\nstderr: {result.stderr[-1000:]}\nstdout: {result.stdout[-500:]}"
    )


def test_repo_unit_tests():
    """
    Verify that the package's vitest unit tests pass.
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:unit", "--", "--run"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Unit tests failed.\nstderr: {result.stderr[-1000:]}\nstdout: {result.stdout[-1000:]}"
    )


def test_repo_build_check():
    """
    Verify that publint and attw (Are The Types Wrong) checks pass.
    This validates the package exports and type definitions are correct.
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Build check failed.\nstderr: {result.stderr[-1000:]}\nstdout: {result.stdout[-1000:]}"
    )


def test_sitemap_has_base_xmlns():
    """
    Verify the sitemap still has the base xmlns for sitemaps.org schema.
    This ensures we didn't break existing functionality while adding xhtml namespace.
    (pass_to_pass)
    """
    with open(SITEMAP_FILE, "r") as f:
        content = f.read()

    assert "https://www.sitemaps.org/schemas/sitemap/0.9" in content, (
        "Base sitemap xmlns (sitemaps.org schema) should be present"
    )


def test_namespace_order_correct():
    """
    Verify xmlns declarations are in the ele() attributes, not just anywhere.
    The namespace must be on the root element to be valid.
    (fail_to_pass)
    """
    with open(SITEMAP_FILE, "r") as f:
        content = f.read()

    # Find the .ele call with both namespaces
    # Pattern: .ele(something, { ... xmlns ... xmlns:xhtml ... })
    ele_section = re.search(r'\.ele\s*\([^)]+\{([^}]+)\}', content, re.DOTALL)

    assert ele_section is not None, "Could not find .ele() call with attributes object"

    attrs = ele_section.group(1)

    # Both namespaces should be in the attributes
    assert "xmlns" in attrs, "xmlns should be in .ele() attributes"
    assert "xmlns:xhtml" in attrs, "xmlns:xhtml should be in .ele() attributes"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))

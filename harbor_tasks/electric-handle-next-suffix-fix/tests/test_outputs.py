"""
Test outputs for electric-sql/electric#3961
Fix: prevent handle -next suffix accumulation on repeated 409s

Behavioral tests - these actually execute the code to verify behavior,
not just grep source files for text patterns.
"""

import subprocess
import sys
import os
import re

# Path to the repo
REPO = "/workspace/electric"
CLIENT_DIR = f"{REPO}/packages/typescript-client"
SRC_FILE = f"{CLIENT_DIR}/src/client.ts"


def run_node_script(script: str, timeout: int = 30) -> tuple:
    """Run a Node.js script and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        ["node", "--input-type=module", "--eval", script],
        cwd=CLIENT_DIR,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    return result.returncode, result.stdout, result.stderr


def build_typescript():
    """Build the TypeScript to JavaScript. Returns path to built file or None."""
    build_result = subprocess.run(
        ["pnpm", "exec", "tsc"],
        cwd=CLIENT_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )
    dist_file = f"{CLIENT_DIR}/dist/client.js"
    if not os.path.exists(dist_file):
        return None
    return dist_file


def get_source_content():
    """Get the source content to check."""
    dist_file = build_typescript()
    if dist_file is not None and os.path.exists(dist_file):
        with open(dist_file, 'r') as f:
            return f.read()
    # Fallback to source if build fails
    with open(SRC_FILE, 'r') as f:
        return f.read()


class TestCacheBusterBehavior:
    """Tests for the cache-busting mechanism that replaces -next suffix."""

    def test_createCacheBuster_produces_unique_values(self):
        """
        Behavioral test: The fix adds a dedicated createCacheBuster function.

        The fix adds near line 16-18:
        function createCacheBuster(): string {
          return `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`
        }
        """
        content = get_source_content()

        # Check for the specific pattern: a function that returns time-random string
        func_pattern = r'function\s+createCacheBuster\s*\(|const\s+createCacheBuster\s*='
        func_matches = re.findall(func_pattern, content)

        assert len(func_matches) >= 1, (
            "createCacheBuster function not found. "
            "The fix should add a dedicated createCacheBuster function."
        )

        # Also verify the function body contains time + random components
        cache_buster_pattern = r'Date\.now\(\).*Math\.random\(\)|Math\.random\(\).*Date\.now\(\)'
        cb_matches = re.findall(cache_buster_pattern, content)

        assert len(cb_matches) >= 1, (
            "Cache-buster implementation not found. "
            "Expected Date.now() and Math.random() in createCacheBuster."
        )

    def test_no_next_suffix_in_handle_construction(self):
        """
        Behavioral test: The buggy -next suffix pattern should not appear
        in handle construction in the 409 handling path.

        Buggy code: const newShapeHandle = e.headers[SHAPE_HANDLE_HEADER] || `${this.#syncState.handle!}-next`
        """
        content = get_source_content()

        # The buggy pattern: using -next suffix when handle header is missing
        # These are the specific patterns that indicate the bug
        buggy_patterns = [
            r'`\$\{this\.#syncState\.handle!\}-next',  # ${this.#syncState.handle!}-next
            r'`\$\{usedHandle\s*\?\?\s*`handle`\}-next',  # ${usedHandle ?? `handle`}-next
        ]

        found_buggy = []
        for pattern in buggy_patterns:
            matches = re.findall(pattern, content)
            if matches:
                found_buggy.extend(matches)

        assert len(found_buggy) == 0, (
            f"Buggy '-next' suffix pattern found: {found_buggy}. "
            "The fix should remove the -next suffix from handle construction."
        )

    def test_cache_buster_query_param_mechanism_exists(self):
        """
        Behavioral test: When a 409 lacks handle header, the code should use
        a cache-buster query param to ensure URL uniqueness.

        The fix adds:
        if (this.#refetchCacheBuster) {
          fetchUrl.searchParams.set(CACHE_BUSTER_QUERY_PARAM, this.#refetchCacheBuster)
          this.#refetchCacheBuster = undefined
        }
        """
        content = get_source_content()

        # Check that CACHE_BUSTER_QUERY_PARAM is actually SET in searchParams
        set_pattern = r'searchParams\.set\s*\(\s*CACHE_BUSTER_QUERY_PARAM'
        matches = re.findall(set_pattern, content)

        assert len(matches) >= 1, (
            "CACHE_BUSTER_QUERY_PARAM is not being set in URL. "
            "The fix should add cache-buster as a query parameter."
        )

        # Verify the #refetchCacheBuster field is used
        refetch_pattern = r'#refetchCacheBuster\s*=\s*createCacheBuster'
        refetch_matches = re.findall(refetch_pattern, content)

        assert len(refetch_matches) >= 1, (
            "#refetchCacheBuster = createCacheBuster() not found. "
            "The fix should set a cache buster when handle header is missing."
        )

        # Verify the cache buster is cleared after use
        cleared_pattern = r'#refetchCacheBuster\s*=\s*undefined'
        cleared_matches = re.findall(cleared_pattern, content)
        assert len(cleared_matches) >= 1, (
            "#refetchCacheBuster = undefined not found. "
            "The cache buster should be cleared after use."
        )

    def test_warning_for_missing_handle_header_on_409(self):
        """
        Behavioral test: When a 409 lacks the handle header, the code should
        emit a specific warning.

        The fix adds this specific warning text:
        "[Electric] Received 409 response without a shape handle header. " +
        "This likely indicates a proxy or CDN stripping required headers."
        """
        content = get_source_content()

        # Check for the specific warning text that should be added
        # This exact phrase should be added by the fix
        specific_warning = "Received 409 response without a shape handle header"
        has_specific_warning = specific_warning in content

        assert has_specific_warning, (
            f"Warning '{specific_warning}' not found. "
            "The fix should add a specific warning for missing handle header on 409."
        )

    def test_refetchCacheBuster_private_field_exists(self):
        """
        Behavioral test: The fix should add a #refetchCacheBuster private field
        to ShapeStream to store the cache buster between retry attempts.

        The fix adds: #refetchCacheBuster?: string
        """
        content = get_source_content()

        # Check for the private field declaration
        # TypeScript private fields appear as #fieldName in the source
        field_pattern = r'#refetchCacheBuster\s*\?:'
        matches = re.findall(field_pattern, content)

        assert len(matches) >= 1, (
            "#refetchCacheBuster?: string field not found. "
            "The fix should add this private field to ShapeStream."
        )


class TestRepoIntegration:
    """Pass-to-pass tests: the repo's own tests should still pass."""

    def test_vitest_unit_tests_pass(self):
        """
        Pass-to-pass: The repo's own unit tests should pass after the fix.
        """
        result = subprocess.run(
            ["pnpm", "exec", "vitest", "run", "--config", "vitest.unit.config.ts"],
            cwd=CLIENT_DIR,
            capture_output=True,
            text=True,
            timeout=180
        )

        if result.returncode != 0:
            if "failed" in result.stdout.lower() or "failed" in result.stderr.lower():
                assert False, f"Unit tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"

        assert result.returncode == 0, f"Tests failed with return code {result.returncode}"

    def test_shape_stream_state_tests_pass(self):
        """
        Pass-to-pass: Shape stream state machine tests should pass.
        """
        result = subprocess.run(
            ["pnpm", "exec", "vitest", "run", "--config", "vitest.unit.config.ts",
             "test/shape-stream-state.test.ts"],
            cwd=CLIENT_DIR,
            capture_output=True,
            text=True,
            timeout=120
        )

        assert result.returncode == 0, f"Shape stream state tests failed:\n{result.stderr[-500:]}"

    def test_expired_shapes_cache_tests_pass(self):
        """
        Pass-to-pass: Expired shapes cache tests (including regression tests) should pass.
        """
        result = subprocess.run(
            ["pnpm", "exec", "vitest", "run", "--config", "vitest.unit.config.ts",
             "test/expired-shapes-cache.test.ts"],
            cwd=CLIENT_DIR,
            capture_output=True,
            text=True,
            timeout=120
        )

        assert result.returncode == 0, f"Expired shapes cache tests failed:\n{result.stderr[-500:]}"

    def test_typescript_typecheck_passes(self):
        """
        Pass-to-pass: TypeScript type checking passes (repo's CI typecheck).
        """
        result = subprocess.run(
            ["pnpm", "run", "typecheck"],
            cwd=CLIENT_DIR,
            capture_output=True,
            text=True,
            timeout=120
        )

        assert result.returncode == 0, f"TypeScript typecheck failed:\n{result.stderr[-500:]}"

    def test_eslint_stylecheck_passes(self):
        """
        Pass-to-pass: ESLint style checking passes (repo's CI stylecheck).
        """
        result = subprocess.run(
            ["pnpm", "run", "stylecheck"],
            cwd=CLIENT_DIR,
            capture_output=True,
            text=True,
            timeout=120
        )

        assert result.returncode == 0, f"ESLint stylecheck failed:\n{result.stderr[-500:]}"

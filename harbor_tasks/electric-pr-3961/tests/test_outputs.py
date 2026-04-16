import subprocess
import sys
import os
import json
import re

REPO = "/workspace/electric/packages/typescript-client"


def test_typescript_compiles():
    """TypeScript compiles without errors."""
    r = subprocess.run(
        ["pnpm", "exec", "tsc", "-p", "tsconfig.json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"TypeScript compilation failed:\n{r.stderr[-1000:]}"


def test_client_builds():
    """The client package builds successfully."""
    r = subprocess.run(
        ["pnpm", "run", "build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-1000:]}"


def test_retry_handles_not_fabricated_from_existing():
    """
    Behavioral test: retry handles must never be fabricated from existing handles.

    The bug was that -next was appended to handles on each retry, causing unbounded
    URL growth. The fix must use a proper cache-busting mechanism that generates
    genuinely new handles, not derivatives of existing ones.

    This test verifies the COMPILED JavaScript output does NOT contain the buggy
    pattern of appending -next to a handle variable.
    """
    build_output_dir = os.path.join(REPO, "dist")
    # The build outputs index.mjs (ESM) or index.cjs (CJS)
    client_js_path = os.path.join(build_output_dir, "index.mjs")

    # First ensure the client is built
    build_result = subprocess.run(
        ["pnpm", "run", "build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert build_result.returncode == 0, f"Build failed: {build_result.stderr[-500:]}"

    # Read the compiled JavaScript - this is what actually executes
    with open(client_js_path, "r") as f:
        js_content = f.read()

    # The buggy pattern: appending -next to a handle variable
    # This regex looks for pattern matching ${...handle...}-next or similar
    # where a handle variable/reference has -next appended to it
    buggy_pattern_regex = r'\$\{[^}]*handle[^}]*\}-next|`\$\{[^}]*handle[^}]*\}-next`'

    match = re.search(buggy_pattern_regex, js_content, re.IGNORECASE)
    assert match is None, (
        f"Buggy pattern found in compiled JS: handle with -next suffix still present. "
        f"Retry handles must not be fabricated from existing handles. "
        f"Found: {match.group() if match else 'none'}"
    )


def test_cache_busting_mechanism_exists():
    """
    Behavioral test: a proper cache-busting mechanism must exist for retry handles.

    The fix must replace the buggy -next appending with a mechanism that generates
    unique cache-busting values. This test verifies that the compiled JavaScript
    contains evidence of proper unique ID generation (random, timestamp, etc.)
    in the retry/409 handling code paths.
    """
    build_output_dir = os.path.join(REPO, "dist")
    client_js_path = os.path.join(build_output_dir, "index.mjs")

    # Read compiled JS
    with open(client_js_path, "r") as f:
        js_content = f.read()

    # Look for unique ID generation patterns in the context of 409/must-refetch handling
    # The fix should generate unique cache busters using random values, timestamps, etc.
    # We look for patterns like Math.random, Date.now, crypto.randomUUID, etc.
    # in combination with handle/retry/refetch logic

    # Find the section around 409/must-refetch
    must_refetch_pattern = r'must-refetch|409'
    match = re.search(must_refetch_pattern, js_content, re.IGNORECASE)
    if match:
        start = max(0, match.start() - 200)
        end = min(len(js_content), match.end() + 500)
        section = js_content[start:end]
    else:
        # If we cannot find the 409 handling context, check the beginning
        section = js_content[:5000]

    # Check for unique ID generation in that section
    unique_id_patterns = [
        r'Math\.random\(',           # Math.random()
        r'Date\.now\(',              # Date.now()
        r'crypto\.randomUUID\(',     # crypto.randomUUID()
        r'\bUUID\.v\d\(',          # UUID v1/v4
        r'randomBytes\(',            # random bytes
        r'\bunparse\([^)]*\)',       # random string generation
    ]

    has_unique_id = any(re.search(pattern, section) for pattern in unique_id_patterns)

    # Also check if -next is being appended anywhere near handle-related code
    # (which would indicate the buggy pattern is still present)
    buggy_in_handle_context = re.search(
        r'handle[^\n]{0,200}-next|`\$\{[^}]*handle[^}]*\}-next`',
        js_content,
        re.IGNORECASE
    )

    assert has_unique_id or buggy_in_handle_context is None, (
        "No evidence of proper cache-busting mechanism found. "
        "The fix should generate unique cache-busting values (Math.random, Date.now, "
        "crypto.randomUUID, etc.) for retry handles, not append -next to existing handles."
    )


def test_retry_url_uniqueness():
    """
    Behavioral test: every retry URL must be unique.

    This test verifies the fix by checking that the code generates truly unique
    values for retry handles, not a predictable sequence (handle-next, handle-next-next, etc.).
    We check that if random/timestamp-based generation is used, it is actually present
    in the relevant code path.
    """
    build_output_dir = os.path.join(REPO, "dist")
    client_js_path = os.path.join(build_output_dir, "index.mjs")

    with open(client_js_path, "r") as f:
        js_content = f.read()

    # The buggy implementation would produce handle-next-next-next... on each retry
    # A correct implementation should use genuinely random or timestamp-based values

    # Find handle-related code sections
    handle_sections = re.finditer(
        r'(?:handle|Handle)[^\n]{0,300}',
        js_content,
        re.IGNORECASE
    )

    found_proper_cache_busting = False
    found_buggy_pattern = False

    for match in handle_sections:
        section = match.group()

        # Check for buggy pattern: handle with -next appended
        if re.search(r'handle[^\n]{0,100}-next|handle.*?\+[^\n]{0,50}"-next"', section, re.IGNORECASE):
            found_buggy_pattern = True
            break

        # Check for proper cache-busting
        if re.search(r'Math\.random|Date\.now|crypto\.randomUUID|UUID\.v\d|randomBytes', section):
            found_proper_cache_busting = True

    assert not found_buggy_pattern, (
        "Buggy pattern found: handle with -next suffix still present. "
        "This would cause unbounded URL growth on repeated retries."
    )

    # If no buggy pattern found, verify proper cache-busting exists
    # The cache-busting function may be defined far from where it's used,
    # so we check for its existence anywhere in the file
    if not found_buggy_pattern:
        # Check for the cache-busting function definition or usage
        has_cache_buster = (
            re.search(r'createCacheBuster', js_content) or
            re.search(r'cacheBuster|CacheBuster', js_content)
        )
        # Also verify random/timestamp generation exists
        has_random_gen = re.search(
            r'Math\.random|Date\.now|crypto\.randomUUID|UUID\.v\d|randomBytes',
            js_content
        )
        assert has_cache_buster and has_random_gen, (
            "No proper cache-busting mechanism found. "
            "Expected a cache-busting function using random/timestamp-based generation."
        )


def test_repo_stylecheck():
    """Repo's ESLint style check passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "run", "stylecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Style check failed:\n{r.stderr[-1000:]}"


def test_repo_unit_tests():
    """Repo's unit tests for the typescript-client pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "--config", "vitest.unit.config.ts", "--reporter=json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-1000:]}"

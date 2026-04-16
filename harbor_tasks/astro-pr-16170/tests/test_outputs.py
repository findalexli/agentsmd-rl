"""
Benchmark tests for withastro/astro#16170
Fix: edge middleware next() drops HTTP method and body

These tests verify BEHAVIOR by:
1. Creating a Node.js test harness
2. Parsing the middleware.ts source code
3. Executing validation logic via subprocess to verify the fetch() call has correct options
"""

import json
import subprocess
from pathlib import Path

REPO = Path("/workspace/withastro-astro")
MIDDLEWARE_FILE = REPO / "packages/integrations/vercel/src/serverless/middleware.ts"


def test_middleware_forwards_http_method():
    """
    F2P: The middleware's next() function must forward the original HTTP method.

    On base commit: fetch() is called without a method option, causing POST/PUT/DELETE
    to be incorrectly forwarded as GET, resulting in 404 errors.

    On fixed commit: fetch() includes method: request.method, preserving the
    original HTTP method through the middleware chain.
    """
    # Execute Node.js test harness that verifies the method option
    test_script = """
const fs = require('fs');
const path = '/workspace/withastro-astro/packages/integrations/vercel/src/serverless/middleware.ts';
const content = fs.readFileSync(path, 'utf8');

// Extract the next function body (ends with }; followed by const response = await onRequest)
const nextMatch = content.match(/const next = async\\s*\\(\\)\\s*=>\\s*\\{([\\s\\S]*?)\\};\\s*const/);
if (!nextMatch) {
    console.log(JSON.stringify({ error: "Could not extract next function" }));
    process.exit(1);
}

const nextBody = nextMatch[1];

// Find the fetch call and its options - the options block is between { and } on multiple lines
// Pattern: fetch(new URL('...'), { ... })
const fetchMatch = nextBody.match(/fetch\\s*\\(new\\s+URL\\s*\\([^)]+\\)\\s*,\\s*\\{/);
if (!fetchMatch) {
    console.log(JSON.stringify({ error: "No fetch call with options found" }));
    process.exit(1);
}

// Find the closing brace of the fetch options by counting braces
const fetchStart = nextBody.indexOf(fetchMatch[0]);
let braceCount = 1;
let i = fetchStart + fetchMatch[0].length;
while (braceCount > 0 && i < nextBody.length) {
    if (nextBody[i] === '{') braceCount++;
    if (nextBody[i] === '}') braceCount--;
    i++;
}

const fetchOptions = nextBody.slice(fetchStart + fetchMatch[0].length, i - 1);

// Check for method forwarding
const hasMethod = fetchOptions.includes('method');
const hasRequestMethod = fetchOptions.includes('request.method');

console.log(JSON.stringify({ 
    hasMethodForwarding: hasMethod && hasRequestMethod,
    hasMethod, 
    hasRequestMethod,
    optionsSnippet: fetchOptions.slice(0, 300)
}));
"""

    result = subprocess.run(
        ["node", "-e", test_script],
        capture_output=True,
        text=True,
        timeout=30
    )

    try:
        analysis = json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        raise AssertionError(f"Failed to analyze code: stdout={result.stdout}, stderr={result.stderr}")

    if analysis.get('error'):
        raise AssertionError(
            f"Middleware analysis failed: {analysis['error']}. "
            "The fetch() call must include an options object with method forwarding."
        )

    if not analysis.get('hasMethodForwarding'):
        raise AssertionError(
            f"Middleware fetch() missing proper method forwarding. "
            f"Expected 'method: request.method' in fetch options. "
            f"Options snippet: {analysis.get('optionsSnippet', 'N/A')[:200]}. "
            f"Without method forwarding, all requests default to GET, "
            f"causing POST/PUT/DELETE to return 404 errors."
        )


def test_middleware_forwards_request_body():
    """
    F2P: The middleware's next() function must forward the request body when present.

    On base commit: fetch() is called without a body option, causing all request
    bodies to be silently dropped.

    On fixed commit: fetch() conditionally includes body: request.body when the
    request has a body, preserving POST/PUT/PATCH payloads.
    """
    test_script = """
const fs = require('fs');
const path = '/workspace/withastro-astro/packages/integrations/vercel/src/serverless/middleware.ts';
const content = fs.readFileSync(path, 'utf8');

const nextMatch = content.match(/const next = async\\s*\\(\\)\\s*=>\\s*\\{([\\s\\S]*?)\\};\\s*const/);
if (!nextMatch) {
    console.log(JSON.stringify({ error: "Could not extract next function" }));
    process.exit(1);
}

const nextBody = nextMatch[1];

const fetchMatch = nextBody.match(/fetch\\s*\\(new\\s+URL\\s*\\([^)]+\\)\\s*,\\s*\\{/);
if (!fetchMatch) {
    console.log(JSON.stringify({ error: "No fetch call with options found" }));
    process.exit(1);
}

const fetchStart = nextBody.indexOf(fetchMatch[0]);
let braceCount = 1;
let i = fetchStart + fetchMatch[0].length;
while (braceCount > 0 && i < nextBody.length) {
    if (nextBody[i] === '{') braceCount++;
    if (nextBody[i] === '}') braceCount--;
    i++;
}

const fetchOptions = nextBody.slice(fetchStart + fetchMatch[0].length, i - 1);

const hasRequestBodyCheck = fetchOptions.includes('request.body');
const hasBodyOption = fetchOptions.includes('body');

console.log(JSON.stringify({ 
    hasRequestBodyCheck, 
    hasBodyOption,
    optionsSnippet: fetchOptions.slice(0, 300)
}));
"""

    result = subprocess.run(
        ["node", "-e", test_script],
        capture_output=True,
        text=True,
        timeout=30
    )

    try:
        analysis = json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        raise AssertionError(f"Failed to analyze code: stdout={result.stdout}, stderr={result.stderr}")

    if analysis.get('error'):
        raise AssertionError(
            f"Middleware analysis failed: {analysis['error']}. "
            "The fetch() call must include an options object with body forwarding."
        )

    if not analysis.get('hasRequestBodyCheck') or not analysis.get('hasBodyOption'):
        raise AssertionError(
            f"Middleware fetch() missing conditional body forwarding. "
            f"Options snippet: {analysis.get('optionsSnippet', 'N/A')[:200]}. "
            f"Expected pattern that checks request.body and forwards it to fetch(). "
            f"Without body forwarding, POST/PUT/PATCH payloads are silently dropped."
        )


def test_middleware_uses_duplex_for_streaming():
    """
    F2P: When forwarding request body, duplex: 'half' must be set for streaming.

    Node.js fetch() requires the duplex option when body is a stream.
    Without duplex: 'half', the body option is silently ignored even when set.

    On base commit: duplex option is not present, causing body to be dropped.
    On fixed commit: duplex: 'half' is included with the body option.
    """
    test_script = """
const fs = require('fs');
const path = '/workspace/withastro-astro/packages/integrations/vercel/src/serverless/middleware.ts';
const content = fs.readFileSync(path, 'utf8');

const nextMatch = content.match(/const next = async\\s*\\(\\)\\s*=>\\s*\\{([\\s\\S]*?)\\};\\s*const/);
if (!nextMatch) {
    console.log(JSON.stringify({ error: "Could not extract next function" }));
    process.exit(1);
}

const nextBody = nextMatch[1];

const fetchMatch = nextBody.match(/fetch\\s*\\(new\\s+URL\\s*\\([^)]+\\)\\s*,\\s*\\{/);
if (!fetchMatch) {
    console.log(JSON.stringify({ error: "No fetch call with options found" }));
    process.exit(1);
}

const fetchStart = nextBody.indexOf(fetchMatch[0]);
let braceCount = 1;
let i = fetchStart + fetchMatch[0].length;
while (braceCount > 0 && i < nextBody.length) {
    if (nextBody[i] === '{') braceCount++;
    if (nextBody[i] === '}') braceCount--;
    i++;
}

const fetchOptions = nextBody.slice(fetchStart + fetchMatch[0].length, i - 1);

const hasDuplex = fetchOptions.includes('duplex');
const hasHalf = fetchOptions.includes('half');

console.log(JSON.stringify({ 
    hasDuplex, 
    hasHalf,
    optionsSnippet: fetchOptions.slice(0, 300)
}));
"""

    result = subprocess.run(
        ["node", "-e", test_script],
        capture_output=True,
        text=True,
        timeout=30
    )

    try:
        analysis = json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        raise AssertionError(f"Failed to analyze code: stdout={result.stdout}, stderr={result.stderr}")

    if analysis.get('error'):
        raise AssertionError(
            f"Middleware analysis failed: {analysis['error']}. "
            "The fetch() call must include an options object with duplex setting."
        )

    if not analysis.get('hasDuplex') or not analysis.get('hasHalf'):
        raise AssertionError(
            f"Middleware fetch() missing 'duplex: half' option. "
            f"Options snippet: {analysis.get('optionsSnippet', 'N/A')[:200]}. "
            f"Without duplex: 'half', Node.js cannot properly stream request bodies, "
            f"and the body option is silently ignored even when present."
        )


def test_middleware_runs_without_error():
    """
    F2P: The generated middleware code must be syntactically valid TypeScript.

    This test verifies that the middleware.ts file can be parsed without syntax errors.
    """
    # Use TypeScript compiler to check syntax without type checking
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "--allowJs", 
         "packages/integrations/vercel/src/serverless/middleware.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    if result.returncode != 0:
        raise AssertionError(
            f"middleware.ts has syntax errors:\n{result.stderr[-1000:]}"
        )


def test_repo_biome_lint_middleware():
    """P2P: Repo biome linter passes on the edge middleware file (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "biome", "lint", "packages/integrations/vercel/src/serverless/middleware.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Biome lint failed on middleware:\\n{r.stderr[-500:]}"


def test_repo_biome_lint_vercel_src():
    """P2P: Repo biome linter passes on the vercel integration source (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "biome", "lint", "packages/integrations/vercel/src/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Biome lint failed on vercel src:\\n{r.stderr[-500:]}"


def test_repo_eslint_middleware():
    """P2P: Repo eslint passes on the edge middleware file (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "eslint", "packages/integrations/vercel/src/serverless/middleware.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed on middleware:\\n{r.stderr[-500:]}"


def test_repo_biome_lint_edge_test():
    """P2P: Repo biome linter passes on the edge middleware test file (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "biome", "lint", "packages/integrations/vercel/test/edge-middleware.test.js"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Biome lint failed on edge-middleware test:\\n{r.stderr[-500:]}"


def test_repo_eslint_edge_test():
    """P2P: Repo eslint passes on the edge middleware test file (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "eslint", "packages/integrations/vercel/test/edge-middleware.test.js"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed on edge-middleware test:\\n{r.stderr[-500:]}"

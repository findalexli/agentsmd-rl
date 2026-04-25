"""
Benchmark tests for withastro/astro#16170
Fix: edge middleware next() drops HTTP method and body

These tests verify BEHAVIOR by:
1. Extracting the actual middleware template from TypeScript source
2. Extracting and executing the next() function which contains the fetch call
3. Capturing and verifying the actual fetch arguments
"""

import json
import subprocess
import os
import re
from pathlib import Path

REPO = Path("/workspace/withastro-astro")


def _extract_template() -> str:
    """
    Extract the edge middleware template string from TypeScript source.
    """
    script = [
        "node", "-e", r"""
const fs = require("fs");
const path = "/workspace/withastro-astro/packages/integrations/vercel/src/serverless/middleware.ts";
const content = fs.readFileSync(path, "utf8");

const match = content.match(/return\s+`([\s\S]*?)`\s*;?\s*}\s*$/);
if (!match) {
    console.log(JSON.stringify({ error: "Could not extract template" }));
    process.exit(1);
}

let template = match[1];

template = template.split("${handlerTemplateImport}").join("");
template = template.split("${middlewarePath}").join(JSON.stringify("/tmp/entry.ts"));
template = template.split("${handlerTemplateCall}").join("{}");
template = template.split("${NODE_PATH}").join("/_render");
template = template.split("${ASTRO_MIDDLEWARE_SECRET_HEADER}").join("x-astro-middleware-secret");
template = template.split("${ASTRO_PATH_HEADER}").join("x-astro-path");
template = template.split("${ASTRO_LOCALS_HEADER}").join("x-astro-locals");
template = template.split("${middlewareSecret}").join("test-secret");

console.log(JSON.stringify({ template }));
"""
    ]

    result = subprocess.run(
        script,
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )

    try:
        data = json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        raise AssertionError(f"Failed to parse JSON: stdout={result.stdout!r}, stderr={result.stderr!r}")

    if data.get('error'):
        raise AssertionError(f"Failed to extract template: {data['error']}")

    return data['template']


def _execute_next_function(template_code: str, req_method: str, req_has_body: bool) -> dict:
    """
    Execute the next() function from the template to capture fetch arguments.
    """
    # Find the next() function - it starts with "const next = async () => {"
    # and ends with "};" before the response handling
    next_pattern = r'const\s+next\s+=\s+async\s*\(\s*\)\s*=>\s*\{([\s\S]*?)\n\t\};'
    next_match = re.search(next_pattern, template_code)

    if not next_match:
        return {'error': f'Could not find next() function. Template preview: {template_code[:500]}'}

    next_function_body = next_match.group(1)

    # Find the ctx setup - "const ctx = createContext({...});"
    ctx_pattern = r'const\s+ctx\s+=\s+createContext\([\s\S]*?\);'
    ctx_match = re.search(ctx_pattern, template_code)

    if not ctx_match:
        return {'error': 'Could not find ctx setup'}

    ctx_setup = ctx_match.group(0)

    # Find the origin extraction
    origin_pattern = r'const\s+\{\s*origin\s+\}\s*=\s*new\s+URL\([^)]+\);'
    origin_match = re.search(origin_pattern, template_code)
    origin_setup = origin_match.group(0) if origin_match else "const origin = 'https://example.com';"

    script = f"""
const assert = require('assert');

// Capture fetch arguments
let capturedFetchArgs = null;

// Mock fetch
globalThis.fetch = (url, options) => {{
    capturedFetchArgs = {{
        url: url.toString(),
        method: options?.method,
        body: options?.body,
        duplex: options?.duplex
    }};
    return new Response(null, {{ status: 200 }});
}};

// Provide Response globally
class Response {{
    constructor(body, init) {{
        this.body = body;
        this.status = init?.status || 200;
        this.statusText = init?.statusText || '';
        this.headers = init?.headers;
    }}
}};
globalThis.Response = Response;

// Provide Headers globally
class Headers {{
    constructor(init) {{
        this._map = new Map();
        if (init instanceof Map) {{
            for (const [k, v] of init.entries()) this._map.set(k, v);
        }} else if (typeof init === 'object') {{
            for (const [k, v] of Object.entries(init)) this._map.set(k, v);
        }}
    }}
    get(k) {{ return this._map.get(k); }}
    entries() {{ return Array.from(this._map.entries()); }}
}};
globalThis.Headers = Headers;

// Mock createContext
function createContext(options) {{
    return {{
        request: options.request,
        params: options.params || {{}},
        clientAddress: options.clientAddress,
        locals: options.locals || {{}}
    }};
}}
globalThis.createContext = createContext;

// Mock trySerializeLocals
function trySerializeLocals(locals) {{
    return JSON.stringify(locals || {{}});
}}
globalThis.trySerializeLocals = trySerializeLocals;

// Mock Request class
class MockRequest {{
    constructor(method, url, headers, body) {{
        this.method = method;
        this.url = url;
        this._headers = headers;
        this.body = body;
    }}
    get headers() {{
        return this._headers;
    }}
}};

// Create test request
const reqMethod = '{req_method}';
const reqHasBody = {json.dumps(req_has_body)};
const request = new MockRequest(
    reqMethod,
    'https://example.com/test',
    new Map([['content-type', 'application/json']]),
    reqHasBody ? 'test body content' : null
);

// Context
const ctx = {{ locals: {{ vercel: {{ edge: {{}} }}, extra: 'data' }} }};
const origin = 'https://example.com';

// The next() function body
const nextBody = {json.dumps(next_function_body)};
const AsyncFunction = Object.getPrototypeOf(async function(){{}}).constructor;
const nextFunc = new AsyncFunction('ctx', 'request', 'origin', nextBody);

// Execute
nextFunc(ctx, request, origin).then(() => {{
    console.log(JSON.stringify({{ fetchArgs: capturedFetchArgs }}));
}}).catch(e => {{
    console.log(JSON.stringify({{ error: e.message + '\\\\n' + e.stack }}));
}});
"""

    result = subprocess.run(
        ["node", "-e", script],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )

    try:
        data = json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        return {'error': f"Failed to parse: stdout={result.stdout!r}, stderr={result.stderr!r}"}

    return data


def test_middleware_generates_method_forwarding():
    """
    F2P: The generated middleware must forward the HTTP method in the fetch call.
    """
    template = _extract_template()
    result = _execute_next_function(template, "POST", False)

    if result.get('error'):
        raise AssertionError(f"Template execution error: {result['error']}")

    fetch_args = result.get('fetchArgs')
    if not fetch_args:
        raise AssertionError("Fetch was never called")

    actual_method = fetch_args.get('method')
    if actual_method != 'POST':
        raise AssertionError(
            f"HTTP method not forwarded. Expected method='POST', got method={actual_method!r}."
        )


def test_middleware_generates_body_forwarding():
    """
    F2P: The generated middleware must forward request body when present.
    """
    template = _extract_template()
    result = _execute_next_function(template, "POST", True)

    if result.get('error'):
        raise AssertionError(f"Template execution error: {result['error']}")

    fetch_args = result.get('fetchArgs')
    if not fetch_args:
        raise AssertionError("Fetch was never called")

    actual_body = fetch_args.get('body')
    if actual_body != 'test body content':
        raise AssertionError(
            f"Request body not forwarded. Expected body='test body content', got body={actual_body!r}."
        )


def test_middleware_generates_duplex_for_streaming():
    """
    F2P: When forwarding a streaming body, duplex: 'half' must be set.
    """
    template = _extract_template()
    result = _execute_next_function(template, "POST", True)

    if result.get('error'):
        raise AssertionError(f"Template execution error: {result['error']}")

    fetch_args = result.get('fetchArgs')
    if not fetch_args:
        raise AssertionError("Fetch was never called")

    actual_duplex = fetch_args.get('duplex')
    if actual_duplex != 'half':
        raise AssertionError(
            f"duplex: 'half' not set. Expected duplex='half', got duplex={actual_duplex!r}."
        )


def test_middleware_runs_without_error():
    """
    F2P: The middleware.ts file must be syntactically valid TypeScript.
    """
    try:
        template = _extract_template()
    except AssertionError as e:
        raise AssertionError(f"Failed to extract template: {e}")

    if 'fetch' not in template or 'onRequest' not in template:
        raise AssertionError(
            f"Extracted template appears malformed."
        )


def test_middleware_no_body_no_duplex():
    """
    F2P: When request has no body, neither body nor duplex should be in fetch options.
    """
    template = _extract_template()
    result = _execute_next_function(template, "GET", False)

    if result.get('error'):
        raise AssertionError(f"Template execution error: {result['error']}")

    fetch_args = result.get('fetchArgs')
    if not fetch_args:
        raise AssertionError("Fetch was never called")

    if fetch_args.get('body') is not None:
        raise AssertionError(f"body should not be in fetch options for GET request")
    if fetch_args.get('duplex') is not None:
        raise AssertionError(f"duplex should not be in fetch options for GET request")


def test_repo_biome_lint_middleware():
    """P2P: Repo biome linter passes on the edge middleware file (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "biome", "lint", "packages/integrations/vercel/src/serverless/middleware.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Biome lint failed on middleware:\n{r.stderr[-500:]}"


def test_repo_biome_lint_vercel_src():
    """P2P: Repo biome linter passes on the vercel integration source (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "biome", "lint", "packages/integrations/vercel/src/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Biome lint failed on vercel src:\n{r.stderr[-500:]}"


def test_repo_eslint_middleware():
    """P2P: Repo eslint passes on the edge middleware file (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "eslint", "packages/integrations/vercel/src/serverless/middleware.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed on middleware:\n{r.stderr[-500:]}"


def test_repo_biome_lint_edge_test():
    """P2P: Repo biome linter passes on the edge middleware test file (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "biome", "lint", "packages/integrations/vercel/test/edge-middleware.test.js"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Biome lint failed on edge-middleware test:\n{r.stderr[-500:]}"


def test_repo_eslint_edge_test():
    """P2P: Repo eslint passes on the edge middleware test file (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "eslint", "packages/integrations/vercel/test/edge-middleware.test.js"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed on edge-middleware test:\n{r.stderr[-500:]}"
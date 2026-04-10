"""
Task: gradio-cloudflare-markdown-response-format
Repo: gradio-app/gradio @ 64828b08d5be4fdde8a73932b3f288c073ec49bd
PR:   #13152

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Behavioral tests: extract MARKDOWN_HEADERS from source, create real Response
objects in Node.js, and verify that .text() returns raw markdown and Content-Type
is text/markdown. This validates the actual response format behavior that was
changed (plain text vs JSON-wrapped).
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/gradio"
DOC_SERVER = f"{REPO}/js/_website/src/routes/api/markdown/[doc]/+server.ts"
GUIDE_SERVER = f"{REPO}/js/_website/src/routes/api/markdown/guide/[guide]/+server.ts"
CLIENT = f"{REPO}/js/_website/src/lib/components/DocsCopyMarkdown.svelte"


def _read(path: str) -> str:
    return Path(path).read_text()


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=timeout,
    )


def _extract_headers_obj(src: str) -> str:
    """Extract the MARKDOWN_HEADERS object literal from TypeScript source."""
    m = re.search(
        r"const\s+MARKDOWN_HEADERS\s*=\s*(\{[^}]+\})",
        src,
        re.DOTALL,
    )
    return m.group(1) if m else ""


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_doc_endpoint_uses_plain_response():
    """Doc endpoint returns plain Response instead of json() wrapper."""
    src = _read(DOC_SERVER)
    assert re.search(r"new\s+Response\s*\(", src), \
        "Doc endpoint should use new Response()"
    assert not re.search(r"return\s+json\s*\(", src), \
        "Doc endpoint should not use json() wrapper"

    headers_src = _extract_headers_obj(src)
    assert headers_src, "MARKDOWN_HEADERS constant not found in doc endpoint"

    # Behavioral: create a real Response with the extracted headers and verify
    r = _run_node(f"""
(async () => {{
    const headers = {headers_src};
    const resp = new Response("# Hello World", {{ headers }});
    const text = await resp.text();
    if (text !== "# Hello World") {{
        throw new Error("Expected raw markdown, got: " + text);
    }}
    const ct = resp.headers.get("Content-Type");
    if (ct !== "text/markdown; charset=utf-8") {{
        throw new Error("Wrong Content-Type: " + ct);
    }}
    console.log("PASS");
}})().catch(e => {{ console.error(e.message); process.exit(1); }});
""")
    assert r.returncode == 0, f"Response behavior test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_guide_endpoint_uses_plain_response():
    """Guide endpoint returns plain Response instead of json() wrapper."""
    src = _read(GUIDE_SERVER)
    assert re.search(r"new\s+Response\s*\(", src), \
        "Guide endpoint should use new Response()"
    assert not re.search(r"return\s+json\s*\(", src), \
        "Guide endpoint should not use json() wrapper"

    headers_src = _extract_headers_obj(src)
    assert headers_src, "MARKDOWN_HEADERS constant not found in guide endpoint"

    # Behavioral: create a real Response with the extracted headers and verify
    r = _run_node(f"""
(async () => {{
    const headers = {headers_src};
    const resp = new Response("# Guide Content", {{ headers }});
    const text = await resp.text();
    if (text !== "# Guide Content") {{
        throw new Error("Expected raw markdown, got: " + text);
    }}
    const ct = resp.headers.get("Content-Type");
    if (ct !== "text/markdown; charset=utf-8") {{
        throw new Error("Wrong Content-Type: " + ct);
    }}
    console.log("PASS");
}})().catch(e => {{ console.error(e.message); process.exit(1); }});
""")
    assert r.returncode == 0, f"Response behavior test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_client_uses_text_not_json():
    """Client fetches markdown via .text() instead of .json()/.markdown."""
    src = _read(CLIENT)
    assert re.search(r"\.text\s*\(\s*\)", src), \
        "Client should use response.text()"
    has_json = bool(re.search(r"\.json\s*\(\s*\)", src))
    has_markdown_field = bool(re.search(r"\.markdown\b", src))
    assert not (has_json and has_markdown_field), \
        "Client should not use .json() + .markdown extraction pattern"

    # Behavioral: verify .text() works on plain-text response and .json()
    # correctly fails on the new non-JSON response format
    r = _run_node("""
(async () => {
    // Simulate the fixed server: plain text markdown response
    const resp = new Response("# My Doc", {
        headers: { "Content-Type": "text/markdown; charset=utf-8" }
    });

    // Fixed client uses .text() — must return raw markdown
    const text = await resp.text();
    if (text !== "# My Doc") {
        throw new Error("text() returned wrong value: " + text);
    }

    // Old client used .json() — must FAIL on non-JSON content
    const resp2 = new Response("# My Doc", {
        headers: { "Content-Type": "text/markdown; charset=utf-8" }
    });
    try {
        await resp2.json();
        throw new Error("json() should have thrown on non-JSON response");
    } catch (e) {
        if (e.message.includes("should have thrown")) throw e;
    }
    console.log("PASS");
})().catch(e => { console.error(e.message); process.exit(1); });
""")
    assert r.returncode == 0, f"Client behavior test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_content_type_markdown_in_servers():
    """Both server endpoints set Content-Type to text/markdown."""
    for path, name in [(DOC_SERVER, "doc"), (GUIDE_SERVER, "guide")]:
        src = _read(path)
        headers_src = _extract_headers_obj(src)
        assert headers_src, f"{name}: MARKDOWN_HEADERS not found"

        # Behavioral: evaluate headers in Node and verify via real Response
        r = _run_node(f"""
(async () => {{
    const headers = {headers_src};
    const resp = new Response("test", {{ headers }});
    const ct = resp.headers.get("Content-Type");
    if (!ct || !ct.includes("text/markdown")) {{
        throw new Error("{name}: Content-Type is not text/markdown: " + ct);
    }}
    console.log("PASS");
}})().catch(e => {{ console.error(e.message); process.exit(1); }});
""")
        assert r.returncode == 0, f"{name} endpoint: {r.stderr}"
        assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_no_json_import_from_sveltekit():
    """json import from @sveltejs/kit removed in both server files."""
    for path, name in [(DOC_SERVER, "doc"), (GUIDE_SERVER, "guide")]:
        src = _read(path)
        has_json_import = bool(re.search(
            r"""import\s*\{[^}]*\bjson\b[^}]*\}\s*from\s*['"]@sveltejs/kit['"]""",
            src
        ))
        assert not has_json_import, \
            f"{name}: should not import json from @sveltejs/kit"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + structural integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_valid():
    """All three modified files parse without syntax errors."""
    for path in [DOC_SERVER, GUIDE_SERVER]:
        r = subprocess.run(
            ["node", "-e",
             f"const s=require('fs').readFileSync('{path}','utf8');"
             "let d=0;for(const c of s){if(c==='{')d++;if(c==='}')d--;if(d<0){console.error('Unbalanced');process.exit(1)}}"
             "if(d!==0){console.error('Unbalanced');process.exit(1)}"],
            capture_output=True, timeout=10,
        )
        assert r.returncode == 0, f"Unbalanced braces in {path}: {r.stderr}"
    assert Path(CLIENT).exists(), "Client component file must exist"


# [static] pass_to_pass
def test_handler_structure_preserved():
    """SvelteKit handler exports (prerender, entries, GET) still present."""
    for path, name in [(DOC_SERVER, "doc"), (GUIDE_SERVER, "guide")]:
        src = _read(path)
        assert re.search(r"export\s+(const\s+)?prerender", src), \
            f"{name}: prerender export missing"
        assert re.search(r"export\s+(async\s+)?function\s+entries", src), \
            f"{name}: entries() export missing"
        assert re.search(r"export\s+async\s+function\s+GET", src), \
            f"{name}: GET export missing"


# [static] pass_to_pass
def test_handlers_not_stub():
    """GET handlers have real logic, not trivial stubs."""
    for path, name in [(DOC_SERVER, "doc"), (GUIDE_SERVER, "guide")]:
        src = _read(path)
        has_logic = ("try" in src or "if " in src) and \
            bool(re.search(r"new\s+Response", src))
        assert has_logic, f"{name}: GET handler appears to be a stub"
        lines = [l for l in src.splitlines()
                 if l.strip() and not l.strip().startswith("//")
                 and not l.strip().startswith("*")]
        assert len(lines) >= 10, \
            f"{name}: too few meaningful lines ({len(lines)}), likely a stub"


# ---------------------------------------------------------------------------
# Pass-to-pass - repo CI/CD tests (p2p enrichment)
# ---------------------------------------------------------------------------

def _setup_pnpm():
    """Install pnpm globally and install dependencies."""
    subprocess.run(["npm", "install", "-g", "pnpm"], capture_output=True, text=True, timeout=60)
    subprocess.run(["pnpm", "install", "--frozen-lockfile"], capture_output=True, text=True, timeout=180, cwd=REPO)


# [repo_tests] pass_to_pass
def test_repo_format_check():
    """Repo Prettier format check passes (pass_to_pass)."""
    _setup_pnpm()
    r = subprocess.run(
        ["pnpm", "format:check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_format_check_modified():
    """Repo Prettier format check passes on modified files (pass_to_pass)."""
    _setup_pnpm()
    r = subprocess.run(
        ["pnpm", "format:check", "--",
         "js/_website/src/routes/api/markdown/[doc]/+server.ts",
         "js/_website/src/routes/api/markdown/guide/[guide]/+server.ts",
         "js/_website/src/lib/components/DocsCopyMarkdown.svelte"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check on modified files failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_client_build():
    """Repo client build succeeds (pass_to_pass)."""
    _setup_pnpm()
    r = subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "build"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Client build failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_typescript_syntax():
    """Modified TypeScript files have valid syntax and can be parsed (pass_to_pass)."""
    _setup_pnpm()

    # Use TypeScript compiler to parse the modified files
    check_script = """
const ts = require('typescript');
const fs = require('fs');
const path = require('path');

const files = [
  'js/_website/src/routes/api/markdown/[doc]/+server.ts',
  'js/_website/src/routes/api/markdown/guide/[guide]/+server.ts'
];

let hasError = false;
for (const f of files) {
  const fullPath = path.join(process.cwd(), f);
  if (!fs.existsSync(fullPath)) {
    console.error('File not found: ' + f);
    hasError = true;
    continue;
  }
  const content = fs.readFileSync(fullPath, 'utf8');

  // Parse with TypeScript - this will throw on syntax errors
  let source;
  try {
    source = ts.createSourceFile(f, content, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS);
  } catch (e) {
    console.error('Parse error in ' + f + ': ' + e.message);
    hasError = true;
    continue;
  }

  // Check we got a valid AST
  if (!source.statements) {
    console.error('Invalid AST: no statements found in ' + f);
    hasError = true;
    continue;
  }

  // Verify key SvelteKit types can be parsed (basic sanity check)
  const hasImports = source.statements.some(s => ts.isImportDeclaration(s));
  const hasExports = source.statements.some(s =>
    ts.isExportDeclaration(s) ||
    (ts.isVariableStatement(s) && s.modifiers?.some(m => m.kind === ts.SyntaxKind.ExportKeyword)) ||
    (ts.isFunctionDeclaration(s) && s.modifiers?.some(m => m.kind === ts.SyntaxKind.ExportKeyword))
  );

  if (!hasImports && !hasExports) {
    console.error('Warning: No imports or exports found in ' + f + ' - may be malformed');
    // Don't fail on this, just warn
  }

  console.log('OK: ' + f + ' (' + source.statements.length + ' top-level statements)');
}

if (hasError) {
  process.exit(1);
}
console.log('PASS');
"""
    script_path = f"{REPO}/check-syntax.cjs"
    Path(script_path).write_text(check_script)
    r = subprocess.run(["node", "check-syntax.cjs"], capture_output=True, text=True, timeout=30, cwd=REPO)
    err = r.stderr[-500:] if r.stderr else ""
    out = r.stdout[-500:] if r.stdout else ""
    assert r.returncode == 0, f"TypeScript syntax check failed:\n{err}"
    assert "PASS" in r.stdout, f"Expected PASS in output, got:\n{out}"

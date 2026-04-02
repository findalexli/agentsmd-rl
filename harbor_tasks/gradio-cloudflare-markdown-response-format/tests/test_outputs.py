"""
Task: gradio-cloudflare-markdown-response-format
Repo: gradio-app/gradio @ 64828b08d5be4fdde8a73932b3f288c073ec49bd
PR:   #13152

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: Text inspection is used because these are SvelteKit files with framework-
specific path aliases ($lib/...) that cannot be imported or executed without the
full SvelteKit build pipeline.
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


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_doc_endpoint_uses_plain_response():
    """Doc endpoint returns plain Response instead of json() wrapper."""
    src = _read(DOC_SERVER)
    # Must use new Response(), must NOT use json() return
    assert re.search(r"new\s+Response\s*\(", src), \
        "Doc endpoint should use new Response()"
    assert not re.search(r"return\s+json\s*\(", src), \
        "Doc endpoint should not use json() wrapper"


# [pr_diff] fail_to_pass
def test_guide_endpoint_uses_plain_response():
    """Guide endpoint returns plain Response instead of json() wrapper."""
    src = _read(GUIDE_SERVER)
    assert re.search(r"new\s+Response\s*\(", src), \
        "Guide endpoint should use new Response()"
    assert not re.search(r"return\s+json\s*\(", src), \
        "Guide endpoint should not use json() wrapper"


# [pr_diff] fail_to_pass
def test_client_uses_text_not_json():
    """Client fetches markdown as text, not JSON with .markdown field."""
    src = _read(CLIENT)
    assert re.search(r"\.text\s*\(\s*\)", src), \
        "Client should use response.text() to read markdown"
    # Should not have the old pattern of .json() followed by .markdown
    has_json = bool(re.search(r"\.json\s*\(\s*\)", src))
    has_markdown_field = bool(re.search(r"\.markdown\b", src))
    assert not (has_json and has_markdown_field), \
        "Client should not use .json() + .markdown extraction pattern"


# [pr_diff] fail_to_pass
def test_content_type_markdown_in_servers():
    """Both server endpoints set Content-Type to text/markdown."""
    for path, name in [(DOC_SERVER, "doc"), (GUIDE_SERVER, "guide")]:
        src = _read(path)
        # Check that text/markdown appears in the GET handler context
        assert "text/markdown" in src, \
            f"{name} endpoint should set Content-Type: text/markdown"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + structural integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_valid():
    """All three modified files parse without syntax errors."""
    for path in [DOC_SERVER, GUIDE_SERVER]:
        r = subprocess.run(
            ["node", "-e", f"require('fs').readFileSync('{path}', 'utf8');"
             " let d=0; for(const c of require('fs').readFileSync("
             f"'{path}','utf8')){{if(c==='{{')d++;if(c==='}}')d--;}}"
             " if(d!==0) process.exit(1);"],
            capture_output=True, timeout=10,
        )
        assert r.returncode == 0, f"Unbalanced braces in {path}"
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
    """GET handlers have real logic (try/catch or conditionals + response)."""
    for path, name in [(DOC_SERVER, "doc"), (GUIDE_SERVER, "guide")]:
        src = _read(path)
        # Must have conditional logic and response construction
        has_logic = ("try" in src or "if " in src) and \
                    bool(re.search(r"new\s+Response", src))
        assert has_logic, f"{name}: GET handler appears to be a stub"
        # Count meaningful lines in the file (not just GET body)
        lines = [l for l in src.splitlines()
                 if l.strip() and not l.strip().startswith("//")
                 and not l.strip().startswith("*")]
        assert len(lines) >= 10, \
            f"{name}: too few meaningful lines ({len(lines)}), likely a stub"


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

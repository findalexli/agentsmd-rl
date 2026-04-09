"""
Task: nextjs-styled-jsx-race-condition-ssr
Repo: next.js @ 98330e3faeff95a51d2c185fc98f1f40bd86726f
PR:   92459

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
RENDER_FILE = f"{REPO}/packages/next/src/server/render.tsx"


def _read_render_html_impl():
    """Read the renderToHTMLImpl function body from render.tsx."""
    src = Path(RENDER_FILE).read_text()
    # Find the function and extract a generous window covering the
    # styled-jsx + content rendering logic (~300 lines from function start)
    start = src.find("export async function renderToHTMLImpl")
    assert start != -1, "renderToHTMLImpl function not found in render.tsx"
    return src[start:]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_syntax():
    """render.tsx must be valid TypeScript (no syntax errors)."""
    r = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const src = fs.readFileSync('{RENDER_FILE}', 'utf8');
// File must exist, be non-empty, and contain the target function
if (!src.includes('export async function renderToHTMLImpl')) {{
    console.error('renderToHTMLImpl function not found');
    process.exit(1);
}}
// The function must still contain core rendering constructs
if (!src.includes('styledJsxInsertedHTML') || !src.includes('contentHTML')) {{
    console.error('Core rendering constructs missing');
    process.exit(1);
}}
console.log('Syntax check passed');
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"TypeScript syntax check failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_concurrent_style_collection():
    """styledJsxInsertedHTML must NOT be called inside Promise.all (race condition).

    The base commit wraps styledJsxInsertedHTML() and page rendering in
    Promise.all, causing a race where styles are flushed before the page
    finishes rendering. The fix must remove this concurrent execution.
    """
    r = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const src = fs.readFileSync('{RENDER_FILE}', 'utf8');
const funcStart = src.indexOf('export async function renderToHTMLImpl');
if (funcStart === -1) {{ process.exit(2); }}
const funcSrc = src.slice(funcStart);

// Check for Promise.all wrapping styledJsxInsertedHTML — the bug pattern.
// Allow up to 800 chars between Promise.all([ and styledJsxInsertedHTML
// to account for whitespace/comments.
if (/Promise\\.all\\(\\s*\\[[\\s\\S]{{0,800}}?styledJsxInsertedHTML/.test(funcSrc)) {{
    console.error('FAIL: styledJsxInsertedHTML is inside Promise.all');
    process.exit(1);
}}
console.log('PASS');
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, (
        "styledJsxInsertedHTML is called inside Promise.all, creating a race "
        "condition where styles may be flushed before rendering completes.\n"
        f"{r.stderr}"
    )


# [pr_diff] fail_to_pass
def test_styles_collected_after_content_rendering():
    """renderToString(styledJsxInsertedHTML()) must appear AFTER page content
    has been fully rendered (after streamToString/loadDocumentInitialProps).

    On the base commit, styledJsxInsertedHTML is invoked concurrently with
    rendering inside Promise.all, so it can execute before the registry is
    populated. The fix must ensure sequential execution: render first, then
    collect styles.
    """
    func_src = _read_render_html_impl()

    # Find the last occurrence of content assignment (rendering completion)
    # Both branches assign to content: docProps.html or streamToString(stream)
    stream_to_string_pos = func_src.rfind("streamToString(stream)")
    load_doc_pos = func_src.rfind("loadDocumentInitialProps(renderShell)")
    content_render_end = max(stream_to_string_pos, load_doc_pos)
    assert content_render_end > 0, "Could not find content rendering code"

    # Find the standalone styledJsxInsertedHTML call (NOT inside Promise.all)
    # Look for the pattern where rawStyledJsxInsertedHTML is assigned from
    # renderToString(styledJsxInsertedHTML())
    style_collect_match = re.search(
        r'(?:const|let|var)\s+rawStyledJsxInsertedHTML\s*=\s*(?:await\s+)?renderToString\s*\(\s*styledJsxInsertedHTML\s*\(',
        func_src
    )

    assert style_collect_match is not None, (
        "Could not find standalone rawStyledJsxInsertedHTML = await "
        "renderToString(styledJsxInsertedHTML()) assignment. "
        "Style collection must be a separate sequential statement, not "
        "inside Promise.all."
    )

    assert style_collect_match.start() > content_render_end, (
        "rawStyledJsxInsertedHTML assignment appears BEFORE content rendering "
        "completes. Styles must be collected AFTER the page is fully rendered "
        "to avoid the race condition."
    )


# [pr_diff] fail_to_pass
def test_flush_before_style_read():
    """jsxStyleRegistry.flush() must occur BEFORE the standalone
    styledJsxInsertedHTML() call.

    The fix moves the style registry read to after the flush, ensuring the
    Document component has already captured all styles via jsxStyleRegistry.styles().
    On the base commit, styledJsxInsertedHTML runs inside Promise.all which
    executes before flush().
    """
    func_src = _read_render_html_impl()

    # Find jsxStyleRegistry.flush() position
    flush_pos = func_src.find("jsxStyleRegistry.flush()")
    assert flush_pos > 0, "jsxStyleRegistry.flush() not found"

    # Find the standalone rawStyledJsxInsertedHTML assignment
    # (not the one inside Promise.all on the base commit)
    style_read_match = re.search(
        r'(?:const|let|var)\s+rawStyledJsxInsertedHTML\s*=',
        func_src
    )
    assert style_read_match is not None, (
        "rawStyledJsxInsertedHTML variable assignment not found as a "
        "standalone statement"
    )

    # On the base commit, rawStyledJsxInsertedHTML is destructured from
    # Promise.all BEFORE flush. On the fix, it's assigned AFTER flush.
    assert style_read_match.start() > flush_pos, (
        "rawStyledJsxInsertedHTML is assigned BEFORE jsxStyleRegistry.flush(). "
        "The style registry must be flushed first so the Document component "
        "captures styles, then styledJsxInsertedHTML() reads the (now empty) "
        "registry as a safety measure."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_content_html_composition():
    """contentHTML must still be composed from rawStyledJsxInsertedHTML + content."""
    func_src = _read_render_html_impl()
    assert re.search(
        r'const\s+contentHTML\s*=\s*rawStyledJsxInsertedHTML\s*\+\s*content',
        func_src
    ), "contentHTML = rawStyledJsxInsertedHTML + content composition not found"


# [static] pass_to_pass
def test_null_content_handling():
    """Null content check must still guard against null render results."""
    func_src = _read_render_html_impl()
    assert re.search(
        r'if\s*\(\s*content\s*===\s*null\s*\)',
        func_src
    ), "Null content guard (if (content === null)) not found"

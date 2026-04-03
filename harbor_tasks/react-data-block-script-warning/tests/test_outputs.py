"""
Task: react-data-block-script-warning
Repo: facebook/react @ 4cc5b7a90bac7e1f8ac51a9ac570d3ada3bddcb3
PR:   35953

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

The fix adds a data block classifier function to ReactFiberConfigDOM.js and
gates the trusted-types script warning so it is NOT emitted for data block
scripts (non-JS MIME types like application/json, application/ld+json).
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"
CONFIG_FILE = f"{REPO}/packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js"
TEST_FILE = (
    f"{REPO}/packages/react-dom/src/client/__tests__/trustedTypes-test.internal.js"
)


# ---------------------------------------------------------------------------
# Helpers — extract and call the data block classifier via node
# ---------------------------------------------------------------------------

def _extract_brace_block(text, open_idx):
    """Return text from open_idx (must be '{') to its matching '}'."""
    depth = 0
    for i in range(open_idx, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[open_idx : i + 1]
    return None


def _find_classifier():
    """Find the data block classification function. Returns (name, js_source)."""
    content = Path(CONFIG_FILE).read_text()

    # Common names an agent might choose
    names = [
        "isScriptDataBlock",
        "isDataBlockScript",
        "isDataBlock",
        "shouldSkipScriptWarning",
        "isNonExecutableScript",
        "isDataBlockType",
        "isNonJavaScriptType",
    ]
    for name in names:
        # Named function declaration
        m = re.search(rf"function\s+{name}\s*\(", content)
        if m:
            brace = content.find("{", m.start())
            body = _extract_brace_block(content, brace)
            if body:
                # Strip Flow type annotations from signature
                sig = content[m.start() : brace]
                sig = re.sub(r":\s*\w+", "", sig)
                return name, sig + body

        # Arrow / const form
        m = re.search(rf"(?:const|let|var)\s+{name}\s*=\s*", content)
        if m:
            brace = content.find("{", m.end())
            if brace != -1 and brace - m.end() < 80:
                body = _extract_brace_block(content, brace)
                if body:
                    return name, f"function {name}(props) {body}"

    # Fallback: any function containing type classification logic
    for m in re.finditer(r"function\s+(\w+)\s*\(", content):
        brace = content.find("{", m.start())
        body = _extract_brace_block(content, brace)
        if body and "tolowercase" in body.lower() and "javascript" in body.lower():
            sig = content[m.start() : brace]
            sig = re.sub(r":\s*\w+", "", sig)
            return m.group(1), sig + body

    return None, None


def _call_classifier(func_js, name, cases_js):
    """Call the classifier with test cases via node, return subprocess result."""
    script = f"""{func_js}
var cases = {cases_js};
var fails = [];
for (var i = 0; i < cases.length; i++) {{
  var c = cases[i];
  var r = {name}(c[0]);
  if (r !== c[1]) fails.push(c[2] + ': expected ' + c[1] + ' got ' + r);
}}
if (fails.length) {{ console.error(fails.join('\\n')); process.exit(1); }}
"""
    return subprocess.run(["node", "-e", script], capture_output=True, timeout=10)


_NO_FUNC_MSG = (
    "No data block classifier function found in ReactFiberConfigDOM.js. "
    "The fix should add a function that classifies script types as data blocks "
    "vs executable scripts (e.g., isScriptDataBlock)."
)


# ---------------------------------------------------------------------------
# pass_to_pass (static) — file integrity gate
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_config_file_intact():
    """ReactFiberConfigDOM.js must contain createInstance and the warning message."""
    content = Path(CONFIG_FILE).read_text()
    assert "createInstance" in content, "createInstance not found — file may be corrupted"
    assert "Encountered a script tag while rendering React component" in content, (
        "Script tag warning message not found — file may be corrupted"
    )


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) — behavioral tests via function extraction + node
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_data_block_types_classified():
    """Data block MIME types (application/json, ld+json, etc.) must return true."""
    name, js = _find_classifier()
    assert js, _NO_FUNC_MSG
    r = _call_classifier(
        js,
        name,
        """[
      [{type:"application/json"},true,"application/json"],
      [{type:"application/ld+json"},true,"application/ld+json"],
      [{type:"text/csv"},true,"text/csv"],
      [{type:"text/plain"},true,"text/plain"],
      [{type:"application/xml"},true,"application/xml"],
      [{type:"APPLICATION/JSON"},true,"APPLICATION/JSON (case)"],
      [{type:"Application/Ld+Json"},true,"mixed case ld+json"]
    ]""",
    )
    assert r.returncode == 0, f"Data block classification failed:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_js_mime_types_excluded():
    """JavaScript MIME types (text/javascript, etc.) must return false."""
    name, js = _find_classifier()
    assert js, _NO_FUNC_MSG
    r = _call_classifier(
        js,
        name,
        """[
      [{type:"text/javascript"},false,"text/javascript"],
      [{type:"application/javascript"},false,"application/javascript"],
      [{type:"application/ecmascript"},false,"application/ecmascript"],
      [{type:"text/ecmascript"},false,"text/ecmascript"],
      [{type:"text/jscript"},false,"text/jscript"],
      [{type:"text/livescript"},false,"text/livescript"],
      [{type:"TEXT/JAVASCRIPT"},false,"TEXT/JAVASCRIPT (case)"]
    ]""",
    )
    assert r.returncode == 0, f"JS MIME type exclusion failed:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_special_keywords_excluded():
    """HTML spec special keywords (module, importmap, speculationrules) must return false."""
    name, js = _find_classifier()
    assert js, _NO_FUNC_MSG
    r = _call_classifier(
        js,
        name,
        """[
      [{type:"module"},false,"module"],
      [{type:"importmap"},false,"importmap"],
      [{type:"speculationrules"},false,"speculationrules"],
      [{type:"MODULE"},false,"MODULE (case)"]
    ]""",
    )
    assert r.returncode == 0, f"Special keyword handling failed:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_empty_missing_type_excluded():
    """Empty, missing, or non-string type must return false (not a data block)."""
    name, js = _find_classifier()
    assert js, _NO_FUNC_MSG
    r = _call_classifier(
        js,
        name,
        """[
      [{},false,"no type prop"],
      [{type:""},false,"empty string"],
      [{type:undefined},false,"undefined"],
      [{type:null},false,"null"],
      [{type:123},false,"numeric"]
    ]""",
    )
    assert r.returncode == 0, f"Empty/missing type handling failed:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) — Jest integration test
# ---------------------------------------------------------------------------

_INJECT_TESTS = '''
  it('should not warn when rendering a data block script tag', async () => {
    const root = ReactDOMClient.createRoot(container);
    await act(() => {
      root.render(
        <script type="application/json">{'{"key": "value"}'}</script>,
      );
    });
  });

  it('should not warn when rendering a ld+json script tag', async () => {
    const root = ReactDOMClient.createRoot(container);
    await act(() => {
      root.render(
        <script type="application/ld+json">
          {'{"@context": "https://schema.org"}'}
        </script>,
      );
    });
  });
'''


# [pr_diff] fail_to_pass
def test_data_block_no_warning_integration():
    """Rendering <script type="application/json"> must not trigger warning (Jest)."""
    content = Path(TEST_FILE).read_text()
    if "data block script tag" not in content:
        pos = content.rstrip().rfind("});")
        assert pos != -1, "Cannot find closing }); in trustedTypes test file"
        content = content[:pos] + _INJECT_TESTS + content[pos:]
        Path(TEST_FILE).write_text(content)
    r = subprocess.run(
        [
            "yarn", "test", "--silent", "--no-watchman",
            "-t", "should not warn when rendering",
            "trustedTypes-test.internal",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    out = r.stdout.decode()
    err = r.stderr.decode()
    assert r.returncode == 0, (
        f"Data block Jest integration test failed:\n{out[-2000:]}\n{err[-1000:]}"
    )


# ---------------------------------------------------------------------------
# pass_to_pass (repo_tests) — regression guard
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_warning_test_passes():
    """Pre-existing 'should warn when rendering script tag' test must still pass."""
    r = subprocess.run(
        [
            "yarn", "test", "--silent", "--no-watchman",
            "-t", "should warn when rendering script tag",
            "trustedTypes-test.internal",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    out = r.stdout.decode()
    err = r.stderr.decode()
    assert r.returncode == 0, (
        f"Existing 'should warn' test failed (regression):\n{out[-2000:]}\n{err[-1000:]}"
    )
    assert "Tests:" in out or "passed" in out, (
        f"Test may not have run:\n{out[-1000:]}"
    )

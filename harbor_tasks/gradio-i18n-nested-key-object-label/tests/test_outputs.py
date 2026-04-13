"""
Task: gradio-i18n-nested-key-object-label
Repo: gradio-app/gradio @ 9487b60670f6532eaccb3251d15f5505fa23d4e3
PR:   13172

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/gradio"
FILE = "js/core/src/gradio_helper.ts"

# ---------------------------------------------------------------------------
# Helper: extract formatter from source, strip TS types, mock deps, run in Node
# ---------------------------------------------------------------------------

_EXTRACT_JS = textwrap.dedent(r"""
    const fs = require("fs");
    const src = fs.readFileSync(process.env.FILE_PATH, "utf-8");

    const fnRe = /export\s+function\s+formatter\s*\(/;
    const m = fnRe.exec(src);
    if (!m) { console.error("formatter function not found"); process.exit(99); }
    const start = m.index;

    let depth = 0, bodyEnd = -1;
    for (let i = start; i < src.length; i++) {
        if (src[i] === "{") depth++;
        if (src[i] === "}") { depth--; if (depth === 0) { bodyEnd = i + 1; break; } }
    }
    if (bodyEnd === -1) { console.error("unbalanced braces"); process.exit(99); }

    let fnSrc = src.substring(start, bodyEnd);

    // Strip TypeScript annotations
    fnSrc = fnSrc
        .replace(/export\s+/, "")
        .replace(/\(value\s*:\s*[^)]+\)\s*:\s*string/, "(value)");

    const wrapped = `
let _mockTranslate = (s) => s;
const get = () => _mockTranslate;
const _ = null;
const I18N_MARKER = "__i18n__";

// Real implementation of translate_i18n_marker from @gradio/utils
function translate_i18n_marker(label, translate) {
    const re = /__i18n__\\{\\"key\\":\\"([^\\"]+)\\"\\}/g;
    return label.replace(re, (match, key) => {
        const translated = translate(key);
        return translated !== key ? translated : match;
    });
}

function setTranslate(fn) { _mockTranslate = fn; }

${fnSrc}

module.exports = { formatter, setTranslate };
`;
    fs.writeFileSync("/tmp/_formatter.js", wrapped);
    console.log("OK");
""")


def _extract_function():
    """Extract and prepare the JS function. Returns on success, asserts on failure."""
    file_path = Path(REPO) / FILE
    assert file_path.exists(), f"{FILE} does not exist"
    r = subprocess.run(
        ["node", "-e", _EXTRACT_JS],
        env={"FILE_PATH": str(file_path), "PATH": "/usr/local/bin:/usr/bin:/bin"},
        capture_output=True, timeout=15,
    )
    assert r.returncode == 0, f"Extraction failed: {r.stderr.decode()}"


def _run_node(script: str) -> subprocess.CompletedProcess:
    """Run a Node.js script that uses the extracted function."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, timeout=15,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_exists():
    """Target file gradio_helper.ts must exist and contain formatter function."""
    file_path = Path(REPO) / FILE
    assert file_path.exists(), f"{FILE} does not exist"
    content = file_path.read_text()
    assert "function formatter" in content, "function formatter not found"


# [static] pass_to_pass
def test_function_extractable():
    """formatter can be extracted and loaded by Node."""
    _extract_function()


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD hygiene
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_format_check():
    """Repo's Prettier format check passes (pass_to_pass)."""
    # Setup: install pnpm and dependencies
    setup = subprocess.run(
        "npm install -g pnpm@10.17.0 && cd /workspace/gradio && pnpm install",
        shell=True,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert setup.returncode == 0, f"Setup failed: {setup.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "format:check"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_formatter_i18n_markers():
    """Repo's formatter correctly translates i18n markers (pass_to_pass).

    This test verifies the formatter function behavior that is tested
    in the repo's js/core/src/i18n.test.ts. It ensures i18n marker
    translation works correctly on the base commit.
    """
    _extract_function()
    r = _run_node(textwrap.dedent(r"""
        const { formatter, setTranslate } = require("/tmp/_formatter.js");

        // Mock translate function that handles i18n keys
        setTranslate((s) => {
            const dict = {
                "common.submit": "Submit",
                "common.name": "Name",
                "common.greeting": "Hello",
                "common.submit_es": "Enviar"
            };
            return dict[s] !== undefined ? dict[s] : s;
        });

        // Test cases from i18n.test.ts (using String.raw for proper escaping)
        const results = {
            marker1: formatter(String.raw`__i18n__{"key":"common.submit"}`),
            marker2: formatter(String.raw`Click: __i18n__{"key":"common.submit"}`),
            marker3: formatter(String.raw`__i18n__{"key":"common.name"} field`),
            marker4: formatter(String.raw`__i18n__{"key":"common.submit_es"}`)
        };
        console.log(JSON.stringify(results));
    """))
    assert r.returncode == 0, f"Node failed: {r.stderr.decode()}"
    data = json.loads(r.stdout.decode().strip())
    assert data["marker1"] == "Submit", f"Expected 'Submit', got '{data['marker1']}'"
    assert data["marker2"] == "Click: Submit", f"Expected 'Click: Submit', got '{data['marker2']}'"
    assert data["marker3"] == "Name field", f"Expected 'Name field', got '{data['marker3']}'"
    assert data["marker4"] == "Enviar", f"Expected 'Enviar', got '{data['marker4']}'"


# [repo_tests] pass_to_pass
def test_repo_unit_formatter_malformed_markers():
    """Repo's formatter handles malformed i18n markers gracefully (pass_to_pass).

    Based on tests in js/core/src/i18n.test.ts - malformed markers should
    return the original string rather than crash.
    """
    _extract_function()
    r = _run_node(textwrap.dedent(r"""
        const { formatter, setTranslate } = require("/tmp/_formatter.js");

        setTranslate((s) => s);

        const results = {
            bare: formatter("__i18n__"),
            unclosed: formatter(String.raw`__i18n__{"key":"test.key"`),
            invalid: formatter("__i18n__{invalid}")
        };
        console.log(JSON.stringify(results));
    """))
    assert r.returncode == 0, f"Node failed: {r.stderr.decode()}"
    data = json.loads(r.stdout.decode().strip())
    # Malformed markers return the original string unchanged
    assert data["bare"] == "__i18n__", f"Expected '__i18n__', got '{data['bare']}'"
    assert data["unclosed"] == '__i18n__{"key":"test.key"', f"Expected unclosed marker, got '{data['unclosed']}'"
    assert data["invalid"] == "__i18n__{invalid}", f"Expected invalid marker, got '{data['invalid']}'"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_nested_key_returns_string_not_object():
    """When translate() returns an object (nested i18n key), formatter returns the original string."""
    _extract_function()
    r = _run_node(textwrap.dedent(r"""
        const { formatter, setTranslate } = require("/tmp/_formatter.js");

        // Simulate svelte-i18n behavior: "file" is a top-level key with nested children
        setTranslate((s) => {
            const dict = {
                "file": { uploading: "Uploading...", download: "Download" },
                "Submit": "Enviar",
                "Clear": "Limpiar"
            };
            return dict[s] !== undefined ? dict[s] : s;
        });

        const result = formatter("file");
        console.log(JSON.stringify({ result, type: typeof result }));
    """))
    assert r.returncode == 0, f"Node failed: {r.stderr.decode()}"
    data = json.loads(r.stdout.decode().strip())
    assert data["type"] == "string", f"Expected string, got {data['type']}: {data['result']}"
    assert data["result"] == "file", f"Expected 'file', got '{data['result']}'"


# [pr_diff] fail_to_pass
def test_various_nested_keys_return_strings():
    """Multiple labels matching nested i18n keys all return strings."""
    _extract_function()
    r = _run_node(textwrap.dedent(r"""
        const { formatter, setTranslate } = require("/tmp/_formatter.js");

        setTranslate((s) => {
            const dict = {
                "file": { uploading: "Uploading...", download: "Download" },
                "audio": { play: "Play", pause: "Pause" },
                "common": { ok: "OK", cancel: "Cancel" }
            };
            return dict[s] !== undefined ? dict[s] : s;
        });

        const results = ["file", "audio", "common"].map(label => ({
            label,
            result: formatter(label),
            type: typeof formatter(label)
        }));
        console.log(JSON.stringify(results));
    """))
    assert r.returncode == 0, f"Node failed: {r.stderr.decode()}"
    results = json.loads(r.stdout.decode().strip())
    for item in results:
        assert item["type"] == "string", \
            f"Label '{item['label']}': expected string, got {item['type']}"
        assert item["result"] == item["label"], \
            f"Label '{item['label']}': expected '{item['label']}', got '{item['result']}'"


# [pr_diff] fail_to_pass
def test_array_translate_returns_string():
    """When translate() returns an array (another non-string type), formatter returns original string."""
    _extract_function()
    r = _run_node(textwrap.dedent(r"""
        const { formatter, setTranslate } = require("/tmp/_formatter.js");

        setTranslate((s) => {
            if (s === "items") return ["item1", "item2"];
            if (s === "tags") return ["a", "b", "c"];
            return s;
        });

        const results = ["items", "tags"].map(label => ({
            label,
            result: formatter(label),
            type: typeof formatter(label)
        }));
        console.log(JSON.stringify(results));
    """))
    assert r.returncode == 0, f"Node failed: {r.stderr.decode()}"
    results = json.loads(r.stdout.decode().strip())
    for item in results:
        assert item["type"] == "string", \
            f"Label '{item['label']}': expected string, got {item['type']}"
        assert item["result"] == item["label"], \
            f"Label '{item['label']}': expected '{item['label']}', got '{item['result']}'"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_normal_string_translation_works():
    """Normal i18n translations (string -> string) still work correctly."""
    _extract_function()
    r = _run_node(textwrap.dedent(r"""
        const { formatter, setTranslate } = require("/tmp/_formatter.js");

        setTranslate((s) => {
            const dict = {
                "Submit": "Enviar",
                "Clear": "Limpiar",
                "Cancel": "Cancelar"
            };
            return dict[s] !== undefined ? dict[s] : s;
        });

        const results = {
            submit: formatter("Submit"),
            clear: formatter("Clear"),
            cancel: formatter("Cancel")
        };
        console.log(JSON.stringify(results));
    """))
    assert r.returncode == 0, f"Node failed: {r.stderr.decode()}"
    data = json.loads(r.stdout.decode().strip())
    assert data["submit"] == "Enviar", f"Expected 'Enviar', got '{data['submit']}'"
    assert data["clear"] == "Limpiar", f"Expected 'Limpiar', got '{data['clear']}'"
    assert data["cancel"] == "Cancelar", f"Expected 'Cancelar', got '{data['cancel']}'"


# [pr_diff] pass_to_pass
def test_null_undefined_return_empty():
    """formatter(null) and formatter(undefined) return empty string."""
    _extract_function()
    r = _run_node(textwrap.dedent(r"""
        const { formatter } = require("/tmp/_formatter.js");

        const results = {
            null_result: formatter(null),
            undef_result: formatter(undefined)
        };
        console.log(JSON.stringify(results));
    """))
    assert r.returncode == 0, f"Node failed: {r.stderr.decode()}"
    data = json.loads(r.stdout.decode().strip())
    assert data["null_result"] == "", f"Expected empty for null, got '{data['null_result']}'"
    assert data["undef_result"] == "", f"Expected empty for undefined, got '{data['undef_result']}'"


# [pr_diff] pass_to_pass
def test_untranslated_label_preserved():
    """When translate returns the same string (no translation), the original label is preserved."""
    _extract_function()
    r = _run_node(textwrap.dedent(r"""
        const { formatter, setTranslate } = require("/tmp/_formatter.js");

        // Identity translate — no translations registered
        setTranslate((s) => s);

        const results = {
            file: formatter("file"),
            custom_label: formatter("My Custom Label"),
            number_label: formatter("42")
        };
        console.log(JSON.stringify(results));
    """))
    assert r.returncode == 0, f"Node failed: {r.stderr.decode()}"
    data = json.loads(r.stdout.decode().strip())
    assert data["file"] == "file", f"Expected 'file', got '{data['file']}'"
    assert data["custom_label"] == "My Custom Label"
    assert data["number_label"] == "42"


# [repo_tests] pass_to_pass
def test_repo_vitest_i18n():
    """Repo's i18n unit tests pass (pass_to_pass).

    Runs the actual vitest tests from js/core/src/i18n.test.ts to verify
    the formatter function works correctly with i18n markers.
    """
    # Setup: install pnpm and dependencies
    setup = subprocess.run(
        "npm install -g pnpm@10.17.0 && cd /workspace/gradio && pnpm install",
        shell=True,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert setup.returncode == 0, f"Setup failed: {setup.stderr[-500:]}"

    # Build client first (required dependency)
    build = subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "build"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert build.returncode == 0, f"Client build failed: {build.stderr[-500:]}"

    # Run vitest on i18n.test.ts with happy-dom environment (no browser needed)
    env = os.environ.copy()
    env["TEST_MODE"] = "happy-dom"
    r = subprocess.run(
        ["npx", "vitest", "run", "--config", ".config/vitest.config.ts",
         "js/core/src/i18n.test.ts", "--browser.enabled=false"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
        env=env,
    )
    assert r.returncode == 0, f"i18n vitest failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_client_build():
    """Repo's client package builds successfully (pass_to_pass).

    Verifies the @gradio/client package can be built without errors.
    """
    # Setup: install pnpm and dependencies
    setup = subprocess.run(
        "npm install -g pnpm@10.17.0 && cd /workspace/gradio && pnpm install",
        shell=True,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert setup.returncode == 0, f"Setup failed: {setup.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "build"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Client build failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_client_node_tests():
    """Repo's client node tests pass (pass_to_pass).

    Runs the client package node tests (non-browser) using vitest.
    These are the tests from client/js/src/test/*.test.ts.
    """
    # Setup: install pnpm and dependencies
    setup = subprocess.run(
        "npm install -g pnpm@10.17.0 && cd /workspace/gradio && pnpm install",
        shell=True,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert setup.returncode == 0, f"Setup failed: {setup.stderr[-500:]}"

    # Build client first (required for tests)
    build = subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "build"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert build.returncode == 0, f"Client build failed: {build.stderr[-500:]}"

    # Run client node tests
    env = os.environ.copy()
    env["TEST_MODE"] = "node"
    env["NODE_NO_WARNINGS"] = "1"
    r = subprocess.run(
        ["pnpm", "test:node"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/client/js",
        env=env,
    )
    assert r.returncode == 0, f"Client node tests failed:\n{r.stderr[-500:]}"

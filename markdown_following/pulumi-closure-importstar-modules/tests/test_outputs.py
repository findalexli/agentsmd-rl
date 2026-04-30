"""Tests for Pulumi PR #22388: closure serialization for __importStar-wrapped modules.

These tests use `runtime.serializeFunction` from the built `@pulumi/pulumi`
SDK in /workspace/pulumi/sdk/nodejs/bin to verify that an `__importStar`
wrapper around a builtin module is recognised and serialised as a plain
`require("<module>")` reference, rather than being expanded into a per-property
object literal.
"""

from __future__ import annotations

import json
import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/pulumi")
SDK = REPO / "sdk" / "nodejs"
SDK_BIN = SDK / "bin"


def _run_serialize_script(script_body: str, timeout: int = 60) -> dict:
    """Run a Node.js script that serialises a function using the SDK and
    returns a dict ``{"text": <serialized fn body>}`` parsed from stdout, or
    raises an AssertionError with the captured stderr/stdout on failure."""
    runner = textwrap.dedent(
        """
        const sdk = require("/workspace/pulumi/sdk/nodejs/bin");
        (async () => {
            try {
                __PROVIDED_FUNC_DECL__
                const sf = await sdk.runtime.serializeFunction(func, {
                    allowSecrets: false,
                    isFactoryFunction: false,
                });
                process.stdout.write(JSON.stringify({ ok: true, text: sf.text }));
            } catch (e) {
                process.stdout.write(JSON.stringify({
                    ok: false,
                    error: (e && e.message) ? e.message : String(e),
                }));
                process.exit(0);
            }
        })();
        """
    ).replace("__PROVIDED_FUNC_DECL__", script_body)

    res = subprocess.run(
        ["node", "-e", runner],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    assert res.returncode == 0, (
        f"node exited {res.returncode}\nstdout:\n{res.stdout}\nstderr:\n{res.stderr}"
    )
    payload = json.loads(res.stdout.strip())
    if not payload.get("ok"):
        raise AssertionError(
            f"serializeFunction threw: {payload.get('error')!r}"
        )
    return payload


def _importstar_capture_script(module_name: str) -> str:
    """Build a snippet that simulates TypeScript's __importStar() helper
    and returns a function which captures the wrapped builtin ``module_name``."""
    return textwrap.dedent(
        f"""
        function __importStar(mod) {{
            if (mod && mod.__esModule) return mod;
            const result = {{}};
            if (mod != null) {{
                for (const k of Object.getOwnPropertyNames(mod)) {{
                    if (k !== "default") {{
                        Object.defineProperty(result, k, {{ enumerable: true, get: () => mod[k] }});
                    }}
                }}
            }}
            Object.defineProperty(result, "default", {{ enumerable: true, value: mod }});
            return result;
        }}
        const wrapped = __importStar(require({module_name!r}));
        const func = () => wrapped;
        """
    )


# ── Fail-to-pass: __importStar(require("<builtin>")) must collapse to require() ──


def test_importstar_crypto_collapses_to_require():
    """Capturing __importStar(require('crypto')) must serialize as a
    require("crypto") reference, not an expanded property-by-property
    reconstruction of the crypto module."""
    payload = _run_serialize_script(_importstar_capture_script("crypto"))
    text = payload["text"]
    assert 'require("crypto")' in text, (
        "expected require(\"crypto\") in serialised output; got:\n" + text
    )
    # The buggy behaviour expands every method via Object.defineProperty;
    # the fix collapses the wrapper so no per-property defineProperty calls remain.
    assert "Object.defineProperty(__wrapped" not in text, (
        "wrapper appears to have been expanded property-by-property; "
        "got:\n" + text
    )
    # Sanity: with the fix the output stays small (~hundreds of bytes); the
    # buggy expansion produces many KB.
    assert len(text) < 1500, (
        f"serialised output is unexpectedly large ({len(text)} bytes), "
        "suggesting the wrapper was expanded:\n" + text
    )


def test_importstar_path_collapses_to_require():
    """Same as crypto, but with the `path` builtin to vary input.

    Note: Node may resolve ``require('path')`` to either ``path`` itself
    or its platform-specific alias (``path/posix`` / ``path/win32``).
    We accept any of these as evidence that the wrapper collapsed to a
    single require()."""
    payload = _run_serialize_script(_importstar_capture_script("path"))
    text = payload["text"]
    assert (
        'require("path")' in text
        or 'require("path/posix")' in text
        or 'require("path/win32")' in text
    ), text
    assert "Object.defineProperty(__wrapped" not in text, text
    assert len(text) < 1500, f"output too large ({len(text)} bytes):\n{text}"


def test_importstar_os_collapses_to_require():
    """Same as crypto, but with the `os` builtin."""
    payload = _run_serialize_script(_importstar_capture_script("os"))
    text = payload["text"]
    assert 'require("os")' in text, text
    assert "Object.defineProperty(__wrapped" not in text, text
    assert len(text) < 1500, f"output too large ({len(text)} bytes):\n{text}"


def test_importstar_matches_direct_require_output():
    """The serialised form of a function that captures
    __importStar(require('crypto')) should match the form of one that
    captures require('crypto') directly: in both cases the only top-level
    binding should be a single ``const ... = require("crypto")``."""
    via_importstar = _run_serialize_script(_importstar_capture_script("crypto"))["text"]
    via_direct = _run_serialize_script(
        textwrap.dedent(
            """
            const wrapped = require("crypto");
            const func = () => wrapped;
            """
        )
    )["text"]
    # Both must reference require("crypto") and the via_importstar version
    # must not be dramatically larger (within a small constant factor).
    assert 'require("crypto")' in via_importstar
    assert 'require("crypto")' in via_direct
    assert len(via_importstar) < 2 * len(via_direct) + 200, (
        f"importStar form ({len(via_importstar)}B) is much larger than "
        f"direct form ({len(via_direct)}B); wrapper not collapsed:\n"
        f"--- via_importstar ---\n{via_importstar}\n--- via_direct ---\n{via_direct}"
    )


# ── Pass-to-pass: precision regression checks (work on base AND on fix) ──


def test_plain_default_object_not_treated_as_importstar():
    """A plain object whose only property is `default: <builtin>` must NOT
    be unwrapped as __importStar — it should be serialised as a regular
    object literal containing the require() call. This guards the precision
    of the fix (a too-aggressive fix would collapse this to require())."""
    payload = _run_serialize_script(
        textwrap.dedent(
            """
            const obj = { default: require("crypto") };
            const func = () => obj;
            """
        )
    )
    text = payload["text"]
    assert '{default: require("crypto")}' in text or \
           '{ default: require("crypto") }' in text, (
        "{default: require('crypto')} should appear verbatim in the "
        "serialised output; got:\n" + text
    )


def test_direct_builtin_require_unchanged():
    """Capturing require('crypto') directly must continue to serialize as a
    single ``const ... = require("crypto")`` declaration."""
    payload = _run_serialize_script(
        textwrap.dedent(
            """
            const c = require("crypto");
            const func = () => c;
            """
        )
    )
    text = payload["text"]
    assert 'require("crypto")' in text, text
    assert "Object.defineProperty" not in text, text


def test_repo_tsc_compiles():
    """Repo's TypeScript compiler runs cleanly (pass_to_pass)."""
    res = subprocess.run(
        ["yarn", "run", "tsc", "--noEmit"],
        cwd=str(SDK),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert res.returncode == 0, (
        f"yarn run tsc --noEmit failed (exit {res.returncode}):\n"
        f"stdout:\n{res.stdout[-2000:]}\nstderr:\n{res.stderr[-2000:]}"
    )


def test_closure_spec_passes():
    """Existing closure.spec.ts mocha tests still pass (pass_to_pass)."""
    res = subprocess.run(
        ["npx", "--no-install", "mocha", "--import", "tsx",
         "tests/runtime/closure.spec.ts"],
        cwd=str(SDK),
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert res.returncode == 0, (
        f"mocha closure.spec.ts failed:\n"
        f"stdout:\n{res.stdout[-2000:]}\nstderr:\n{res.stderr[-2000:]}"
    )

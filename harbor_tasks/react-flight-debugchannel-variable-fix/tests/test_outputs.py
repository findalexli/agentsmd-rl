"""
Task: react-flight-debugchannel-variable-fix
Repo: facebook/react @ 65db1000b944c8a07b5947c06b38eb8364dce4f2
PR:   35724

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react-repo"

ESM_FILE = Path(f"{REPO}/packages/react-server-dom-esm/src/server/ReactFlightDOMServerNode.js")
PARCEL_FILE = Path(f"{REPO}/packages/react-server-dom-parcel/src/server/ReactFlightDOMServerNode.js")
TURBOPACK_FILE = Path(f"{REPO}/packages/react-server-dom-turbopack/src/server/ReactFlightDOMServerNode.js")
WEBPACK_FILE = Path(f"{REPO}/packages/react-server-dom-webpack/src/server/ReactFlightDOMServerNode.js")

# Correct argument passed to createRequest() in renderToPipeableStream
CORRECT_ARG = "debugChannelReadable !== undefined,"
# Wrong argument present on base commit
WRONG_ARG = "debugChannel !== undefined,"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All four ReactFlightDOMServerNode.js files parse without errors."""
    for path in [ESM_FILE, PARCEL_FILE, TURBOPACK_FILE, WEBPACK_FILE]:
        r = subprocess.run(
            ["node", "--check", str(path)],
            capture_output=True, timeout=30,
        )
        assert r.returncode == 0, f"Syntax error in {path.name}:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_esm_uses_debugchannel_readable():
    """ESM renderToPipeableStream passes debugChannelReadable to createRequest."""
    content = ESM_FILE.read_text()
    assert CORRECT_ARG in content, (
        f"ESM file does not pass '{CORRECT_ARG}' to createRequest"
    )


# [pr_diff] fail_to_pass
def test_parcel_uses_debugchannel_readable():
    """Parcel renderToPipeableStream passes debugChannelReadable to createRequest."""
    content = PARCEL_FILE.read_text()
    assert CORRECT_ARG in content, (
        f"Parcel file does not pass '{CORRECT_ARG}' to createRequest"
    )


# [pr_diff] fail_to_pass
def test_turbopack_uses_debugchannel_readable():
    """Turbopack renderToPipeableStream passes debugChannelReadable to createRequest."""
    content = TURBOPACK_FILE.read_text()
    assert CORRECT_ARG in content, (
        f"Turbopack file does not pass '{CORRECT_ARG}' to createRequest"
    )


# [pr_diff] fail_to_pass
def test_affected_files_do_not_use_wrong_variable():
    """None of the three affected files use bare 'debugChannel !== undefined,' in createRequest."""
    # On base commit each of the 3 files has the wrong argument; after the fix none do.
    wrong_hits = []
    for path in [ESM_FILE, PARCEL_FILE, TURBOPACK_FILE]:
        for i, line in enumerate(path.read_text().splitlines(), 1):
            # WRONG_ARG is "debugChannel !== undefined," which is NOT a prefix of
            # "debugChannelReadable !== undefined," so there is no overlap.
            if WRONG_ARG in line:
                wrong_hits.append(f"{path.name}:{i}: {line.strip()}")
    assert not wrong_hits, (
        f"Found incorrect '{WRONG_ARG}' in:\n" + "\n".join(wrong_hits)
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression guard
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_webpack_reference_unchanged():
    """Webpack implementation still uses debugChannelReadable (reference unchanged)."""
    content = WEBPACK_FILE.read_text()
    assert CORRECT_ARG in content, (
        "Webpack reference implementation no longer contains the correct argument"
    )

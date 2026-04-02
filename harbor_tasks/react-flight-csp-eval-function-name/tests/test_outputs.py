"""
Task: react-flight-csp-eval-function-name
Repo: facebook/react @ 87ae75b33f71eb673c55ddb3a147a9e58b7d05bd
PR:   35650

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Fix: In createFakeFunction's eval-disabled fallback (catch block),
add Object.defineProperty(fn, 'name', {value: name}) so the function
retains its server-side name for stack traces in CSP environments.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"
CLIENT_JS = f"{REPO}/packages/react-client/src/ReactFlightClient.js"


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — source file structure
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_createfakefunction_exists():
    """ReactFlightClient.js exists and contains createFakeFunction with a catch block."""
    src = Path(CLIENT_JS).read_text()
    assert "createFakeFunction" in src, "createFakeFunction not found in ReactFlightClient.js"
    func_start = src.find("function createFakeFunction")
    assert func_start != -1, "function createFakeFunction declaration not found"
    catch_pos = src.find("catch (x)", func_start)
    assert catch_pos != -1, "catch (x) block not found in createFakeFunction"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# AST-only because: ReactFlightClient.js uses Flow type annotations and cannot
# be executed directly with node without transpilation.
def test_defineProperty_sets_fn_name_in_csp_fallback():
    """catch block in createFakeFunction sets fn.name via Object.defineProperty."""
    src = Path(CLIENT_JS).read_text()

    func_start = src.find("function createFakeFunction")
    assert func_start != -1

    catch_start = src.find("catch (x)", func_start)
    assert catch_start != -1

    # Inspect up to 600 chars after catch — enough to cover the full catch body
    catch_region = src[catch_start : catch_start + 600]

    # Must call Object.defineProperty on fn
    assert "Object.defineProperty" in catch_region, (
        "catch block does not call Object.defineProperty to set fn.name; "
        "CSP fallback function will have no meaningful name in stack traces"
    )

    # Must target the 'name' property
    define_idx = catch_region.index("Object.defineProperty")
    name_region = catch_region[define_idx : define_idx + 200]
    assert "'name'" in name_region or '"name"' in name_region, (
        "Object.defineProperty in catch block does not target the 'name' property"
    )

    # Must pass the name variable as the value descriptor
    assert "value: name" in name_region, (
        "{value: name} descriptor not found — fn.name will not be set to the "
        "server-side component name"
    )


# [pr_diff] fail_to_pass
# AST-only because: ReactFlightClient.js uses Flow type annotations and cannot
# be executed directly with node without transpilation.
def test_flowfixme_cannot_write_comment():
    """$FlowFixMe[cannot-write] suppresses the Flow type error on fn.name assignment."""
    src = Path(CLIENT_JS).read_text()

    # Verify the comment is present anywhere in the file
    assert "$FlowFixMe[cannot-write]" in src, (
        "$FlowFixMe[cannot-write] comment not found; Flow will report a type error "
        "because the `name` property is typed as read-only on Function"
    )

    # Verify it appears near the Object.defineProperty call (not some unrelated location)
    func_start = src.find("function createFakeFunction")
    catch_start = src.find("catch (x)", func_start)
    catch_region = src[catch_start : catch_start + 600]
    assert "$FlowFixMe[cannot-write]" in catch_region, (
        "$FlowFixMe[cannot-write] must be inside the createFakeFunction catch block, "
        "directly suppressing the Object.defineProperty('name') call"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression check
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_flight_tests():
    """Upstream ReactFlight test suite still passes after the fix."""
    r = subprocess.run(
        [
            "yarn",
            "test",
            "--silent",
            "--no-watchman",
            "--testPathPattern",
            "ReactFlight-test",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=110,
    )
    stdout = r.stdout.decode(errors="replace")
    stderr = r.stderr.decode(errors="replace")
    assert r.returncode == 0, (
        f"ReactFlight tests failed (exit {r.returncode}):\n"
        f"{stdout[-3000:]}\n{stderr[-1000:]}"
    )

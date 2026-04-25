"""
Tests for prisma/prisma#29182: fix: add missing deserialization for JSON values

The bug: Date objects in JSON/JSONB fields lose their type information
because the parameterization layer double-serializes them via JSON.stringify().
When read back, dates appear as strings instead of Date objects.

The fix: Use deserializeJsonObject to properly wrap values before JSON.stringify
in the parameterization layer, and add Raw type handling in the deserialization path.
"""
import subprocess
import os
import sys

REPO = "/workspace/prisma_repo"


def test_json_protocol_unit_tests():
    """Run the json-protocol unit test suite (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "--filter", "@prisma/client-engine-runtime", "test", "json-protocol"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"json-protocol unit tests failed:\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n"
        f"STDERR:\n{r.stderr[-2000:]}"
    )


def test_deserialize_json_object_is_a_function():
    """
    Verify deserializeJsonObject is exported as a function from @prisma/client-engine-runtime.
    On base commit the function is named deserializeJsonResponse (returns undefined when
    imported as deserializeJsonObject). After the fix, deserializeJsonObject is a proper function.
    Fails on base (deserializeJsonObject is undefined), passes after fix.
    """
    test_script = REPO + "/test_fn.ts"
    with open(test_script, "w") as f:
        f.write("""
import { deserializeJsonObject } from "./packages/client-engine-runtime/src/index.ts";
if (typeof deserializeJsonObject !== 'function') {
    console.error("FAIL: deserializeJsonObject is", typeof deserializeJsonObject);
    process.exit(1);
}
console.log("PASS: deserializeJsonObject is a function");
process.exit(0);
""")
    try:
        r = subprocess.run(
            ["tsx", test_script],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
        )
    finally:
        os.unlink(test_script)

    assert r.returncode == 0, (
        f"deserializeJsonObject is not a function on base (it doesn't exist yet).\n"
        f"STDOUT:\n{r.stdout}\n"
        f"STDERR:\n{r.stderr}"
    )


def test_deserialize_handles_raw_type():
    """
    Verify deserializeJsonObject handles Raw type ($type: 'Raw').
    On the base commit, deserializeTaggedValue does not have a case for 'Raw',
    so it hits assertNever and throws 'Unknown tagged value'.
    After the fix, it returns the raw value.
    Fails on base (throws), passes after fix.
    """
    test_script = REPO + "/test_raw.ts"
    with open(test_script, "w") as f:
        f.write("""
import { deserializeJsonObject } from "./packages/client-engine-runtime/src/json-protocol.ts";

try {
    const result = deserializeJsonObject({ $type: "Raw", value: 42 });
    if (result !== 42) {
        console.error("FAIL: Raw type returned", result, "expected 42");
        process.exit(1);
    }
    console.log("PASS: Raw type handled correctly, returned 42");
    process.exit(0);
} catch (e) {
    console.error("FAIL: threw error:", (e as Error).message);
    process.exit(1);
}
""")
    try:
        r = subprocess.run(
            ["tsx", test_script],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
        )
    finally:
        os.unlink(test_script)

    assert r.returncode == 0, (
        f"Raw type handling test failed:\n"
        f"STDOUT:\n{r.stdout}\n"
        f"STDERR:\n{r.stderr}"
    )


def test_normalize_handles_fieldref():
    """
    Verify normalizeJsonProtocolValues handles FieldRef type.
    On base, FieldRef is not handled and throws 'Unknown tagged value'.
    After the fix, FieldRef values pass through unchanged.
    Fails on base (throws), passes after fix.
    """
    test_script = REPO + "/test_fieldref.ts"
    with open(test_script, "w") as f:
        f.write("""
import { normalizeJsonProtocolValues } from "./packages/client-engine-runtime/src/json-protocol.ts";

try {
    const result = normalizeJsonProtocolValues({ $type: "FieldRef", value: { _ref: "test" } });
    if (result.$type !== "FieldRef") {
        console.error("FAIL: FieldRef type lost");
        process.exit(1);
    }
    console.log("PASS: FieldRef handled correctly");
    process.exit(0);
} catch (e) {
    console.error("FAIL: threw error:", (e as Error).message);
    process.exit(1);
}
""")
    try:
        r = subprocess.run(
            ["tsx", test_script],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
        )
    finally:
        os.unlink(test_script)

    assert r.returncode == 0, (
        f"FieldRef handling test failed:\n"
        f"STDOUT:\n{r.stdout}\n"
        f"STDERR:\n{r.stderr}"
    )


def test_normalize_handles_enum():
    """
    Verify normalizeJsonProtocolValues handles Enum type.
    On base, Enum is not handled and throws 'Unknown tagged value'.
    After the fix, Enum values pass through unchanged.
    Fails on base (throws), passes after fix.
    """
    test_script = REPO + "/test_enum.ts"
    with open(test_script, "w") as f:
        f.write("""
import { normalizeJsonProtocolValues } from "./packages/client-engine-runtime/src/json-protocol.ts";

try {
    const result = normalizeJsonProtocolValues({ $type: "Enum", value: "Active" });
    if (result.$type !== "Enum" || result.value !== "Active") {
        console.error("FAIL: Enum type/value lost");
        process.exit(1);
    }
    console.log("PASS: Enum handled correctly");
    process.exit(0);
} catch (e) {
    console.error("FAIL: threw error:", (e as Error).message);
    process.exit(1);
}
""")
    try:
        r = subprocess.run(
            ["tsx", test_script],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
        )
    finally:
        os.unlink(test_script)

    assert r.returncode == 0, (
        f"Enum handling test failed:\n"
        f"STDOUT:\n{r.stdout}\n"
        f"STDERR:\n{r.stderr}"
    )


def test_wrap_raw_values_default_true():
    """
    Verify shouldWrapRawValues() defaults to true in SerializeContext.
    The method returns this.params.wrapRawValues ?? true after fix,
    but this.params.wrapRawValues ?? false before fix.
    This grep test verifies the default has been changed.
    Fails on base (grep finds false), passes after fix (grep finds true).
    """
    result = subprocess.run(
        ["grep", "-n", "wrapRawValues ?? true", "packages/client/src/runtime/core/jsonProtocol/serializeJsonQuery.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        "shouldWrapRawValues does not default to true. "
        "The fix changes the default from false to true. "
        "grep exit code: " + str(result.returncode)
    )


def test_repo_prettier_check():
    """Repo's prettier check passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "run", "prettier-check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"prettier-check failed:\n"
        f"STDOUT:\n{r.stdout[-1000:]}\n"
        f"STDERR:\n{r.stderr[-1000:]}"
    )


def test_repo_check_engines_override():
    """Repo's check-engines-override script passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "run", "check-engines-override"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"check-engines-override failed:\n"
        f"STDOUT:\n{r.stdout[-1000:]}\n"
        f"STDERR:\n{r.stderr[-1000:]}"
    )


def test_repo_client_engine_runtime_tests():
    """Repo's client-engine-runtime unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "--filter", "@prisma/client-engine-runtime", "test"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"client-engine-runtime tests failed:\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n"
        f"STDERR:\n{r.stderr[-2000:]}"
    )


if __name__ == "__main__":
    # Run all tests
    tests = [
        test_json_protocol_unit_tests,
        test_deserialize_json_object_is_a_function,
        test_deserialize_handles_raw_type,
        test_normalize_handles_fieldref,
        test_normalize_handles_enum,
        test_wrap_raw_values_default_true,
        test_repo_prettier_check,
        test_repo_check_engines_override,
        test_repo_client_engine_runtime_tests,
    ]

    failed = []
    for test in tests:
        try:
            print(f"Running {test.__name__}...", file=sys.stderr)
            test()
            print(f"  PASS: {test.__name__}", file=sys.stderr)
        except AssertionError as e:
            print(f"  FAIL: {test.__name__}: {e}", file=sys.stderr)
            failed.append(test.__name__)
        except Exception as e:
            print(f"  ERROR: {test.__name__}: {e}", file=sys.stderr)
            failed.append(test.__name__)

    if failed:
        print(f"\n{len(failed)} test(s) failed: {', '.join(failed)}", file=sys.stderr)
        sys.exit(1)
    else:
        print("\nAll tests passed!", file=sys.stderr)
        sys.exit(0)

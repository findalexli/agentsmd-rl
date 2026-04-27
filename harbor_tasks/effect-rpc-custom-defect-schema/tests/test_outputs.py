"""Tests for the @effect/rpc custom defect schema feature.

Each ``def test_*`` function maps 1:1 to a check id in eval_manifest.yaml.
Tests run inside the task-env Docker image with the agent's edits applied.
"""

import os
import shutil
import subprocess

REPO = "/workspace/effect"
RPC_PKG = "/workspace/effect/packages/rpc"
PLATFORM_NODE_PKG = "/workspace/effect/packages/platform-node"

CUSTOM_DEFECT_TEST_SRC = "/tests/custom_defect.test.ts"
CUSTOM_DEFECT_TEST_DST = f"{RPC_PKG}/test/_z_custom_defect.test.ts"


def _ensure_custom_test_present():
    if not os.path.exists(CUSTOM_DEFECT_TEST_DST):
        shutil.copy(CUSTOM_DEFECT_TEST_SRC, CUSTOM_DEFECT_TEST_DST)


def _vitest_filter(test_name_substring: str, timeout: int = 180):
    _ensure_custom_test_present()
    return subprocess.run(
        ["pnpm", "exec", "vitest", "run",
         "test/_z_custom_defect.test.ts",
         "-t", test_name_substring],
        cwd=RPC_PKG, capture_output=True, text=True, timeout=timeout,
    )


def _fail_msg(r: subprocess.CompletedProcess) -> str:
    return ("vitest failed:\n" + (r.stdout + r.stderr)[-3000:])


def test_exitschema_preserves_defect_object_fields():
    """f2p: Rpc.exitSchema with `defect: Schema.Unknown` round-trips an
    arbitrary object without losing fields like `code`, `kind`."""
    r = _vitest_filter("Schema.Unknown preserves arbitrary object fields")
    assert r.returncode == 0, _fail_msg(r)


def test_exitschema_preserves_primitive_defect():
    """f2p: round-trip of a primitive (number) defect."""
    r = _vitest_filter("Schema.Unknown preserves a primitive number defect")
    assert r.returncode == 0, _fail_msg(r)


def test_exitschema_preserves_nested_defect():
    """f2p: nested-object defect round-trips identically."""
    r = _vitest_filter("Schema.Unknown preserves a nested object defect")
    assert r.returncode == 0, _fail_msg(r)


def test_setsuccess_preserves_defect_schema():
    """f2p: chaining ``.setSuccess()`` retains the custom defect schema."""
    r = _vitest_filter("setSuccess preserves the defect schema across Proto chain")
    assert r.returncode == 0, _fail_msg(r)


def test_seterror_preserves_defect_schema():
    """f2p: chaining ``.setError()`` retains the custom defect schema."""
    r = _vitest_filter("setError preserves the defect schema across Proto chain")
    assert r.returncode == 0, _fail_msg(r)


def test_rpcgroup_preserves_defect_schema():
    """f2p: ``RpcGroup.make`` passes through the custom defect schema."""
    r = _vitest_filter("RpcGroup retains custom defect schema")
    assert r.returncode == 0, _fail_msg(r)


def test_existing_rpc_unit_tests_pass():
    """p2p: original rpc package unit tests still pass."""
    r = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "test/Rpc.test.ts"],
        cwd=RPC_PKG, capture_output=True, text=True, timeout=180,
    )
    assert r.returncode == 0, _fail_msg(r)


def test_existing_rpc_server_e2e_pass():
    """p2p: existing platform-node RpcServer e2e tests (100 tests) still pass.

    The strongest p2p — exercises ``sendRequestDefect`` / ``handleEncode``
    server-side encoding paths the PR refactors.
    """
    r = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "test/RpcServer.test.ts"],
        cwd=PLATFORM_NODE_PKG, capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, _fail_msg(r)


def test_lint_passes_on_changed_files():
    """p2p: eslint passes on the two files the PR modifies."""
    r = subprocess.run(
        ["pnpm", "exec", "eslint",
         "packages/rpc/src/Rpc.ts",
         "packages/rpc/src/RpcServer.ts"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, _fail_msg(r)

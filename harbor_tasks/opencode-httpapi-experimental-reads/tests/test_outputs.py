"""Behavioural tests for opencode PR #24365.

Track 1 oracle for the experimental HttpApi read-only routes.

Strategy
--------
We re-use the upstream PR's own integration test against the bridged Hono
routes. Bun's `bun:test` runs it in tree, so we materialise the test file in
`packages/opencode/test/server/` at run time, then invoke `bun test`.

`bun:test` does not always return a non-zero exit code on test-file import
failures (it prints `0 pass / 1 fail / 1 error` but exits 0), so we also
string-match the textual summary instead of relying solely on the exit code.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/opencode")
PKG = REPO / "packages" / "opencode"

GOLD_TEST_PATH = PKG / "test" / "server" / "httpapi-experimental.test.ts"
GOLD_TEST_BODY = '''import { afterEach, describe, expect, test } from "bun:test"
import type { UpgradeWebSocket } from "hono/ws"
import { Flag } from "@opencode-ai/core/flag/flag"
import { Instance } from "../../src/project/instance"
import { InstanceRoutes } from "../../src/server/routes/instance"
import { ExperimentalPaths } from "../../src/server/routes/instance/httpapi/experimental"
import { Log } from "../../src/util"
import { resetDatabase } from "../fixture/db"
import { tmpdir } from "../fixture/fixture"

void Log.init({ print: false })

const original = Flag.OPENCODE_EXPERIMENTAL_HTTPAPI
const websocket = (() => () => new Response(null, { status: 501 })) as unknown as UpgradeWebSocket

function app() {
  Flag.OPENCODE_EXPERIMENTAL_HTTPAPI = true
  return InstanceRoutes(websocket)
}

afterEach(async () => {
  Flag.OPENCODE_EXPERIMENTAL_HTTPAPI = original
  await Instance.disposeAll()
  await resetDatabase()
})

describe("experimental HttpApi", () => {
  test("serves read-only experimental endpoints through Hono bridge", async () => {
    await using tmp = await tmpdir({
      config: {
        formatter: false,
        lsp: false,
        mcp: {
          demo: {
            type: "local",
            command: ["echo", "demo"],
            enabled: false,
          },
        },
      },
    })

    const headers = { "x-opencode-directory": tmp.path }
    const [consoleState, consoleOrgs, toolIDs, resources] = await Promise.all([
      app().request(ExperimentalPaths.console, { headers }),
      app().request(ExperimentalPaths.consoleOrgs, { headers }),
      app().request(ExperimentalPaths.toolIDs, { headers }),
      app().request(ExperimentalPaths.resource, { headers }),
    ])

    expect(consoleState.status).toBe(200)
    expect(await consoleState.json()).toEqual({
      consoleManagedProviders: [],
      switchableOrgCount: 0,
    })

    expect(consoleOrgs.status).toBe(200)
    expect(await consoleOrgs.json()).toEqual({ orgs: [] })

    expect(toolIDs.status).toBe(200)
    expect(await toolIDs.json()).toContain("bash")

    expect(resources.status).toBe(200)
    expect(await resources.json()).toEqual({})
  })
})
'''

BUN_ENV = {
    **os.environ,
    "OPENCODE_DB": ":memory:",
    "CI": "1",
}


def _run(cmd: list[str], *, cwd: Path, timeout: int = 300) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
        env=BUN_ENV,
    )


def _ensure_gold_test_in_place() -> None:
    GOLD_TEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    GOLD_TEST_PATH.write_text(GOLD_TEST_BODY)


# -------- Fail-to-pass (PR's behavioural test) -----------------------------

def test_httpapi_experimental_passes() -> None:
    """The PR's integration test must pass end-to-end.

    On the base commit (no fix), the test file fails to import the new
    `httpapi/experimental` module and bun reports `0 pass / 1 fail`. After
    the fix, the four read-only routes are wired and the bodies match.
    """
    _ensure_gold_test_in_place()
    proc = _run(
        ["bun", "test", "--timeout", "60000", "test/server/httpapi-experimental.test.ts"],
        cwd=PKG,
        timeout=300,
    )
    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    pass_marker = "(pass) experimental HttpApi > serves read-only experimental endpoints through Hono bridge"
    assert pass_marker in combined, (
        "PR integration test did not pass on this build.\n"
        f"---- STDOUT ----\n{proc.stdout[-3000:]}\n"
        f"---- STDERR ----\n{proc.stderr[-3000:]}"
    )
    assert "Cannot find module" not in combined, (
        "Module import failed during test run.\n" + combined[-3000:]
    )
    assert " 0 fail" in combined, (
        "Some sub-assertions failed inside the integration test.\n" + combined[-3000:]
    )


def test_experimental_paths_exported() -> None:
    """`ExperimentalPaths` must be exported as a const map of the four route paths."""
    probe = PKG / "test" / "server" / "_probe_experimental_paths.test.ts"
    probe.write_text(
        '''
import { describe, expect, test } from "bun:test"
import { ExperimentalPaths } from "../../src/server/routes/instance/httpapi/experimental"

describe("experimental paths", () => {
  test("exports the four read-only paths", () => {
    expect(ExperimentalPaths.console).toBe("/experimental/console")
    expect(ExperimentalPaths.consoleOrgs).toBe("/experimental/console/orgs")
    expect(ExperimentalPaths.toolIDs).toBe("/experimental/tool/ids")
    expect(ExperimentalPaths.resource).toBe("/experimental/resource")
  })
})
'''
    )
    try:
        proc = _run(
            ["bun", "test", "--timeout", "30000", str(probe.relative_to(PKG))],
            cwd=PKG,
            timeout=120,
        )
        combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
        assert "(pass) experimental paths > exports the four read-only paths" in combined, (
            "ExperimentalPaths export probe failed.\n" + combined[-2000:]
        )
        assert " 0 fail" in combined, combined[-2000:]
    finally:
        try:
            probe.unlink()
        except FileNotFoundError:
            pass


def test_mcp_resource_is_effect_schema() -> None:
    """`MCP.Resource` must expose a `.zod` accessor for the legacy Hono route."""
    probe = PKG / "test" / "server" / "_probe_mcp_resource.test.ts"
    probe.write_text(
        '''
import { describe, expect, test } from "bun:test"
import { MCP } from "../../src/mcp"

describe("mcp resource schema", () => {
  test("exposes .zod compat for SDK pipeline", () => {
    expect(typeof (MCP.Resource as { zod?: unknown }).zod).not.toBe("undefined")
  })
})
'''
    )
    try:
        proc = _run(
            ["bun", "test", "--timeout", "30000", str(probe.relative_to(PKG))],
            cwd=PKG,
            timeout=120,
        )
        combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
        assert "(pass) mcp resource schema > exposes .zod compat for SDK pipeline" in combined, (
            "MCP.Resource shape probe failed.\n" + combined[-2000:]
        )
        assert " 0 fail" in combined, combined[-2000:]
    finally:
        try:
            probe.unlink()
        except FileNotFoundError:
            pass


# -------- Pass-to-pass (unrelated upstream tests still work) ---------------

def test_p2p_httpapi_bridge_still_passes() -> None:
    """Repo's existing httpapi-bridge test must keep passing."""
    proc = _run(
        ["bun", "test", "--timeout", "60000", "test/server/httpapi-bridge.test.ts"],
        cwd=PKG,
        timeout=300,
    )
    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    assert " 0 fail" in combined, combined[-2000:]
    assert "(pass) HttpApi Hono bridge" in combined, combined[-2000:]


def test_p2p_httpapi_file_still_passes() -> None:
    """Repo's existing httpapi-file test must keep passing."""
    proc = _run(
        ["bun", "test", "--timeout", "60000", "test/server/httpapi-file.test.ts"],
        cwd=PKG,
        timeout=300,
    )
    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    assert " 0 fail" in combined, combined[-2000:]

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_serves_read_only_experimental_endpoints_through_():
    """fail_to_pass | PR added test 'serves read-only experimental endpoints through Hono bridge' in 'packages/opencode/test/server/httpapi-experimental.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/opencode/test/server/httpapi-experimental.test.ts" -t "serves read-only experimental endpoints through Hono bridge" 2>&1 || npx vitest run "packages/opencode/test/server/httpapi-experimental.test.ts" -t "serves read-only experimental endpoints through Hono bridge" 2>&1 || pnpm jest "packages/opencode/test/server/httpapi-experimental.test.ts" -t "serves read-only experimental endpoints through Hono bridge" 2>&1 || npx jest "packages/opencode/test/server/httpapi-experimental.test.ts" -t "serves read-only experimental endpoints through Hono bridge" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'serves read-only experimental endpoints through Hono bridge' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_typecheck_run_typecheck():
    """pass_to_pass | CI job 'typecheck' → step 'Run typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_run_unit_tests():
    """pass_to_pass | CI job 'unit' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun turbo test:ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_run_app_e2e_tests():
    """pass_to_pass | CI job 'e2e' → step 'Run app e2e tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/app test:e2e:local'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run app e2e tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
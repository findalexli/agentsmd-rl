"""Behavioral tests for Infisical PR #6112 — disallow TOTP token reuse.

Strategy: We materialise a single Vitest test file that exercises the public
``totpServiceFactory`` from ``backend/src/services/totp/totp-service.ts`` with
hand-built mocks for the keystore, totp-config DAL and KMS service. The
keystore mock implements Redis ``SET … NX`` semantics with an in-memory map.

Each Python ``def test_*`` corresponds to one named Vitest test inside that
file. We run Vitest exactly once per Python test session via a module-level
fixture and look up each test result by name.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/infisical")
BACKEND = REPO / "backend"
TEST_REL_PATH = Path("src/services/totp/totp-service.replay.test.ts")
TEST_ABS_PATH = BACKEND / TEST_REL_PATH

VITEST_TEST_FILE = r'''
import { authenticator } from "otplib";
import { describe, expect, test, vi } from "vitest";

import {
  KeyStorePrefixes,
  KeyStoreTtls,
} from "@app/keystore/keystore";
import {
  BadRequestError,
  ForbiddenRequestError,
  NotFoundError,
} from "@app/lib/errors";

import { totpServiceFactory } from "@app/services/totp/totp-service";

const SECRET = "JBSWY3DPEHPK3PXP";
const USER_ID = "11111111-1111-1111-1111-111111111111";

const mkInMemoryKeyStore = () => {
  const store = new Map<string, string>();
  const calls: any[] = [];
  const setItemWithExpiryNX = vi.fn(
    async (key: string, ttl: number | string, value: string | number | Buffer) => {
      calls.push({ key, ttl, value });
      if (store.has(key)) return null;
      store.set(key, String(value));
      return "OK" as const;
    }
  );
  return { setItemWithExpiryNX, calls, store };
};

type Cfg = {
  isVerified?: boolean;
  config?: any;
};

const mkVerifiedConfig = () => ({
  id: "cfg-1",
  userId: USER_ID,
  isVerified: true,
  encryptedSecret: Buffer.from(SECRET),
  encryptedRecoveryCodes: Buffer.from(""),
});

const mkService = (opts: Cfg = {}) => {
  const cfg =
    opts.config === undefined
      ? mkVerifiedConfig()
      : opts.config;
  if (cfg && opts.isVerified !== undefined) {
    cfg.isVerified = opts.isVerified;
  }
  const totpConfigDAL: any = {
    findOne: vi.fn(async () => cfg),
    updateById: vi.fn(),
    deleteById: vi.fn(),
    create: vi.fn(),
    transaction: vi.fn(async (cb: any) => cb({})),
  };
  const kmsService: any = {
    decryptWithRootKey: () => (b: Buffer) => b,
    encryptWithRootKey: () => (b: Buffer) => b,
  };
  const userDAL: any = {
    findById: vi.fn(async () => ({ id: USER_ID, username: "alice" })),
    updateById: vi.fn(),
  };
  const keyStore = mkInMemoryKeyStore();
  const service = totpServiceFactory({
    totpConfigDAL,
    kmsService,
    userDAL,
    keyStore: keyStore as any,
  } as any);
  return { service, keyStore, totpConfigDAL };
};

describe("verifyUserTotp — replay prevention", () => {
  test("rejects a TOTP that was already accepted in the same window", async () => {
    const { service } = mkService();
    const code = authenticator.generate(SECRET);

    await service.verifyUserTotp({ userId: USER_ID, totp: code } as any);

    let threw = false;
    try {
      await service.verifyUserTotp({ userId: USER_ID, totp: code } as any);
    } catch (e: any) {
      threw = true;
      expect(e).toBeInstanceOf(ForbiddenRequestError);
    }
    expect(threw).toBe(true);
  });

  test("calls the keystore claim with the documented prefix and TTL", async () => {
    const { service, keyStore } = mkService();
    const code = authenticator.generate(SECRET);

    await service.verifyUserTotp({ userId: USER_ID, totp: code } as any);

    expect(keyStore.setItemWithExpiryNX).toHaveBeenCalledTimes(1);
    const call = keyStore.calls[0];
    expect(call.key).toBe(`used-totp-code:${USER_ID}:${code}`);
    expect(Number(call.ttl)).toBe(120);
  });

  test("a different user using the same code value is unaffected", async () => {
    // ONE service instance, ONE keystore — so per-user namespacing is the
    // only thing that prevents user B from being rejected as a replay.
    const { service, keyStore } = mkService();
    const code = authenticator.generate(SECRET);

    await service.verifyUserTotp({ userId: USER_ID, totp: code } as any);
    await expect(
      service.verifyUserTotp({ userId: "different-user-id", totp: code } as any)
    ).resolves.toBeUndefined();

    expect(keyStore.setItemWithExpiryNX).toHaveBeenCalledTimes(2);
    const keyA = keyStore.calls[0].key;
    const keyB = keyStore.calls[1].key;
    expect(keyA).not.toBe(keyB);
    expect(keyA).toContain(USER_ID);
    expect(keyB).toContain("different-user-id");
  });
});

describe("KeyStorePrefixes.UsedTotpCode — key shape", () => {
  test("formats the key as used-totp-code:<userId>:<code>", () => {
    const fn = (KeyStorePrefixes as any).UsedTotpCode as (
      u: string,
      c: string
    ) => string;
    expect(typeof fn).toBe("function");
    expect(fn("u-7", "123456")).toBe("used-totp-code:u-7:123456");
    expect(fn("alice", "999000")).toBe("used-totp-code:alice:999000");
  });
});

describe("KeyStoreTtls.UsedTotpCodeInSeconds", () => {
  test("is at least the full ±30s acceptance window", () => {
    const ttl = (KeyStoreTtls as any).UsedTotpCodeInSeconds as number;
    expect(typeof ttl).toBe("number");
    // window:1 → 90s of valid skew; the value must cover that with margin
    // and must not exceed 5 minutes (which would unduly delay legitimate
    // re-use after the window closes).
    expect(ttl).toBeGreaterThanOrEqual(90);
    expect(ttl).toBeLessThanOrEqual(300);
  });
});

describe("verifyUserTotp — preserved error contracts (pass-to-pass)", () => {
  test("throws NotFoundError when the user has no TOTP config", async () => {
    const { service } = mkService({ config: null });
    await expect(
      service.verifyUserTotp({ userId: USER_ID, totp: "000000" } as any)
    ).rejects.toBeInstanceOf(NotFoundError);
  });

  test("throws BadRequestError when the user's TOTP config is unverified", async () => {
    const { service } = mkService({ isVerified: false });
    await expect(
      service.verifyUserTotp({ userId: USER_ID, totp: "000000" } as any)
    ).rejects.toBeInstanceOf(BadRequestError);
  });

  test("throws ForbiddenRequestError on an invalid TOTP without consuming a claim", async () => {
    const { service, keyStore } = mkService();
    let threw = false;
    try {
      await service.verifyUserTotp({ userId: USER_ID, totp: "000000" } as any);
    } catch (e: any) {
      threw = true;
      expect(e).toBeInstanceOf(ForbiddenRequestError);
    }
    expect(threw).toBe(true);
    expect(keyStore.setItemWithExpiryNX).not.toHaveBeenCalled();
  });
});
'''


def _write_vitest_file() -> None:
    TEST_ABS_PATH.write_text(VITEST_TEST_FILE)


def _cleanup_vitest_file() -> None:
    try:
        TEST_ABS_PATH.unlink()
    except FileNotFoundError:
        pass


def _run_vitest() -> dict:
    json_out = BACKEND / "vitest-totp-report.json"
    if json_out.exists():
        json_out.unlink()
    env = os.environ.copy()
    env["NODE_OPTIONS"] = env.get("NODE_OPTIONS", "") + " --max-old-space-size=2048"
    cmd = [
        "npx",
        "--no-install",
        "vitest",
        "run",
        "-c",
        "vitest.unit.config.mts",
        "--reporter=json",
        f"--outputFile={json_out.name}",
        str(TEST_REL_PATH),
    ]
    proc = subprocess.run(
        cmd, cwd=str(BACKEND), capture_output=True, text=True, timeout=600, env=env
    )
    if not json_out.exists():
        raise RuntimeError(
            f"vitest produced no JSON report.\n"
            f"return code: {proc.returncode}\n"
            f"--- stdout ---\n{proc.stdout[-2000:]}\n"
            f"--- stderr ---\n{proc.stderr[-2000:]}"
        )
    report = json.loads(json_out.read_text())
    return report


_REPORT_CACHE: dict | None = None


def _report() -> dict:
    global _REPORT_CACHE
    if _REPORT_CACHE is None:
        _write_vitest_file()
        try:
            _REPORT_CACHE = _run_vitest()
        finally:
            _cleanup_vitest_file()
    return _REPORT_CACHE


def _assert_vitest_test_passed(name_substring: str) -> None:
    report = _report()
    matched = []
    for suite in report.get("testResults", []):
        for assertion in suite.get("assertionResults", []):
            full = assertion.get("fullName") or assertion.get("title", "")
            if name_substring in full:
                matched.append((full, assertion.get("status")))
    assert matched, (
        f"No vitest test matched substring {name_substring!r}. "
        f"Available tests: "
        + "; ".join(
            (a.get("fullName") or a.get("title", ""))
            for s in report.get("testResults", [])
            for a in s.get("assertionResults", [])
        )
    )
    failed = [f for f, status in matched if status != "passed"]
    assert not failed, f"vitest tests failed: {failed!r}"


# ---------- fail-to-pass ----------------------------------------------------


def test_replay_blocked():
    """Submitting the same TOTP twice in succession is rejected on the second
    call with a ForbiddenRequestError."""
    _assert_vitest_test_passed("rejects a TOTP that was already accepted")


def test_keystore_claim_uses_documented_prefix_and_ttl():
    """The replay-prevention claim is written under the
    ``used-totp-code:<userId>:<code>`` key with a 120-second TTL."""
    _assert_vitest_test_passed("calls the keystore claim with the documented prefix")


def test_replay_protection_is_per_user():
    """The claim key includes the userId so distinct users with the same
    code value do not collide."""
    _assert_vitest_test_passed("a different user using the same code value")


def test_used_totp_code_prefix_factory_shape():
    """KeyStorePrefixes.UsedTotpCode produces the documented key shape."""
    _assert_vitest_test_passed("formats the key as used-totp-code")


def test_used_totp_code_ttl_in_window():
    """KeyStoreTtls.UsedTotpCodeInSeconds covers the ±30s acceptance window."""
    _assert_vitest_test_passed("at least the full ±30s acceptance window")


# ---------- pass-to-pass ----------------------------------------------------


def test_p2p_no_config_throws_not_found():
    _assert_vitest_test_passed("throws NotFoundError when the user has no TOTP config")


def test_p2p_unverified_config_throws_bad_request():
    _assert_vitest_test_passed("throws BadRequestError when the user's TOTP config is unverified")


def test_p2p_invalid_totp_throws_forbidden_without_claim():
    _assert_vitest_test_passed("throws ForbiddenRequestError on an invalid TOTP")


def test_p2p_repo_validate_string_unit_test():
    """Run an unrelated existing unit test from the repo to confirm the
    backend test toolchain stays green at base."""
    proc = subprocess.run(
        [
            "npx",
            "--no-install",
            "vitest",
            "run",
            "-c",
            "vitest.unit.config.mts",
            "src/lib/validator/validate-string.test.ts",
        ],
        cwd=str(BACKEND),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, (
        f"validate-string unit tests should pass at base.\n"
        f"--- stdout ---\n{proc.stdout[-1500:]}\n"
        f"--- stderr ---\n{proc.stderr[-1500:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_lint_run_lint_check():
    """pass_to_pass | CI job 'Lint' → step 'Run lint check'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run lint'], cwd=os.path.join(REPO, 'backend'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run lint check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_type_check_run_type_check():
    """pass_to_pass | CI job 'Type Check' → step 'Run type check'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run type:check'], cwd=os.path.join(REPO, 'backend'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run type check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_run_bdd_tests_run_bdd_tests():
    """pass_to_pass | CI job 'Run BDD tests' → step 'Run bdd tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run test:bdd'], cwd=os.path.join(REPO, 'backend'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run bdd tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_run_integration_test_run_unit_test():
    """pass_to_pass | CI job 'Run integration test' → step 'Run unit test'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run test:unit'], cwd=os.path.join(REPO, 'backend'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_run_integration_test_run_integration_test():
    """pass_to_pass | CI job 'Run integration test' → step 'Run integration test'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run test:e2e'], cwd=os.path.join(REPO, 'backend'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run integration test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_validate_db_schemas_apply_migrations():
    """pass_to_pass | CI job 'Validate DB schemas' → step 'Apply migrations'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run migration:latest-dev'], cwd=os.path.join(REPO, 'backend'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Apply migrations' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_validate_db_schemas_run_schema_generation():
    """pass_to_pass | CI job 'Validate DB schemas' → step 'Run schema generation'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run generate:schema'], cwd=os.path.join(REPO, 'backend'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run schema generation' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
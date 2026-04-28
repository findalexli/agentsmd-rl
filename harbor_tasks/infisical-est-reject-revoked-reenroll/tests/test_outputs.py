"""Behavioral tests for Infisical PR #6163 (reject EST simple re-enroll with revoked client cert).

Strategy: write the gold version of certificate-est-v3-service.test.ts (which contains the new
revoked-cert test) onto the repo, then run vitest. Parse vitest JSON output and assert on
individual test outcomes.
"""

import json
import os
import subprocess
from functools import lru_cache
from pathlib import Path

REPO = Path("/workspace/infisical")
BACKEND = REPO / "backend"
TEST_REL = "src/services/certificate-est-v3/certificate-est-v3-service.test.ts"
REVOKED_TEST_TITLE = "should reject re-enrollment when the client certificate is revoked"

# The gold version of certificate-est-v3-service.test.ts at the merge commit of PR #6163
# (9cab65ffeeb6c9f7ff7020f33f483464a945ea4d). Embedded inline so the harness does not need
# to mount any extra fixture files into /tests.
GOLD_TEST_FIXTURE = r'''/* eslint-disable @typescript-eslint/no-unsafe-call */
/* eslint-disable @typescript-eslint/no-unsafe-return */
/* eslint-disable @typescript-eslint/no-unsafe-argument */
/* eslint-disable @typescript-eslint/no-unsafe-assignment */
/* eslint-disable @typescript-eslint/no-unsafe-member-access */
/* eslint-disable @typescript-eslint/no-explicit-any */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { BadRequestError, NotFoundError, UnauthorizedError } from "@app/lib/errors";
import { CertStatus } from "@app/services/certificate/certificate-types";
import { CertificateRequestStatus } from "@app/services/certificate-request/certificate-request-types";

import { EnrollmentType } from "../certificate-profile/certificate-profile-types";
import { certificateEstV3ServiceFactory, TCertificateEstV3ServiceFactory } from "./certificate-est-v3-service";

// Mock the x509 module
vi.mock("@peculiar/x509", () => ({
  Pkcs10CertificateRequest: vi.fn(),
  GeneralNames: vi.fn(),
  KeyUsagesExtension: vi.fn(),
  ExtendedKeyUsageExtension: vi.fn(),
  X509Certificate: vi.fn().mockImplementation(() => ({
    rawData: new ArrayBuffer(0)
  })),
  KeyUsageFlags: {
    digitalSignature: 1,
    nonRepudiation: 2,
    keyEncipherment: 4,
    dataEncipherment: 8,
    keyAgreement: 16,
    keyCertSign: 32,
    cRLSign: 64,
    encipherOnly: 128,
    decipherOnly: 256
  },
  ExtendedKeyUsage: {
    clientAuth: "1.3.6.1.5.5.7.3.2",
    serverAuth: "1.3.6.1.5.5.7.3.1",
    codeSigning: "1.3.6.1.5.5.7.3.3",
    emailProtection: "1.3.6.1.5.5.7.3.4",
    ocspSigning: "1.3.6.1.5.5.7.3.9",
    timeStamping: "1.3.6.1.5.5.7.3.8"
  }
}));

vi.mock("@app/lib/certificates/extract-certificate", () => ({
  extractX509CertFromChain: vi.fn(() => ["mock-cert"])
}));

vi.mock("@app/services/certificate/certificate-fns", () => ({
  isCertChainValid: vi.fn(() => Promise.resolve(true))
}));

vi.mock("@app/services/certificate-authority/certificate-authority-fns", () => ({
  getCaCertChain: vi.fn(() =>
    Promise.resolve({
      caCert: "mock-ca-cert",
      caCertChain: "mock-ca-chain"
    })
  ),
  getCaCertChains: vi.fn(() =>
    Promise.resolve([
      {
        certificate: "mock-cert",
        certificateChain: "mock-chain"
      }
    ])
  )
}));

vi.mock("@app/services/project/project-fns", () => ({
  getProjectKmsCertificateKeyId: vi.fn(() => Promise.resolve("mock-kms-id"))
}));

vi.mock("../../ee/services/certificate-est/certificate-est-fns", () => ({
  convertRawCertsToPkcs7: vi.fn(() => "mocked-pkcs7-response")
}));

describe("CertificateEstV3Service", () => {
  let service: TCertificateEstV3ServiceFactory;

  const mockCertificateV3Service = {
    signCertificateFromProfile: vi.fn()
  };

  const mockCertificateAuthorityDAL = {
    findById: vi.fn(),
    findByIdWithAssociatedCa: vi.fn()
  };

  const mockCertificateAuthorityCertDAL = {
    find: vi.fn(),
    findById: vi.fn()
  };

  const mockCertificateDAL = {
    findOne: vi.fn(),
    transaction: vi.fn().mockImplementation(async (cb: (tx: unknown) => unknown) => cb({}))
  };

  const mockProjectDAL = {
    findOne: vi.fn(),
    updateById: vi.fn(),
    transaction: vi.fn()
  };

  const mockKmsService = {
    decryptWithKmsKey: vi.fn().mockResolvedValue(vi.fn(() => Promise.resolve(Buffer.from("mock-decrypted")))),
    generateKmsKey: vi.fn()
  };

  const mockLicenseService = {
    getPlan: vi.fn()
  };

  const mockCertificateProfileDAL = {
    findByIdWithConfigs: vi.fn()
  };

  const mockEstEnrollmentConfigDAL = {
    findById: vi.fn()
  };

  const mockCertificatePolicyDAL = {
    findById: vi.fn()
  };

  const mockProfile = {
    id: "profile-123",
    projectId: "project-123",
    caId: "ca-123",
    certificatePolicyId: "policy-123",
    slug: "test-profile",
    enrollmentType: EnrollmentType.EST,
    issuerType: "ca" as const,
    estConfigId: "est-config-123",
    createdAt: new Date(),
    updatedAt: new Date()
  };

  const mockEstConfig = {
    id: "est-config-123",
    disableBootstrapCaValidation: true,
    encryptedCaChain: null,
    hashedPassphrase: "hashed",
    createdAt: new Date(),
    updatedAt: new Date()
  };

  const mockProject = {
    id: "project-123",
    orgId: "org-123"
  };

  const mockPlan = {
    pkiEst: true
  };

  const mockPolicy = {
    id: "policy-123",
    validity: { max: "90d" }
  };

  beforeEach(async () => {
    service = certificateEstV3ServiceFactory({
      certificateV3Service: mockCertificateV3Service,
      certificateAuthorityDAL: mockCertificateAuthorityDAL,
      certificateAuthorityCertDAL: mockCertificateAuthorityCertDAL,
      certificateDAL: mockCertificateDAL,
      projectDAL: mockProjectDAL,
      kmsService: mockKmsService,
      licenseService: mockLicenseService,
      certificateProfileDAL: mockCertificateProfileDAL,
      estEnrollmentConfigDAL: mockEstEnrollmentConfigDAL,
      certificatePolicyDAL: mockCertificatePolicyDAL
    });

    mockCertificateProfileDAL.findByIdWithConfigs.mockResolvedValue(mockProfile);
    mockEstEnrollmentConfigDAL.findById.mockResolvedValue(mockEstConfig);
    mockProjectDAL.findOne.mockResolvedValue(mockProject);
    mockLicenseService.getPlan.mockResolvedValue(mockPlan);
    mockCertificatePolicyDAL.findById.mockResolvedValue(mockPolicy);
    mockCertificateDAL.findOne.mockResolvedValue(null);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe("simpleEnrollByProfile", () => {
    it("should successfully enroll and return PKCS7 response", async () => {
      mockCertificateV3Service.signCertificateFromProfile.mockResolvedValue({
        status: CertificateRequestStatus.ISSUED,
        certificate: "-----BEGIN CERTIFICATE-----\nMIIB...\n-----END CERTIFICATE-----",
        certificateId: "cert-123"
      });

      const result = await service.simpleEnrollByProfile({
        csr: "mock-csr",
        profileId: "profile-123",
        sslClientCert: ""
      });

      expect(result).toBe("mocked-pkcs7-response");
      expect(mockCertificateV3Service.signCertificateFromProfile).toHaveBeenCalledWith(
        expect.objectContaining({
          profileId: "profile-123",
          csr: "mock-csr",
          enrollmentType: EnrollmentType.EST,
          validity: { ttl: "90d" }
        })
      );
    });

    it("should throw error when approval is required", async () => {
      mockCertificateV3Service.signCertificateFromProfile.mockResolvedValue({
        status: CertificateRequestStatus.PENDING_APPROVAL,
        certificateRequestId: "req-123",
        message: "Requires approval"
      });

      await expect(
        service.simpleEnrollByProfile({
          csr: "mock-csr",
          profileId: "profile-123",
          sslClientCert: ""
        })
      ).rejects.toThrow(BadRequestError);

      await expect(
        service.simpleEnrollByProfile({
          csr: "mock-csr",
          profileId: "profile-123",
          sslClientCert: ""
        })
      ).rejects.toThrow(/requires approval/i);
    });

    it("should throw error when profile not found", async () => {
      mockCertificateProfileDAL.findByIdWithConfigs.mockResolvedValue(null);

      await expect(
        service.simpleEnrollByProfile({
          csr: "mock-csr",
          profileId: "nonexistent",
          sslClientCert: ""
        })
      ).rejects.toThrow(NotFoundError);
    });

    it("should throw error when profile is not configured for EST", async () => {
      mockCertificateProfileDAL.findByIdWithConfigs.mockResolvedValue({
        ...mockProfile,
        enrollmentType: EnrollmentType.API
      });

      await expect(
        service.simpleEnrollByProfile({
          csr: "mock-csr",
          profileId: "profile-123",
          sslClientCert: ""
        })
      ).rejects.toThrow(BadRequestError);
    });

    it("should throw error when EST config not found", async () => {
      mockEstEnrollmentConfigDAL.findById.mockResolvedValue(null);

      await expect(
        service.simpleEnrollByProfile({
          csr: "mock-csr",
          profileId: "profile-123",
          sslClientCert: ""
        })
      ).rejects.toThrow(NotFoundError);
    });

    it("should throw error when PKI EST is not available in plan", async () => {
      mockLicenseService.getPlan.mockResolvedValue({ pkiEst: false });

      await expect(
        service.simpleEnrollByProfile({
          csr: "mock-csr",
          profileId: "profile-123",
          sslClientCert: ""
        })
      ).rejects.toThrow(BadRequestError);
    });

    it("should throw error when certificate is not returned", async () => {
      mockCertificateV3Service.signCertificateFromProfile.mockResolvedValue({
        status: CertificateRequestStatus.ISSUED,
        certificate: null,
        certificateId: "cert-123"
      });

      await expect(
        service.simpleEnrollByProfile({
          csr: "mock-csr",
          profileId: "profile-123",
          sslClientCert: ""
        })
      ).rejects.toThrow(BadRequestError);
    });

    it("should use flow default TTL when profile has no defaultTtlDays", async () => {
      mockCertificatePolicyDAL.findById.mockResolvedValue({
        id: "policy-123",
        validity: { max: "30d" }
      });

      mockCertificateV3Service.signCertificateFromProfile.mockResolvedValue({
        status: CertificateRequestStatus.ISSUED,
        certificate: "-----BEGIN CERTIFICATE-----\nMIIB...\n-----END CERTIFICATE-----",
        certificateId: "cert-123"
      });

      await service.simpleEnrollByProfile({
        csr: "mock-csr",
        profileId: "profile-123",
        sslClientCert: ""
      });

      expect(mockCertificateV3Service.signCertificateFromProfile).toHaveBeenCalledWith(
        expect.objectContaining({
          validity: { ttl: "90d" }
        })
      );
    });

    it("should use default 90d TTL when policy has no validity", async () => {
      mockCertificatePolicyDAL.findById.mockResolvedValue({
        id: "policy-123",
        validity: null
      });

      mockCertificateV3Service.signCertificateFromProfile.mockResolvedValue({
        status: CertificateRequestStatus.ISSUED,
        certificate: "-----BEGIN CERTIFICATE-----\nMIIB...\n-----END CERTIFICATE-----",
        certificateId: "cert-123"
      });

      await service.simpleEnrollByProfile({
        csr: "mock-csr",
        profileId: "profile-123",
        sslClientCert: ""
      });

      expect(mockCertificateV3Service.signCertificateFromProfile).toHaveBeenCalledWith(
        expect.objectContaining({
          validity: { ttl: "90d" }
        })
      );
    });
  });

  describe("simpleReenrollByProfile", () => {
    beforeEach(async () => {
      const { Pkcs10CertificateRequest, X509Certificate, GeneralNames } = await import("@peculiar/x509");

      (Pkcs10CertificateRequest as any).mockImplementation(() => ({
        subject: "CN=test.example.com",
        extensions: []
      }));

      (X509Certificate as any).mockImplementation(() => ({
        subject: "CN=test.example.com",
        extensions: [],
        rawData: new ArrayBuffer(0)
      }));

      (GeneralNames as any).mockImplementation(() => ({
        items: []
      }));
    });

    it("should successfully re-enroll and return PKCS7 response", async () => {
      mockCertificateV3Service.signCertificateFromProfile.mockResolvedValue({
        status: CertificateRequestStatus.ISSUED,
        certificate: "-----BEGIN CERTIFICATE-----\nMIIB...\n-----END CERTIFICATE-----",
        certificateId: "cert-123"
      });

      const result = await service.simpleReenrollByProfile({
        csr: "mock-csr",
        profileId: "profile-123",
        sslClientCert: encodeURIComponent("-----BEGIN CERTIFICATE-----\nMIIB...\n-----END CERTIFICATE-----")
      });

      expect(result).toBe("mocked-pkcs7-response");
    });

    it("should throw error when subjects do not match", async () => {
      const { Pkcs10CertificateRequest, X509Certificate } = await import("@peculiar/x509");

      (Pkcs10CertificateRequest as any).mockImplementation(() => ({
        subject: "CN=different.example.com",
        extensions: []
      }));

      (X509Certificate as any).mockImplementation(() => ({
        subject: "CN=test.example.com",
        extensions: [],
        rawData: new ArrayBuffer(0)
      }));

      await expect(
        service.simpleReenrollByProfile({
          csr: "mock-csr",
          profileId: "profile-123",
          sslClientCert: encodeURIComponent("-----BEGIN CERTIFICATE-----\nMIIB...\n-----END CERTIFICATE-----")
        })
      ).rejects.toThrow(BadRequestError);
    });

    it("should throw error when approval is required for re-enrollment", async () => {
      mockCertificateV3Service.signCertificateFromProfile.mockResolvedValue({
        status: CertificateRequestStatus.PENDING_APPROVAL,
        certificateRequestId: "req-123",
        message: "Requires approval"
      });

      await expect(
        service.simpleReenrollByProfile({
          csr: "mock-csr",
          profileId: "profile-123",
          sslClientCert: encodeURIComponent("-----BEGIN CERTIFICATE-----\nMIIB...\n-----END CERTIFICATE-----")
        })
      ).rejects.toThrow(/requires approval/i);
    });

    it("should reject re-enrollment when the client certificate is revoked", async () => {
      mockCertificateDAL.findOne.mockResolvedValue({ status: CertStatus.REVOKED });

      await expect(
        service.simpleReenrollByProfile({
          csr: "mock-csr",
          profileId: "profile-123",
          sslClientCert: encodeURIComponent("-----BEGIN CERTIFICATE-----\nMIIB...\n-----END CERTIFICATE-----")
        })
      ).rejects.toThrow(UnauthorizedError);

      expect(mockCertificateV3Service.signCertificateFromProfile).not.toHaveBeenCalled();
    });
  });

  describe("getCaCertsByProfile", () => {
    it("should return CA certificates in PKCS7 format", async () => {
      mockCertificateAuthorityDAL.findByIdWithAssociatedCa.mockResolvedValue({
        id: "ca-123",
        internalCa: {
          id: "internal-ca-123",
          activeCaCertId: "ca-cert-123"
        }
      });

      const result = await service.getCaCertsByProfile({
        profileId: "profile-123"
      });

      expect(result).toBe("mocked-pkcs7-response");
    });

    it("should throw error when profile not found", async () => {
      mockCertificateProfileDAL.findByIdWithConfigs.mockResolvedValue(null);

      await expect(
        service.getCaCertsByProfile({
          profileId: "nonexistent"
        })
      ).rejects.toThrow(NotFoundError);
    });

    it("should throw error when profile is not configured for EST", async () => {
      mockCertificateProfileDAL.findByIdWithConfigs.mockResolvedValue({
        ...mockProfile,
        enrollmentType: EnrollmentType.API
      });

      await expect(
        service.getCaCertsByProfile({
          profileId: "profile-123"
        })
      ).rejects.toThrow(BadRequestError);
    });
  });
});
'''


def _overlay_gold_test_file() -> None:
    target = BACKEND / TEST_REL
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(GOLD_TEST_FIXTURE)


def _run_vitest_json(*paths: str, timeout: int = 300) -> subprocess.CompletedProcess:
    args = [
        "npx", "vitest", "run",
        "-c", "vitest.unit.config.mts",
        "--reporter=json",
    ]
    args.extend(paths)
    return subprocess.run(
        args,
        cwd=str(BACKEND),
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "NODE_OPTIONS": "--max-old-space-size=4096"},
    )


def _parse_vitest_json(stdout: str) -> dict:
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        lines = stdout.splitlines()
        for i, line in enumerate(lines):
            if line.lstrip().startswith("{"):
                return json.loads("\n".join(lines[i:]))
    raise RuntimeError(
        "Could not parse vitest JSON output. First 500 chars:\n" + stdout[:500]
    )


@lru_cache(maxsize=1)
def _est_v3_results() -> dict:
    _overlay_gold_test_file()
    r = _run_vitest_json(TEST_REL)
    if not r.stdout.strip():
        raise RuntimeError(
            "vitest produced no stdout (rc=" + str(r.returncode) + ").\nstderr tail:\n" + r.stderr[-2000:]
        )
    return _parse_vitest_json(r.stdout)


def _all_assertions(data: dict) -> list:
    out = []
    for f in data.get("testResults", []):
        for a in f.get("assertionResults", []):
            out.append(a)
    return out


def test_revoked_reenroll_rejected():
    """fail_to_pass: simpleReenrollByProfile must throw UnauthorizedError when the client
    certificate's stored status is REVOKED. At base, no revocation check exists, so the
    request proceeds (or throws a different error class) and this assertion fails."""
    data = _est_v3_results()
    target = next(
        (a for a in _all_assertions(data) if REVOKED_TEST_TITLE in a.get("fullName", "")),
        None,
    )
    assert target is not None, (
        "vitest did not run a test titled "
        + repr(REVOKED_TEST_TITLE)
        + ". Tests seen: "
        + repr([a.get("fullName") for a in _all_assertions(data)])
    )
    assert target["status"] == "passed", (
        "Revoked-cert test did not pass (status="
        + str(target["status"])
        + "). Failure: "
        + repr(target.get("failureMessages", []))
    )


def test_existing_est_v3_tests_pass():
    """pass_to_pass: every test in certificate-est-v3-service.test.ts that existed at base
    (the 15 tests covering enroll, re-enroll, and CA-cert flows) must still pass — the agent's
    fix must not regress sibling behaviour."""
    data = _est_v3_results()
    existing = [
        a for a in _all_assertions(data)
        if REVOKED_TEST_TITLE not in a.get("fullName", "")
    ]
    assert len(existing) == 15, (
        "Expected 15 pre-existing tests, found "
        + str(len(existing))
        + ": "
        + repr([a.get("fullName") for a in existing])
    )
    failures = [a for a in existing if a["status"] != "passed"]
    if failures:
        msg = "Pre-existing tests regressed:"
        for a in failures:
            msg += "\n  - " + a["fullName"] + ": " + repr(a.get("failureMessages", []))
        raise AssertionError(msg)


def test_full_backend_unit_suite_passes():
    """pass_to_pass: the entire backend unit test suite (npm run test:unit) passes. The agent's
    change to certificate-est-v3-service.ts must not break unrelated unit tests — e.g. by
    altering the service factory's exported type signature in a way that breaks importers."""
    _overlay_gold_test_file()
    r = _run_vitest_json(timeout=600)
    assert r.returncode == 0, (
        "Full backend unit suite failed (rc="
        + str(r.returncode)
        + ").\nstdout tail:\n"
        + r.stdout[-2000:]
        + "\nstderr tail:\n"
        + r.stderr[-1000:]
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_type_check_run_type_check():
    """pass_to_pass | CI job 'Type Check' → step 'Run type check'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run type:check'], cwd=os.path.join(REPO, 'backend'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run type check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_run_lint_check():
    """pass_to_pass | CI job 'Lint' → step 'Run lint check'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run lint'], cwd=os.path.join(REPO, 'backend'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run lint check' failed (returncode={r.returncode}):\n"
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

def test_ci_run_bdd_tests_run_bdd_tests():
    """pass_to_pass | CI job 'Run BDD tests' → step 'Run bdd tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run test:bdd'], cwd=os.path.join(REPO, 'backend'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run bdd tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_should_reject_re_enrollment_when_the_client_cert():
    """fail_to_pass | PR added test 'should reject re-enrollment when the client certificate is revoked' in 'backend/src/services/certificate-est-v3/certificate-est-v3-service.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "backend/src/services/certificate-est-v3/certificate-est-v3-service.test.ts" -t "should reject re-enrollment when the client certificate is revoked" 2>&1 || npx vitest run "backend/src/services/certificate-est-v3/certificate-est-v3-service.test.ts" -t "should reject re-enrollment when the client certificate is revoked" 2>&1 || pnpm jest "backend/src/services/certificate-est-v3/certificate-est-v3-service.test.ts" -t "should reject re-enrollment when the client certificate is revoked" 2>&1 || npx jest "backend/src/services/certificate-est-v3/certificate-est-v3-service.test.ts" -t "should reject re-enrollment when the client certificate is revoked" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should reject re-enrollment when the client certificate is revoked' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

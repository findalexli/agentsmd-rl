#!/usr/bin/env bash
# Gold patch for Infisical PR #6163: reject EST simple re-enroll with revoked client cert.
# Inlined as a HEREDOC — never fetched from the network.
set -euo pipefail

cd /workspace/infisical

# Idempotency: if the distinctive line is already present, the patch is applied.
if grep -q 'Client certificate has been revoked' \
       backend/src/services/certificate-est-v3/certificate-est-v3-service.ts 2>/dev/null; then
  echo "solve.sh: gold patch already applied"
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/backend/src/server/routes/index.ts b/backend/src/server/routes/index.ts
index 244a3d9e92b..fd8cae9c705 100644
--- a/backend/src/server/routes/index.ts
+++ b/backend/src/server/routes/index.ts
@@ -2644,6 +2644,7 @@ export const registerRoutes = async (
     certificateV3Service,
     certificateAuthorityDAL,
     certificateAuthorityCertDAL,
+    certificateDAL,
     projectDAL,
     kmsService,
     licenseService,
diff --git a/backend/src/services/certificate-est-v3/certificate-est-v3-service.test.ts b/backend/src/services/certificate-est-v3/certificate-est-v3-service.test.ts
index 5b2b77d0249..f71f725b937 100644
--- a/backend/src/services/certificate-est-v3/certificate-est-v3-service.test.ts
+++ b/backend/src/services/certificate-est-v3/certificate-est-v3-service.test.ts
@@ -6,7 +6,8 @@
 /* eslint-disable @typescript-eslint/no-explicit-any */
 import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

-import { BadRequestError, NotFoundError } from "@app/lib/errors";
+import { BadRequestError, NotFoundError, UnauthorizedError } from "@app/lib/errors";
+import { CertStatus } from "@app/services/certificate/certificate-types";
 import { CertificateRequestStatus } from "@app/services/certificate-request/certificate-request-types";

 import { EnrollmentType } from "../certificate-profile/certificate-profile-types";
@@ -31,6 +32,14 @@ vi.mock("@peculiar/x509", () => ({
     cRLSign: 64,
     encipherOnly: 128,
     decipherOnly: 256
+  },
+  ExtendedKeyUsage: {
+    clientAuth: "1.3.6.1.5.5.7.3.2",
+    serverAuth: "1.3.6.1.5.5.7.3.1",
+    codeSigning: "1.3.6.1.5.5.7.3.3",
+    emailProtection: "1.3.6.1.5.5.7.3.4",
+    ocspSigning: "1.3.6.1.5.5.7.3.9",
+    timeStamping: "1.3.6.1.5.5.7.3.8"
   }
 }));

@@ -84,6 +93,11 @@ describe("CertificateEstV3Service", () => {
     findById: vi.fn()
   };

+  const mockCertificateDAL = {
+    findOne: vi.fn(),
+    transaction: vi.fn().mockImplementation(async (cb: (tx: unknown) => unknown) => cb({}))
+  };
+
   const mockProjectDAL = {
     findOne: vi.fn(),
     updateById: vi.fn(),
@@ -152,6 +166,7 @@ describe("CertificateEstV3Service", () => {
       certificateV3Service: mockCertificateV3Service,
       certificateAuthorityDAL: mockCertificateAuthorityDAL,
       certificateAuthorityCertDAL: mockCertificateAuthorityCertDAL,
+      certificateDAL: mockCertificateDAL,
       projectDAL: mockProjectDAL,
       kmsService: mockKmsService,
       licenseService: mockLicenseService,
@@ -165,6 +180,7 @@ describe("CertificateEstV3Service", () => {
     mockProjectDAL.findOne.mockResolvedValue(mockProject);
     mockLicenseService.getPlan.mockResolvedValue(mockPlan);
     mockCertificatePolicyDAL.findById.mockResolvedValue(mockPolicy);
+    mockCertificateDAL.findOne.mockResolvedValue(null);
   });

   afterEach(() => {
@@ -412,6 +428,20 @@ describe("CertificateEstV3Service", () => {
         })
       ).rejects.toThrow(/requires approval/i);
     });
+
+    it("should reject re-enrollment when the client certificate is revoked", async () => {
+      mockCertificateDAL.findOne.mockResolvedValue({ status: CertStatus.REVOKED });
+
+      await expect(
+        service.simpleReenrollByProfile({
+          csr: "mock-csr",
+          profileId: "profile-123",
+          sslClientCert: encodeURIComponent("-----BEGIN CERTIFICATE-----\nMIIB...\n-----END CERTIFICATE-----")
+        })
+      ).rejects.toThrow(UnauthorizedError);
+
+      expect(mockCertificateV3Service.signCertificateFromProfile).not.toHaveBeenCalled();
+    });
   });

   describe("getCaCertsByProfile", () => {
diff --git a/backend/src/services/certificate-est-v3/certificate-est-v3-service.ts b/backend/src/services/certificate-est-v3/certificate-est-v3-service.ts
index e3b6edae301..22275b8e978 100644
--- a/backend/src/services/certificate-est-v3/certificate-est-v3-service.ts
+++ b/backend/src/services/certificate-est-v3/certificate-est-v3-service.ts
@@ -3,7 +3,9 @@ import * as x509 from "@peculiar/x509";
 import { extractX509CertFromChain } from "@app/lib/certificates/extract-certificate";
 import { BadRequestError, NotFoundError, UnauthorizedError } from "@app/lib/errors";
 import { ActorType } from "@app/services/auth/auth-type";
+import { TCertificateDALFactory } from "@app/services/certificate/certificate-dal";
 import { isCertChainValid } from "@app/services/certificate/certificate-fns";
+import { CertStatus } from "@app/services/certificate/certificate-types";
 import { TCertificateAuthorityCertDALFactory } from "@app/services/certificate-authority/certificate-authority-cert-dal";
 import { TCertificateAuthorityDALFactory } from "@app/services/certificate-authority/certificate-authority-dal";
 import { getCaCertChain, getCaCertChains } from "@app/services/certificate-authority/certificate-authority-fns";
@@ -25,6 +27,7 @@ type TCertificateEstV3ServiceFactoryDep = {
   certificateV3Service: Pick<TCertificateV3ServiceFactory, "signCertificateFromProfile">;
   certificateAuthorityDAL: Pick<TCertificateAuthorityDALFactory, "findById" | "findByIdWithAssociatedCa">;
   certificateAuthorityCertDAL: Pick<TCertificateAuthorityCertDALFactory, "find" | "findById">;
+  certificateDAL: Pick<TCertificateDALFactory, "findOne" | "transaction">;
   projectDAL: Pick<TProjectDALFactory, "findOne" | "updateById" | "transaction">;
   kmsService: Pick<TKmsServiceFactory, "decryptWithKmsKey" | "generateKmsKey">;
   licenseService: Pick<TLicenseServiceFactory, "getPlan">;
@@ -39,6 +42,7 @@ export const certificateEstV3ServiceFactory = ({
   certificateV3Service,
   certificateAuthorityCertDAL,
   certificateAuthorityDAL,
+  certificateDAL,
   projectDAL,
   kmsService,
   licenseService,
@@ -249,6 +253,16 @@ export const certificateEstV3ServiceFactory = ({
       });
     }

+    // Transaction forces primary (not replica) so a just-revoked cert cannot slip through replica lag.
+    const isRevoked = await certificateDAL.transaction(async (tx) => {
+      const storedCert = await certificateDAL.findOne({ serialNumber: cert.serialNumber, caId: profile.caId }, tx);
+      return storedCert?.status === CertStatus.REVOKED;
+    });
+
+    if (isRevoked) {
+      throw new UnauthorizedError({ message: "Client certificate has been revoked" });
+    }
+
     const csrObj = new x509.Pkcs10CertificateRequest(csr);
     if (csrObj.subject !== cert.subject) {
       throw new BadRequestError({
PATCH

echo "solve.sh: gold patch applied"

#!/usr/bin/env bash
set -euo pipefail

cd /workspace/infisical

# Idempotency guard: distinctive token from the patch.
if grep -q "UsedTotpCode: (userId: string, code: string) =>" backend/src/keystore/keystore.ts; then
    echo "Patch already applied; skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/backend/src/keystore/keystore.ts b/backend/src/keystore/keystore.ts
--- a/backend/src/keystore/keystore.ts
+++ b/backend/src/keystore/keystore.ts
@@ -80,6 +80,7 @@ export const KeyStorePrefixes = {
   WebAuthnChallenge: (userId: string) => `webauthn-challenge:${userId}` as const,
   UserMfaLockoutLock: (userId: string) => `user-mfa-lockout-lock:${userId}` as const,
   UserMfaUnlockEmailSent: (userId: string) => `user-mfa-unlock-email-sent:${userId}` as const,
+  UsedTotpCode: (userId: string, code: string) => `used-totp-code:${userId}:${code}` as const,

   AiMcpServerOAuth: (sessionId: string) => `ai-mcp-server-oauth:${sessionId}` as const,

@@ -114,6 +115,7 @@ export const KeyStoreTtls = {
   ProjectPermissionDataTtlSeconds: 600, // 10 minutes - longer-lived data payload
   MfaSessionInSeconds: 300, // 5 minutes
   WebAuthnChallengeInSeconds: 300, // 5 minutes
+  UsedTotpCodeInSeconds: 120, // covers the full ±30s acceptance window (window:1 → 90s) with margin
   ProjectSSEConnectionTtlSeconds: 180, // Must be > heartbeat interval (60s) * 2
   TelemetryIdentifyIdentityInSeconds: 86400, // 24 hours
   RefreshTokenGraceInSeconds: 10,
diff --git a/backend/src/server/routes/index.ts b/backend/src/server/routes/index.ts
--- a/backend/src/server/routes/index.ts
+++ b/backend/src/server/routes/index.ts
@@ -981,7 +981,8 @@ export const registerRoutes = async (
   const totpService = totpServiceFactory({
     totpConfigDAL,
     userDAL,
-    kmsService
+    kmsService,
+    keyStore
   });

   const webAuthnService = webAuthnServiceFactory({
diff --git a/backend/src/services/totp/totp-service.ts b/backend/src/services/totp/totp-service.ts
--- a/backend/src/services/totp/totp-service.ts
+++ b/backend/src/services/totp/totp-service.ts
@@ -1,5 +1,6 @@
 import { authenticator } from "otplib";

+import { KeyStorePrefixes, KeyStoreTtls, TKeyStoreFactory } from "@app/keystore/keystore";
 import { BadRequestError, ForbiddenRequestError, NotFoundError } from "@app/lib/errors";

 import { TKmsServiceFactory } from "../kms/kms-service";
@@ -20,6 +21,7 @@ type TTotpServiceFactoryDep = {
   userDAL: TUserDALFactory;
   totpConfigDAL: TTotpConfigDALFactory;
   kmsService: TKmsServiceFactory;
+  keyStore: Pick<TKeyStoreFactory, "setItemWithExpiryNX">;
 };

 authenticator.options = { window: 1 };
@@ -28,7 +30,7 @@ export type TTotpServiceFactory = ReturnType<typeof totpServiceFactory>;

 const MAX_RECOVERY_CODE_LIMIT = 10;

-export const totpServiceFactory = ({ totpConfigDAL, kmsService, userDAL }: TTotpServiceFactoryDep) => {
+export const totpServiceFactory = ({ totpConfigDAL, kmsService, userDAL, keyStore }: TTotpServiceFactoryDep) => {
   const getUserTotpConfig = async ({ userId }: TGetUserTotpConfigDTO) => {
     const totpConfig = await totpConfigDAL.findOne({
       userId
@@ -178,6 +180,15 @@ export const totpServiceFactory = ({ totpConfigDAL, kmsService, userDAL }: TTotp
         message: "Invalid TOTP"
       });
     }
+
+    const claimed = await keyStore.setItemWithExpiryNX(
+      KeyStorePrefixes.UsedTotpCode(userId, totp),
+      KeyStoreTtls.UsedTotpCodeInSeconds,
+      "1"
+    );
+    if (!claimed) {
+      throw new ForbiddenRequestError({ message: "Invalid TOTP" });
+    }
   };

   const verifyWithUserRecoveryCode = async ({ userId, recoveryCode }: TVerifyWithUserRecoveryCodeDTO) => {
PATCH

echo "Patch applied successfully."

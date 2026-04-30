#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lobe-chat

# Idempotent: skip if already applied
if grep -q 'performTokenRefreshWithRetry' apps/desktop/src/main/controllers/RemoteServerConfigCtr.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
index fe8a82b6c31..5796cc8f922 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -81,17 +81,21 @@ When working with Linear issues:
 1. Complete the implementation for this specific issue
 2. Run type check: `bun run type-check`
 3. Run related tests if applicable
-4. **IMMEDIATELY** update issue status to "Done": `mcp__linear-server__update_issue`
-5. **IMMEDIATELY** add completion comment: `mcp__linear-server__create_comment`
-6. Only then move on to the next issue
+4. Create PR if needed
+5. **IMMEDIATELY** update issue status to **"In Review"** (NOT "Done"): `mcp__linear-server__update_issue`
+6. **IMMEDIATELY** add completion comment: `mcp__linear-server__create_comment`
+7. Only then move on to the next issue
+
+**Note:** Issue status should be set to **"In Review"** when PR is created. The status will be updated to **"Done"** only after the PR is merged (usually handled by Linear-GitHub integration or manually).
 
 **❌ Wrong approach:**
 
 - Complete Issue A → Complete Issue B → Complete Issue C → Update all statuses → Add all comments
+- Mark issue as "Done" immediately after creating PR
 
 **✅ Correct approach:**
 
-- Complete Issue A → Update A status → Add A comment → Complete Issue B → Update B status → Add B comment → ...
+- Complete Issue A → Create PR → Update A status to "In Review" → Add A comment → Complete Issue B → ...
 
 ## Rules Index
 
diff --git a/apps/desktop/package.json b/apps/desktop/package.json
index 8109dc034c2..8f04c152147 100644
--- a/apps/desktop/package.json
+++ b/apps/desktop/package.json
@@ -45,11 +45,13 @@
     "@lobechat/electron-server-ipc": "workspace:*",
     "@lobechat/file-loaders": "workspace:*",
     "@lobehub/i18n-cli": "^1.25.1",
+    "@types/async-retry": "^1.4.9",
     "@types/lodash": "^4.17.21",
     "@types/resolve": "^1.20.6",
     "@types/semver": "^7.7.1",
     "@types/set-cookie-parser": "^2.4.10",
     "@typescript/native-preview": "7.0.0-dev.20250711.1",
+    "async-retry": "^1.3.3",
     "consola": "^3.4.2",
     "cookie": "^1.1.1",
     "diff": "^8.0.2",
diff --git a/apps/desktop/src/main/controllers/AuthCtr.ts b/apps/desktop/src/main/controllers/AuthCtr.ts
index 5394f828b88..23b85a08513 100644
--- a/apps/desktop/src/main/controllers/AuthCtr.ts
+++ b/apps/desktop/src/main/controllers/AuthCtr.ts
@@ -246,12 +246,23 @@ export default class AuthCtr extends ControllerModule {
             logger.info('Auto-refresh successful');
             this.broadcastTokenRefreshed();
           } else {
-            logger.error(`Auto-refresh failed: ${result.error}`);
-            // If auto-refresh fails, stop timer and clear token
-            this.stopAutoRefresh();
-            await this.remoteServerConfigCtr.clearTokens();
-            await this.remoteServerConfigCtr.setRemoteServerConfig({ active: false });
-            this.broadcastAuthorizationRequired();
+            logger.error(`Auto-refresh failed after retries: ${result.error}`);
+
+            // Only clear tokens for non-retryable errors (e.g., invalid_grant)
+            // The retry mechanism in RemoteServerConfigCtr already handles transient errors
+            if (this.remoteServerConfigCtr.isNonRetryableError(result.error)) {
+              logger.warn(
+                'Non-retryable error detected, clearing tokens and requiring re-authorization',
+              );
+              this.stopAutoRefresh();
+              await this.remoteServerConfigCtr.clearTokens();
+              await this.remoteServerConfigCtr.setRemoteServerConfig({ active: false });
+              this.broadcastAuthorizationRequired();
+            } else {
+              // For other errors (after retries exhausted), log but don't clear tokens immediately
+              // The next refresh cycle will retry
+              logger.warn('Refresh failed but error may be transient, will retry on next cycle');
+            }
           }
         }
       } catch (error) {
@@ -335,11 +346,12 @@ export default class AuthCtr extends ControllerModule {
 
   /**
    * Refresh access token
+   * This method includes retry mechanism via RemoteServerConfigCtr.refreshAccessToken()
    */
   async refreshAccessToken() {
     logger.info('Starting to refresh access token');
     try {
-      // Call the centralized refresh logic in RemoteServerConfigCtr
+      // Call the centralized refresh logic in RemoteServerConfigCtr (includes retry)
       const result = await this.remoteServerConfigCtr.refreshAccessToken();
 
       if (result.success) {
@@ -350,25 +362,38 @@ export default class AuthCtr extends ControllerModule {
         this.startAutoRefresh();
         return { success: true };
       } else {
-        // Throw an error to be caught by the catch block below
-        // This maintains the existing behavior of clearing tokens on failure
         logger.error(`Token refresh failed via AuthCtr call: ${result.error}`);
-        throw new Error(result.error || 'Token refresh failed');
-      }
-    } catch (error) {
-      // Keep the existing logic to clear tokens and require re-auth on failure
-      logger.error('Token refresh operation failed via AuthCtr, initiating cleanup:', error);
 
-      // Refresh failed, clear tokens and disable remote server
-      logger.warn('Refresh failed, clearing tokens and disabling remote server');
-      this.stopAutoRefresh();
-      await this.remoteServerConfigCtr.clearTokens();
-      await this.remoteServerConfigCtr.setRemoteServerConfig({ active: false });
+        // Only clear tokens for non-retryable errors (e.g., invalid_grant)
+        if (this.remoteServerConfigCtr.isNonRetryableError(result.error)) {
+          logger.warn(
+            'Non-retryable error detected, clearing tokens and requiring re-authorization',
+          );
+          this.stopAutoRefresh();
+          await this.remoteServerConfigCtr.clearTokens();
+          await this.remoteServerConfigCtr.setRemoteServerConfig({ active: false });
+          this.broadcastAuthorizationRequired();
+        } else {
+          // For transient errors, don't clear tokens - allow manual retry
+          logger.warn('Refresh failed but error may be transient, tokens preserved for retry');
+        }
 
-      // Notify render process that re-authorization is required
-      this.broadcastAuthorizationRequired();
+        return { error: result.error, success: false };
+      }
+    } catch (error) {
+      const errorMessage = error instanceof Error ? error.message : String(error);
+      logger.error('Token refresh operation failed via AuthCtr:', errorMessage);
+
+      // Only clear tokens for non-retryable errors
+      if (this.remoteServerConfigCtr.isNonRetryableError(errorMessage)) {
+        logger.warn('Non-retryable error in catch block, clearing tokens');
+        this.stopAutoRefresh();
+        await this.remoteServerConfigCtr.clearTokens();
+        await this.remoteServerConfigCtr.setRemoteServerConfig({ active: false });
+        this.broadcastAuthorizationRequired();
+      }
 
-      return { error: error.message, success: false };
+      return { error: errorMessage, success: false };
     }
   }
 
@@ -601,7 +626,7 @@ export default class AuthCtr extends ControllerModule {
       if (currentTime >= expiresAt) {
         logger.info('Token has expired, attempting to refresh it');
 
-        // Attempt to refresh token
+        // Attempt to refresh token (includes retry mechanism)
         const refreshResult = await this.remoteServerConfigCtr.refreshAccessToken();
         if (refreshResult.success) {
           logger.info('Token refresh successful during initialization');
@@ -611,10 +636,18 @@ export default class AuthCtr extends ControllerModule {
           return;
         } else {
           logger.error(`Token refresh failed during initialization: ${refreshResult.error}`);
-          // Clear token and require re-authorization only on refresh failure
-          await this.remoteServerConfigCtr.clearTokens();
-          await this.remoteServerConfigCtr.setRemoteServerConfig({ active: false });
-          this.broadcastAuthorizationRequired();
+
+          // Only clear token for non-retryable errors
+          if (this.remoteServerConfigCtr.isNonRetryableError(refreshResult.error)) {
+            logger.warn('Non-retryable error during initialization, clearing tokens');
+            await this.remoteServerConfigCtr.clearTokens();
+            await this.remoteServerConfigCtr.setRemoteServerConfig({ active: false });
+            this.broadcastAuthorizationRequired();
+          } else {
+            // For transient errors, still start auto-refresh timer to retry later
+            logger.warn('Transient error during initialization, will retry via auto-refresh');
+            this.startAutoRefresh();
+          }
           return;
         }
       }
diff --git a/apps/desktop/src/main/controllers/RemoteServerConfigCtr.ts b/apps/desktop/src/main/controllers/RemoteServerConfigCtr.ts
index 4b9072005cd..8bfbda5c21c 100644
--- a/apps/desktop/src/main/controllers/RemoteServerConfigCtr.ts
+++ b/apps/desktop/src/main/controllers/RemoteServerConfigCtr.ts
@@ -1,4 +1,5 @@
 import { DataSyncConfig } from '@lobechat/electron-client-ipc';
+import retry from 'async-retry';
 import { safeStorage } from 'electron';
 import querystring from 'node:querystring';
 import { URL } from 'node:url';
@@ -8,6 +9,28 @@ import { createLogger } from '@/utils/logger';
 
 import { ControllerModule, ipcClientEvent } from './index';
 
+/**
+ * Non-retryable OIDC error codes
+ * These errors indicate the refresh token is invalid and retry won't help
+ */
+const NON_RETRYABLE_OIDC_ERRORS = [
+  'invalid_grant', // refresh token is invalid, expired, or revoked
+  'invalid_client', // client configuration error
+  'unauthorized_client', // client not authorized
+  'access_denied', // user denied access
+  'invalid_scope', // requested scope is invalid
+];
+
+/**
+ * Deterministic failures that will never succeed on retry
+ * These are permanent state issues that require user intervention
+ */
+const DETERMINISTIC_FAILURES = [
+  'no refresh token available', // refresh token is missing from storage
+  'remote server is not active or configured', // config is invalid or disabled
+  'missing tokens in refresh response', // server returned incomplete response
+];
+
 // Create logger
 const logger = createLogger('controllers:RemoteServerConfigCtr');
 
@@ -246,9 +269,34 @@ export default class RemoteServerConfigCtr extends ControllerModule {
   }
 
   /**
-   * Refresh access token
+   * Check if an error is non-retryable
+   * Includes OIDC errors (e.g., invalid_grant) and deterministic failures
+   * (e.g., missing refresh token, invalid config)
+   * @param error Error message to check
+   * @returns true if the error should not be retried
+   */
+  isNonRetryableError(error?: string): boolean {
+    if (!error) return false;
+    const lowerError = error.toLowerCase();
+
+    // Check OIDC error codes
+    if (NON_RETRYABLE_OIDC_ERRORS.some((code) => lowerError.includes(code))) {
+      return true;
+    }
+
+    // Check deterministic failures that require user intervention
+    if (DETERMINISTIC_FAILURES.some((msg) => lowerError.includes(msg))) {
+      return true;
+    }
+
+    return false;
+  }
+
+  /**
+   * Refresh access token with retry mechanism
    * Use stored refresh token to obtain a new access token
    * Handles concurrent requests by returning the existing refresh promise if one is in progress.
+   * Retries up to 3 times with exponential backoff for transient errors.
    */
   async refreshAccessToken(): Promise<{ error?: string; success: boolean }> {
     // If a refresh is already in progress, return the existing promise
@@ -257,14 +305,62 @@ export default class RemoteServerConfigCtr extends ControllerModule {
       return this.refreshPromise;
     }
 
-    // Start a new refresh operation
-    logger.info('Initiating new token refresh operation.');
-    this.refreshPromise = this.performTokenRefresh();
+    // Start a new refresh operation with retry
+    logger.info('Initiating new token refresh operation with retry.');
+    this.refreshPromise = this.performTokenRefreshWithRetry();
 
     // Return the promise so callers can wait
     return this.refreshPromise;
   }
 
+  /**
+   * Performs token refresh with retry mechanism
+   * Uses exponential backoff: 1s, 2s, 4s
+   */
+  private async performTokenRefreshWithRetry(): Promise<{ error?: string; success: boolean }> {
+    try {
+      return await retry(
+        async (bail, attemptNumber) => {
+          logger.debug(`Token refresh attempt ${attemptNumber}/3`);
+
+          const result = await this.performTokenRefresh();
+
+          if (result.success) {
+            return result;
+          }
+
+          // Check if error is non-retryable
+          if (this.isNonRetryableError(result.error)) {
+            logger.warn(`Non-retryable error encountered: ${result.error}`);
+            // Use bail to stop retrying immediately
+            bail(new Error(result.error));
+            return result; // This won't be reached, but TypeScript needs it
+          }
+
+          // Throw error to trigger retry for transient errors
+          throw new Error(result.error);
+        },
+        {
+          factor: 2, // Exponential backoff factor
+          maxTimeout: 4000, // Max wait time between retries: 4s
+          minTimeout: 1000, // Min wait time between retries: 1s
+          onRetry: (err: Error, attempt: number) => {
+            logger.info(`Token refresh retry ${attempt}/3: ${err.message}`);
+          },
+          retries: 3, // Total retry attempts
+        },
+      );
+    } catch (error) {
+      const errorMessage = error instanceof Error ? error.message : String(error);
+      logger.error('Token refresh failed after all retries:', errorMessage);
+      return { error: errorMessage, success: false };
+    } finally {
+      // Ensure the promise reference is cleared once the operation completes
+      logger.debug('Clearing the refresh promise reference.');
+      this.refreshPromise = null;
+    }
+  }
+
   /**
    * Performs the actual token refresh logic.
    * This method is called by refreshAccessToken and wrapped in a promise.
@@ -337,10 +433,6 @@ export default class RemoteServerConfigCtr extends ControllerModule {
       const errorMessage = error instanceof Error ? error.message : String(error);
       logger.error('Exception during token refresh operation:', errorMessage, error);
       return { error: `Exception occurred during token refresh: ${errorMessage}`, success: false };
-    } finally {
-      // Ensure the promise reference is cleared once the operation completes
-      logger.debug('Clearing the refresh promise reference.');
-      this.refreshPromise = null;
     }
   }
 
diff --git a/apps/desktop/src/main/controllers/__tests__/RemoteServerConfigCtr.test.ts b/apps/desktop/src/main/controllers/__tests__/RemoteServerConfigCtr.test.ts
index b854e88365f..9d562827b20 100644
--- a/apps/desktop/src/main/controllers/__tests__/RemoteServerConfigCtr.test.ts
+++ b/apps/desktop/src/main/controllers/__tests__/RemoteServerConfigCtr.test.ts
@@ -355,6 +355,41 @@ describe('RemoteServerConfigCtr', () => {
     });
   });
 
+  describe('isNonRetryableError', () => {
+    it('should return false for null/undefined error', () => {
+      expect(controller.isNonRetryableError(undefined)).toBe(false);
+      expect(controller.isNonRetryableError('')).toBe(false);
+    });
+
+    it('should return true for OIDC error codes', () => {
+      expect(controller.isNonRetryableError('invalid_grant')).toBe(true);
+      expect(controller.isNonRetryableError('Token refresh failed: invalid_client')).toBe(true);
+      expect(controller.isNonRetryableError('unauthorized_client error')).toBe(true);
+      expect(controller.isNonRetryableError('access_denied by user')).toBe(true);
+      expect(controller.isNonRetryableError('invalid_scope requested')).toBe(true);
+    });
+
+    it('should return true for deterministic failures', () => {
+      expect(controller.isNonRetryableError('No refresh token available')).toBe(true);
+      expect(controller.isNonRetryableError('Remote server is not active or configured')).toBe(
+        true,
+      );
+      expect(controller.isNonRetryableError('Missing tokens in refresh response')).toBe(true);
+    });
+
+    it('should return false for transient/network errors', () => {
+      expect(controller.isNonRetryableError('Network error')).toBe(false);
+      expect(controller.isNonRetryableError('fetch failed')).toBe(false);
+      expect(controller.isNonRetryableError('ETIMEDOUT')).toBe(false);
+      expect(controller.isNonRetryableError('Connection refused')).toBe(false);
+    });
+
+    it('should be case insensitive', () => {
+      expect(controller.isNonRetryableError('INVALID_GRANT')).toBe(true);
+      expect(controller.isNonRetryableError('NO REFRESH TOKEN AVAILABLE')).toBe(true);
+    });
+  });
+
   describe('refreshAccessToken', () => {
     let mockFetch: ReturnType<typeof vi.fn>;
 
@@ -556,7 +591,7 @@ describe('RemoteServerConfigCtr', () => {
       expect(mockFetch).toHaveBeenCalledTimes(1);
     });
 
-    it('should handle network errors', async () => {
+    it('should handle network errors with retry', async () => {
       const { safeStorage } = await import('electron');
       vi.mocked(safeStorage.isEncryptionAvailable).mockReturnValue(true);
       vi.mocked(safeStorage.decryptString).mockImplementation((buffer: Buffer) =>
@@ -582,7 +617,9 @@ describe('RemoteServerConfigCtr', () => {
 
       expect(result.success).toBe(false);
       expect(result.error).toContain('Network error');
-    });
+      // With retry mechanism, fetch should be called 4 times (1 initial + 3 retries)
+      expect(mockFetch).toHaveBeenCalledTimes(4);
+    }, 15000);
   });
 
   describe('afterAppReady', () => {
diff --git a/packages/database/src/server/models/__tests__/adapter.test.ts b/packages/database/src/server/models/__tests__/adapter.test.ts
index 60bc9ab1943..aaa06d23a3f 100644
--- a/packages/database/src/server/models/__tests__/adapter.test.ts
+++ b/packages/database/src/server/models/__tests__/adapter.test.ts
@@ -16,20 +16,20 @@ import {
 
 let serverDB = await getTestDBInstance();
 
-// 测试数据
+// Test data
 const testModelName = 'Session';
 const testId = 'test-id';
 const testUserId = 'test-user-id';
 const testClientId = 'test-client-id';
 const testGrantId = 'test-grant-id';
 const testUserCode = 'test-user-code';
-const testExpires = new Date(Date.now() + 3600 * 1000); // 1小时后过期
+const testExpires = new Date(Date.now() + 3600 * 1000); // Expires in 1 hour
 
 beforeEach(async () => {
   await serverDB.insert(users).values({ id: testUserId }).onConflictDoNothing();
 });
 
-// 每次测试后清理数据
+// Clean up data after each test
 afterEach(async () => {
   await serverDB.delete(users);
   await serverDB.delete(oidcClients);
@@ -39,14 +39,14 @@ afterEach(async () => {
 
 describe('DrizzleAdapter', () => {
   describe('constructor', () => {
-    it('应该正确创建适配器实例', () => {
+    it('should create adapter instance correctly', () => {
       const adapter = new DrizzleAdapter(testModelName, serverDB);
       expect(adapter).toBeDefined();
     });
   });
 
   describe('upsert', () => {
-    it('应该为Session模型创建新记录', async () => {
+    it('should create new record for Session model', async () => {
       const adapter = new DrizzleAdapter('Session', serverDB);
       const payload = {
         accountId: testUserId,
@@ -66,7 +66,7 @@ describe('DrizzleAdapter', () => {
       expect(result?.data).toEqual(payload);
     });
 
-    it('应该为Client模型创建新记录', async () => {
+    it('should create new record for Client model', async () => {
       const adapter = new DrizzleAdapter('Client', serverDB);
       const payload = {
         client_id: testClientId,
@@ -94,7 +94,7 @@ describe('DrizzleAdapter', () => {
       expect(result?.scopes).toEqual(['openid', 'profile', 'email']);
     });
 
-    it('应该为AccessToken模型创建新记录', async () => {
+    it('should create new record for AccessToken model', async () => {
       const adapter = new DrizzleAdapter('AccessToken', serverDB);
       const payload = {
         accountId: testUserId,
@@ -118,7 +118,7 @@ describe('DrizzleAdapter', () => {
       expect(result?.data).toEqual(payload);
     });
 
-    it('应该为DeviceCode模型创建新记录并包含userCode', async () => {
+    it('should create new record for DeviceCode model with userCode', async () => {
       const adapter = new DrizzleAdapter('DeviceCode', serverDB);
       const payload = {
         clientId: testClientId,
@@ -139,30 +139,30 @@ describe('DrizzleAdapter', () => {
       expect(result?.data).toEqual(payload);
     });
 
-    it('应该更新现有的Session记录', async () => {
+    it('should update existing Session record', async () => {
       const adapter = new DrizzleAdapter('Session', serverDB);
       const initialPayload = { accountId: testUserId, cookie: 'initial-cookie' };
       const updatedPayload = { accountId: testUserId, cookie: 'updated-cookie' };
 
-      // 初始插入
+      // Initial insert
       await adapter.upsert(testId, initialPayload, 3600);
       let result = await serverDB.query.oidcSessions.findFirst({
         where: eq(oidcSessions.id, testId),
       });
       expect(result?.data).toEqual(initialPayload);
 
-      // 更新
-      await adapter.upsert(testId, updatedPayload, 7200); // 新的过期时间
+      // Update
+      await adapter.upsert(testId, updatedPayload, 7200); // New expiration time
       result = await serverDB.query.oidcSessions.findFirst({ where: eq(oidcSessions.id, testId) });
       expect(result?.data).toEqual(updatedPayload);
-      // 验证 expiresAt 是否也更新了 (大约 2 小时后)
+      // Verify expiresAt is also updated (approximately 2 hours later)
       expect(result?.expiresAt).toBeInstanceOf(Date);
       const expectedExpires = Date.now() + 7200 * 1000;
-      expect(result!.expiresAt!.getTime()).toBeGreaterThan(expectedExpires - 5000); // 允许 5 秒误差
+      expect(result!.expiresAt!.getTime()).toBeGreaterThan(expectedExpires - 5000); // Allow 5 second tolerance
       expect(result!.expiresAt!.getTime()).toBeLessThan(expectedExpires + 5000);
     });
 
-    it('应该更新现有的Client记录', async () => {
+    it('should update existing Client record', async () => {
       const adapter = new DrizzleAdapter('Client', serverDB);
       const initialPayload = {
         client_id: testClientId,
@@ -175,12 +175,12 @@ describe('DrizzleAdapter', () => {
         ...initialPayload,
         client_uri: 'https://updated.com',
         name: 'Updated Client',
-        scopes: ['openid', 'profile'], // 假设 scope 格式是空格分隔字符串
+        scopes: ['openid', 'profile'],
         scope: 'openid profile',
         redirectUris: ['https://updated.com/callback'],
       };
 
-      // 初始插入
+      // Initial insert
       await adapter.upsert(testClientId, initialPayload, 0);
       let result = await serverDB.query.oidcClients.findFirst({
         where: eq(oidcClients.id, testClientId),
@@ -190,21 +190,20 @@ describe('DrizzleAdapter', () => {
       expect(result?.clientUri).toBe('https://initial.com');
       expect(result?.scopes).toEqual(['openid']);
 
-      // 更新
+      // Update
       await adapter.upsert(testClientId, updatedPayload, 0);
       result = await serverDB.query.oidcClients.findFirst({
         where: eq(oidcClients.id, testClientId),
       });
       expect(result?.name).toBe('Updated Client');
       expect(result?.clientUri).toBe('https://updated.com');
-      expect(result?.scopes).toEqual(['openid', 'profile']); // 验证数据库中存储的是数组
+      expect(result?.scopes).toEqual(['openid', 'profile']);
       expect(result?.redirectUris).toEqual(['https://updated.com/callback']);
     });
   });
 
   describe('find', () => {
-    it('应该找到存在的记录', async () => {
-      // 先创建一个记录
+    it('should find existing record', async () => {
       const adapter = new DrizzleAdapter('Session', serverDB);
       const payload = {
         accountId: testUserId,
@@ -214,15 +213,13 @@ describe('DrizzleAdapter', () => {
 
       await adapter.upsert(testId, payload, 3600);
 
-      // 然后查找它
       const result = await adapter.find(testId);
 
       expect(result).toBeDefined();
       expect(result).toEqual(payload);
     });
 
-    it('应该为Client模型返回正确的格式', async () => {
-      // 先创建一个Client记录
+    it('should return correct format for Client model', async () => {
       const adapter = new DrizzleAdapter('Client', serverDB);
       const payload = {
         client_id: testClientId,
@@ -239,7 +236,6 @@ describe('DrizzleAdapter', () => {
 
       await adapter.upsert(testClientId, payload, 0);
 
-      // 然后查找它
       const result = await adapter.find(testClientId);
 
       expect(result).toBeDefined();
@@ -249,50 +245,87 @@ describe('DrizzleAdapter', () => {
       expect(result.scope).toBe(payload.scope);
     });
 
-    it('应该返回undefined如果记录不存在', async () => {
+    it('should return undefined if record does not exist', async () => {
       const adapter = new DrizzleAdapter('Session', serverDB);
       const result = await adapter.find('non-existent-id');
       expect(result).toBeUndefined();
     });
 
-    it('应该返回undefined如果记录已过期', async () => {
-      // 创建一个过期的记录（过期时间设为过去）
+    it('should return undefined if record is expired', async () => {
       const adapter = new DrizzleAdapter('Session', serverDB);
       const payload = {
         accountId: testUserId,
         cookie: 'cookie-value',
-        exp: Math.floor(Date.now() / 1000) - 3600, // 1小时前
+        exp: Math.floor(Date.now() / 1000) - 3600, // 1 hour ago
       };
 
-      // 负的过期时间表示立即过期
+      // Negative expiration time means immediate expiration
       await adapter.upsert(testId, payload, -1);
 
-      // 等待一小段时间确保过期
+      // Wait briefly to ensure expiration
       await new Promise((resolve) => setTimeout(resolve, 10));
 
-      // 然后查找它
       const result = await adapter.find(testId);
 
       expect(result).toBeUndefined();
     });
 
-    it('应该返回undefined如果记录已被消费', async () => {
+    it('should return undefined if record is consumed', async () => {
       const adapter = new DrizzleAdapter('AccessToken', serverDB);
       const payload = { accountId: testUserId, clientId: testClientId };
       await adapter.upsert(testId, payload, 3600);
 
-      // 消费记录
+      // Consume the record
       await adapter.consume(testId);
 
-      // 查找已消费记录
+      // Find consumed record
+      const result = await adapter.find(testId);
+      expect(result).toBeUndefined();
+    });
+
+    it('should allow RefreshToken reuse within grace period', async () => {
+      const adapter = new DrizzleAdapter('RefreshToken', serverDB);
+      const payload = {
+        accountId: testUserId,
+        clientId: testClientId,
+        grantId: testGrantId,
+      };
+      await adapter.upsert(testId, payload, 3600);
+
+      // Consume the record
+      await adapter.consume(testId);
+
+      // Within grace period (180 seconds), should still find the record
+      const result = await adapter.find(testId);
+      expect(result).toBeDefined();
+      expect(result).toEqual(payload);
+    });
+
+    it('should reject RefreshToken reuse after grace period expires', async () => {
+      const adapter = new DrizzleAdapter('RefreshToken', serverDB);
+      const payload = {
+        accountId: testUserId,
+        clientId: testClientId,
+        grantId: testGrantId,
+      };
+      await adapter.upsert(testId, payload, 3600);
+
+      // Directly update consumedAt to a past time (beyond grace period)
+      // Grace period is 180 seconds, set to 200 seconds ago
+      const pastConsumedAt = new Date(Date.now() - 200 * 1000);
+      await serverDB
+        .update(oidcRefreshTokens)
+        .set({ consumedAt: pastConsumedAt })
+        .where(eq(oidcRefreshTokens.id, testId));
+
+      // Grace period expired, should return undefined
       const result = await adapter.find(testId);
       expect(result).toBeUndefined();
     });
   });
 
   describe('findByUserCode', () => {
-    it('应该通过userCode找到DeviceCode记录', async () => {
-      // 先创建一个DeviceCode记录
+    it('should find DeviceCode record by userCode', async () => {
       const adapter = new DrizzleAdapter('DeviceCode', serverDB);
       const payload = {
         clientId: testClientId,
@@ -302,46 +335,44 @@ describe('DrizzleAdapter', () => {
 
       await adapter.upsert(testId, payload, 3600);
 
-      // 然后通过userCode查找它
       const result = await adapter.findByUserCode(testUserCode);
 
       expect(result).toBeDefined();
       expect(result).toEqual(payload);
     });
 
-    it('应该返回undefined如果DeviceCode记录已过期', async () => {
+    it('should return undefined if DeviceCode record is expired', async () => {
       const adapter = new DrizzleAdapter('DeviceCode', serverDB);
       const payload = { clientId: testClientId, userCode: testUserCode };
-      // 使用负数 expiresIn 使其立即过期
+      // Use negative expiresIn to make it expire immediately
       await adapter.upsert(testId, payload, -1);
-      await new Promise((resolve) => setTimeout(resolve, 10)); // 短暂等待确保过期
+      await new Promise((resolve) => setTimeout(resolve, 10)); // Brief wait to ensure expiration
 
       const result = await adapter.findByUserCode(testUserCode);
       expect(result).toBeUndefined();
     });
 
-    it('应该返回undefined如果DeviceCode记录已被消费', async () => {
+    it('should return undefined if DeviceCode record is consumed', async () => {
       const adapter = new DrizzleAdapter('DeviceCode', serverDB);
       const payload = { clientId: testClientId, userCode: testUserCode };
       await adapter.upsert(testId, payload, 3600);
 
-      // 消费记录
+      // Consume the record
       await adapter.consume(testId);
 
-      // 查找已消费记录
+      // Find consumed record
       const result = await adapter.findByUserCode(testUserCode);
       expect(result).toBeUndefined();
     });
 
-    it('应该在非DeviceCode模型上抛出错误', async () => {
+    it('should throw error on non-DeviceCode model', async () => {
       const adapter = new DrizzleAdapter('Session', serverDB);
       await expect(adapter.findByUserCode(testUserCode)).rejects.toThrow();
     });
   });
 
   describe('findSessionByUserId', () => {
-    it('应该通过userId找到Session记录', async () => {
-      // 先创建一个Session记录
+    it('should find Session record by userId', async () => {
       const adapter = new DrizzleAdapter('Session', serverDB);
       const payload = {
         accountId: testUserId,
@@ -351,14 +382,13 @@ describe('DrizzleAdapter', () => {
 
       await adapter.upsert(testId, payload, 3600);
 
-      // 然后通过userId查找它
       const result = await adapter.findSessionByUserId(testUserId);
 
       expect(result).toBeDefined();
       expect(result).toEqual(payload);
     });
 
-    it('应该在非Session模型上返回undefined', async () => {
+    it('should return undefined on non-Session model', async () => {
       const adapter = new DrizzleAdapter('AccessToken', serverDB);
       const result = await adapter.findSessionByUserId(testUserId);
       expect(result).toBeUndefined();
@@ -366,8 +396,7 @@ describe('DrizzleAdapter', () => {
   });
 
   describe('destroy', () => {
-    it('应该删除存在的记录', async () => {
-      // 先创建一个记录
+    it('should delete existing record', async () => {
       const adapter = new DrizzleAdapter('Session', serverDB);
       const payload = {
         accountId: testUserId,
@@ -377,16 +406,16 @@ describe('DrizzleAdapter', () => {
 
       await adapter.upsert(testId, payload, 3600);
 
-      // 确认记录存在
+      // Confirm record exists
       let result = await serverDB.query.oidcSessions.findFirst({
         where: eq(oidcSessions.id, testId),
       });
       expect(result).toBeDefined();
 
-      // 删除记录
+      // Delete record
       await adapter.destroy(testId);
 
-      // 验证记录已被删除
+      // Verify record is deleted
       result = await serverDB.query.oidcSessions.findFirst({
         where: eq(oidcSessions.id, testId),
       });
@@ -395,8 +424,7 @@ describe('DrizzleAdapter', () => {
   });
 
   describe('consume', () => {
-    it('应该标记记录为已消费', async () => {
-      // 先创建一个记录
+    it('should mark record as consumed', async () => {
       const adapter = new DrizzleAdapter('AccessToken', serverDB);
       const payload = {
         accountId: testUserId,
@@ -406,10 +434,10 @@ describe('DrizzleAdapter', () => {
 
       await adapter.upsert(testId, payload, 3600);
 
-      // 消费记录
+      // Consume the record
       await adapter.consume(testId);
 
-      // 验证记录已被标记为已消费
+      // Verify record is marked as consumed
       const result = await serverDB.query.oidcAccessTokens.findFirst({
         where: eq(oidcAccessTokens.id, testId),
       });
@@ -420,8 +448,8 @@ describe('DrizzleAdapter', () => {
   });
 
   describe('revokeByGrantId', () => {
-    it('应该撤销与指定 grantId 相关的所有记录', async () => {
-      // 创建AccessToken记录
+    it('should revoke all records associated with specified grantId', async () => {
+      // Create AccessToken record
       const accessTokenAdapter = new DrizzleAdapter('AccessToken', serverDB);
       const accessTokenPayload = {
         accountId: testUserId,
@@ -431,7 +459,7 @@ describe('DrizzleAdapter', () => {
       };
       await accessTokenAdapter.upsert(testId, accessTokenPayload, 3600);
 
-      // 创建RefreshToken记录
+      // Create RefreshToken record
       const refreshTokenAdapter = new DrizzleAdapter('RefreshToken', serverDB);
       const refreshTokenPayload = {
         accountId: testUserId,
@@ -441,10 +469,10 @@ describe('DrizzleAdapter', () => {
       };
       await refreshTokenAdapter.upsert('refresh-' + testId, refreshTokenPayload, 3600);
 
-      // 撤销与testGrantId相关的所有记录
+      // Revoke all records associated with testGrantId
       await accessTokenAdapter.revokeByGrantId(testGrantId);
 
-      // 验证记录已被删除
+      // Verify records are deleted
       const accessTokenResult = await serverDB.query.oidcAccessTokens.findFirst({
         where: eq(oidcAccessTokens.id, testId),
       });
@@ -458,16 +486,16 @@ describe('DrizzleAdapter', () => {
       expect(refreshTokenResult).toBeUndefined();
     });
 
-    it('应该在Grant模型上直接返回', async () => {
-      // Grant模型不需要通过grantId来撤销
+    it('should return directly on Grant model', async () => {
+      // Grant model does not need to be revoked by grantId
       const adapter = new DrizzleAdapter('Grant', serverDB);
       await adapter.revokeByGrantId(testGrantId);
-      // 如果没有抛出错误，测试通过
+      // Test passes if no error is thrown
     });
   });
 
   describe('createAdapterFactory', () => {
-    it('应该创建一个适配器工厂函数', () => {
+    it('should create an adapter factory function', () => {
       const factory = DrizzleAdapter.createAdapterFactory(serverDB as any);
       expect(factory).toBeDefined();
       expect(typeof factory).toBe('function');
@@ -479,9 +507,9 @@ describe('DrizzleAdapter', () => {
   });
 
   describe('getTable (indirectly via public methods)', () => {
-    it('当使用不支持的模型名称时应该抛出错误', async () => {
+    it('should throw error when using unsupported model name', async () => {
       const invalidAdapter = new DrizzleAdapter('InvalidModelName', serverDB);
-      // 调用一个会触发 getTable 的方法
+      // Call a method that triggers getTable
       await expect(invalidAdapter.find('any-id')).rejects.toThrow('不支持的模型: InvalidModelName');
       await expect(invalidAdapter.upsert('any-id', {}, 3600)).rejects.toThrow(
         '不支持的模型: InvalidModelName',
diff --git a/src/libs/oidc-provider/adapter.ts b/src/libs/oidc-provider/adapter.ts
index 5e71546f4a0..4a915415de6 100644
--- a/src/libs/oidc-provider/adapter.ts
+++ b/src/libs/oidc-provider/adapter.ts
@@ -15,6 +15,20 @@ import { eq, sql } from 'drizzle-orm';
 // 创建 adapter 日志命名空间
 const log = debug('lobe-oidc:adapter');
 
+/**
+ * Grace period for consumed RefreshToken (in seconds)
+ *
+ * When rotateRefreshToken is enabled, the old refresh token is consumed
+ * when a new one is issued. However, if the client fails to receive/save
+ * the new token (network issues, crashes), the old token becomes unusable.
+ *
+ * This grace period allows the consumed refresh token to be reused within
+ * a short window, giving clients a chance to retry the refresh operation.
+ *
+ * Default: 180 seconds (3 minutes)
+ */
+const REFRESH_TOKEN_GRACE_PERIOD_SECONDS = 180;
+
 class OIDCAdapter {
   private db: LobeChatDatabase;
   private name: string;
@@ -278,8 +292,35 @@ class OIDCAdapter {
         return undefined;
       }
 
-      // 如果记录已被消费，返回 undefined
+      // 如果记录已被消费，检查是否在宽限期内
       if (model.consumedAt) {
+        // For RefreshToken, allow reuse within grace period
+        if (this.name === 'RefreshToken') {
+          const consumedAt = new Date(model.consumedAt);
+          const gracePeriodEnd = new Date(
+            consumedAt.getTime() + REFRESH_TOKEN_GRACE_PERIOD_SECONDS * 1000,
+          );
+          const now = new Date();
+
+          if (now <= gracePeriodEnd) {
+            // Within grace period, allow reuse for retry scenarios
+            log(
+              '[RefreshToken] Token consumed at %s but within grace period (ends %s), allowing reuse',
+              consumedAt.toISOString(),
+              gracePeriodEnd.toISOString(),
+            );
+            return model.data;
+          }
+
+          log(
+            '[RefreshToken] Token consumed at %s, grace period expired at %s, returning undefined',
+            consumedAt.toISOString(),
+            gracePeriodEnd.toISOString(),
+          );
+          return undefined;
+        }
+
+        // For other token types, consumed means invalid
         log(
           '[%s] Record already consumed (consumedAt: %s), returning undefined',
           this.name,

PATCH

echo "Patch applied successfully."

#!/usr/bin/env bash
# Gold patch for Infisical PR #5653 — enrich PostHog org groupIdentify
# with plan, is_cloud, seat_count, created_at properties.
set -euo pipefail

cd /workspace/infisical

# Idempotency guard: if the gold patch is already applied, exit 0.
if grep -q "getOrgGroupProperties" backend/src/services/telemetry/telemetry-service.ts 2>/dev/null; then
    echo "Patch already applied; skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/backend/src/server/routes/index.ts b/backend/src/server/routes/index.ts
index 95172f8dba2..866f1bd3b52 100644
--- a/backend/src/server/routes/index.ts
+++ b/backend/src/server/routes/index.ts
@@ -945,7 +945,8 @@ export const registerRoutes = async (

   const telemetryService = telemetryServiceFactory({
     keyStore,
-    licenseService
+    licenseService,
+    orgDAL
   });
   const telemetryQueue = telemetryQueueServiceFactory({
     keyStore,
diff --git a/backend/src/services/telemetry/telemetry-service.ts b/backend/src/services/telemetry/telemetry-service.ts
index fb891f6621e..9d21e82b166 100644
--- a/backend/src/services/telemetry/telemetry-service.ts
+++ b/backend/src/services/telemetry/telemetry-service.ts
@@ -8,6 +8,7 @@ import { getConfig } from "@app/lib/config/env";
 import { request } from "@app/lib/config/request";
 import { crypto } from "@app/lib/crypto/cryptography";
 import { logger } from "@app/lib/logger";
+import { TOrgDALFactory } from "@app/services/org/org-dal";

 import { PostHogEventTypes, TPostHogEvent, TSecretModifiedEvent } from "./telemetry-types";

@@ -39,7 +40,8 @@ export type TTelemetryServiceFactoryDep = {
     TKeyStoreFactory,
     "incrementBy" | "deleteItemsByKeyIn" | "setItemWithExpiry" | "getKeysByPattern" | "getItems"
   >;
-  licenseService: Pick<TLicenseServiceFactory, "getInstanceType">;
+  licenseService: Pick<TLicenseServiceFactory, "getInstanceType" | "getPlan">;
+  orgDAL: Pick<TOrgDALFactory, "findOrgById">;
 };

 const getBucketForDistinctId = (distinctId: string): string => {
@@ -58,7 +60,7 @@ export const createTelemetryEventKey = (event: string, distinctId: string): stri
   return `telemetry-event-${event}-${bucketId}-${distinctId}-${crypto.nativeCrypto.randomUUID()}`;
 };

-export const telemetryServiceFactory = ({ keyStore, licenseService }: TTelemetryServiceFactoryDep) => {
+export const telemetryServiceFactory = ({ keyStore, licenseService, orgDAL }: TTelemetryServiceFactoryDep) => {
   const appCfg = getConfig();

   if (appCfg.isProductionMode && !appCfg.TELEMETRY_ENABLED) {
@@ -99,6 +101,38 @@ To opt into telemetry, you can set "TELEMETRY_ENABLED=true" within the environme
     }
   };

+  const getOrgGroupProperties = async (orgId: string, orgName?: string): Promise<Record<string, unknown>> => {
+    const properties: Record<string, unknown> = {};
+    if (orgName) {
+      properties.name = orgName;
+    }
+
+    const instanceType = licenseService.getInstanceType();
+    properties.is_cloud = instanceType === InstanceType.Cloud;
+
+    try {
+      const org = await orgDAL.findOrgById(orgId);
+      if (org) {
+        if (!properties.name) {
+          properties.name = org.name;
+        }
+        properties.created_at = org.createdAt.toISOString();
+      }
+    } catch (error) {
+      logger.error(error, "Failed to fetch org details for PostHog group properties");
+    }
+
+    try {
+      const plan = await licenseService.getPlan(orgId);
+      properties.plan = plan.slug ?? "free";
+      properties.seat_count = plan.membersUsed;
+    } catch (error) {
+      logger.error(error, "Failed to fetch org plan for PostHog group properties");
+    }
+
+    return properties;
+  };
+
   const sendPostHogEvents = async (event: TPostHogEvent) => {
     if (postHog) {
       const instanceType = licenseService.getInstanceType();
@@ -123,15 +157,19 @@ To opt into telemetry, you can set "TELEMETRY_ENABLED=true" within the environme
           );
         } else {
           if (event.organizationId) {
-            try {
-              postHog.groupIdentify({
-                groupType: "organization",
-                groupKey: event.organizationId,
-                ...(resolvedOrgName ? { properties: { name: resolvedOrgName } } : {})
+            // Fire-and-forget: enrich groupIdentify without blocking the HTTP response
+            const orgId = event.organizationId;
+            void getOrgGroupProperties(orgId, resolvedOrgName)
+              .then((groupProperties) => {
+                postHog.groupIdentify({
+                  groupType: "organization",
+                  groupKey: orgId,
+                  properties: groupProperties
+                });
+              })
+              .catch((error) => {
+                logger.error(error, "Failed to identify PostHog organization");
               });
-            } catch (error) {
-              logger.error(error, "Failed to identify PostHog organization");
-            }
           }
           postHog.capture({
             event: event.event,
@@ -261,16 +299,26 @@ To opt into telemetry, you can set "TELEMETRY_ENABLED=true" within the environme

       if (eventsGrouped.size === 0) return 0;

+      // Cache org group properties per orgId to avoid redundant DB/API calls
+      // when multiple users share the same org within a bucket
+      const orgPropertiesCache = new Map<string, Record<string, unknown>>();
+
       for (const [eventsKey, events] of eventsGrouped) {
         const key = JSON.parse(eventsKey) as { id: string; org?: string };
         if (key.org) {
           try {
-            // Use the organizationName from the first event in the group (all events in a group share the same org)
-            const orgName = events[0]?.organizationName;
+            let groupProperties = orgPropertiesCache.get(key.org);
+            if (!groupProperties) {
+              // Use the organizationName from the first event in the group (all events in a group share the same org)
+              const orgName = events[0]?.organizationName;
+              // eslint-disable-next-line no-await-in-loop
+              groupProperties = await getOrgGroupProperties(key.org, orgName);
+              orgPropertiesCache.set(key.org, groupProperties);
+            }
             postHog.groupIdentify({
               groupType: "organization",
               groupKey: key.org,
-              ...(orgName ? { properties: { name: orgName } } : {})
+              properties: groupProperties
             });
           } catch (error) {
             logger.error(error, "Failed to identify PostHog organization");
PATCH

echo "Patch applied successfully."

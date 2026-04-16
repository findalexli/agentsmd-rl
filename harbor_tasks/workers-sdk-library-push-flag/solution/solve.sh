#!/bin/bash
set -e

cd /workspace/workers-sdk

# Apply the gold patch for adding --library-push flag
cat <<'PATCH' | git apply -
diff --git a/packages/containers-shared/src/client/models/ImageRegistryPermissions.ts b/packages/containers-shared/src/client/models/ImageRegistryPermissions.ts
index 239216f2b4..3cda7f14ae 100644
--- a/packages/containers-shared/src/client/models/ImageRegistryPermissions.ts
+++ b/packages/containers-shared/src/client/models/ImageRegistryPermissions.ts
@@ -5,4 +5,5 @@
 export enum ImageRegistryPermissions {
 	PULL = "pull",
 	PUSH = "push",
+	LIBRARY_PUSH = "library_push",
 }
diff --git a/packages/wrangler/src/containers/registries.ts b/packages/wrangler/src/containers/registries.ts
index 71bc5e9c99..e9d32b9dcf 100644
--- a/packages/wrangler/src/containers/registries.ts
+++ b/packages/wrangler/src/containers/registries.ts
@@ -501,6 +501,7 @@ async function registryCredentialsCommand(credentialsArgs: {
 	expirationMinutes: number;
 	push?: boolean;
 	pull?: boolean;
+	libraryPush?: boolean;
 	json?: boolean;
 }) {
 	const cloudflareRegistry = getCloudflareContainerRegistry();
@@ -511,7 +512,11 @@ async function registryCredentialsCommand(credentialsArgs: {
 		);
 	}

-	if (!credentialsArgs.pull && !credentialsArgs.push) {
+	if (
+		!credentialsArgs.pull &&
+		!credentialsArgs.push &&
+		!credentialsArgs.libraryPush
+	) {
 		throw new UserError(
 			"You have to specify either --push or --pull in the command."
 		);
@@ -523,6 +528,7 @@ async function registryCredentialsCommand(credentialsArgs: {
 			permissions: [
 				...(credentialsArgs.push ? ["push"] : []),
 				...(credentialsArgs.pull ? ["pull"] : []),
+				...(credentialsArgs.libraryPush ? ["library_push"] : []),
 			] as ImageRegistryPermissions[],
 		});
 	if (credentialsArgs.json) {
@@ -623,6 +629,12 @@ export const containersRegistriesCredentialsCommand = createCommand({
 			type: "boolean",
 			description: "If you want these credentials to be able to pull",
 		},
+		"library-push": {
+			type: "boolean",
+			description:
+				"If you want these credentials to be able to push to the public library namespace",
+			hidden: true,
+		},
 		json: {
 			type: "boolean",
 			description: "Format output as JSON",
PATCH

# Rebuild the affected packages
pnpm run build --filter @cloudflare/containers-shared --filter wrangler

echo "Patch applied and built successfully"

#!/usr/bin/env bash
set -euo pipefail

cd /workspace/trigger.dev

# Idempotent: skip if already applied
if grep -q 'normalizeApiUrlForBuild' packages/cli-v3/src/deploy/buildImage.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
index 12e85c33b76..c5ac964558d 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -68,9 +68,9 @@ branch are tagged into a release periodically.
    ```
    pnpm run db:migrate
    ```
-10. Build the server app
+10. Build everything
     ```
-    pnpm run build --filter webapp
+    pnpm run build --filter webapp && pnpm run build --filter trigger.dev && pnpm run build --filter @trigger.dev/sdk
     ```
 11. Run the app. See the section below.

diff --git a/apps/supervisor/README.md b/apps/supervisor/README.md
index 2d225ca186b..86b447269d2 100644
--- a/apps/supervisor/README.md
+++ b/apps/supervisor/README.md
@@ -36,7 +36,7 @@ pnpm dev
 ```

-4. Build CLI, then deploy a reference project
+4. Build CLI, then deploy a test project

 ```sh
 pnpm exec trigger deploy --self-hosted
diff --git a/apps/webapp/app/routes/api.v1.projects.$projectRef.$env.ts b/apps/webapp/app/routes/api.v1.projects.$projectRef.$env.ts
index bfcf174df9c..ad92e0a9951 100644
--- a/apps/webapp/app/routes/api.v1.projects.$projectRef.$env.ts
+++ b/apps/webapp/app/routes/api.v1.projects.$projectRef.$env.ts
@@ -88,7 +88,7 @@ export async function loader({ request, params }: LoaderFunctionArgs) {
   const result: GetProjectEnvResponse = {
     apiKey: runtimeEnv.apiKey,
     name: project.name,
-    apiUrl: processEnv.APP_ORIGIN,
+    apiUrl: processEnv.API_ORIGIN ?? processEnv.APP_ORIGIN,
     projectId: project.id,
   };

diff --git a/packages/cli-v3/src/deploy/buildImage.ts b/packages/cli-v3/src/deploy/buildImage.ts
index 73e377796a7..6721317e409 100644
--- a/packages/cli-v3/src/deploy/buildImage.ts
+++ b/packages/cli-v3/src/deploy/buildImage.ts
@@ -327,7 +327,7 @@ async function selfHostedBuildImage(
     "--build-arg",
     `TRIGGER_PROJECT_REF=${options.projectRef}`,
     "--build-arg",
-    `TRIGGER_API_URL=${options.apiUrl}`,
+    `TRIGGER_API_URL=${normalizeApiUrlForBuild(options.apiUrl)}`,
     "--build-arg",
     `TRIGGER_SECRET_KEY=${options.apiKey}`,
     ...(buildArgs || []),
@@ -723,3 +723,13 @@ ENTRYPOINT [ "dumb-init", "node", "${options.entrypoint}" ]
 CMD []
   `;
 }
+
+// If apiUrl is something like http://localhost:3030, AND we are on macOS, we need to convert it to http://host.docker.internal:3030
+// this way the indexing will work because the docker image can reach the local server
+function normalizeApiUrlForBuild(apiUrl: string) {
+  if (process.platform === "darwin") {
+    return apiUrl.replace("localhost", "host.docker.internal");
+  }
+
+  return apiUrl;
+}

PATCH

echo "Patch applied successfully."

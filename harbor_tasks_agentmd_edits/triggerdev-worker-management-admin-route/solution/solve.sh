#!/usr/bin/env bash
set -euo pipefail

cd /workspace/trigger.dev

# Idempotent: skip if already applied
if grep -q 'removeDefaultFromProject: z.boolean()' apps/webapp/app/routes/admin.api.v1.workers.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/apps/supervisor/README.md b/apps/supervisor/README.md
index e3bad3dcb61..2d225ca186b 100644
--- a/apps/supervisor/README.md
+++ b/apps/supervisor/README.md
@@ -19,6 +19,8 @@ curl -sS \
     -d "{\"name\": \"$wg_name\"}"
 ```

+If the worker group is newly created, the response will include a `token` field. If the group already exists, no token is returned.
+
 2. Create `.env` and set the worker token

 ```sh
@@ -43,16 +45,52 @@ pnpm exec trigger deploy --self-hosted
 pnpm exec trigger deploy --self-hosted --network host
 ```

-## Additional worker groups
+## Worker group management

-When adding more worker groups you might also want to make them the default for a specific project. This will allow you to test it without having to change the global default:
+### Shared variables

 ```sh
 api_url=http://localhost:3030
+admin_pat=tr_pat_... # edit this
+```
+
+- These are used by all commands
+
+### Create a worker group
+
+```sh
 wg_name=my-worker

-# edit these
-admin_pat=tr_pat_...
+curl -sS \
+    -X POST \
+    "$api_url/admin/api/v1/workers" \
+    -H "Authorization: Bearer $admin_pat" \
+    -H "Content-Type: application/json" \
+    -d "{\"name\": \"$wg_name\"}"
+```
+
+- If the worker group already exists, no token will be returned
+
+### Set a worker group as default for a project
+
+```sh
+wg_name=my-worker
+project_id=clsw6q8wz...
+
+curl -sS \
+    -X POST \
+    "$api_url/admin/api/v1/workers" \
+    -H "Authorization: Bearer $admin_pat" \
+    -H "Content-Type: application/json" \
+    -d "{\"name\": \"$wg_name\", \"projectId\": \"$project_id\", \"makeDefaultForProject\": true}"
+```
+
+- If the worker group doesn't exist, yet it will be created
+- If the worker group already exists, it will be attached to the project as default. No token will be returned.
+
+### Remove the default worker group from a project
+
+```sh
 project_id=clsw6q8wz...

 curl -sS \
@@ -60,8 +98,8 @@ curl -sS \
     "$api_url/admin/api/v1/workers" \
     -H "Authorization: Bearer $admin_pat" \
     -H "Content-Type: application/json" \
-    -d "{
-        \"name\": \"$wg_name\",
-        \"makeDefaultForProjectId\": \"$project_id\"
-    }"
+    -d "{\"projectId\": \"$project_id\", \"removeDefaultFromProject\": true}"
 ```
+
+- The project will then use the global default again
+- When `removeDefaultFromProject: true` no other actions will be performed
diff --git a/apps/webapp/app/routes/admin.api.v1.workers.ts b/apps/webapp/app/routes/admin.api.v1.workers.ts
index 9299c0e2c09..b215d8ce223 100644
--- a/apps/webapp/app/routes/admin.api.v1.workers.ts
+++ b/apps/webapp/app/routes/admin.api.v1.workers.ts
@@ -1,4 +1,6 @@
-import { ActionFunctionArgs, json } from "@remix-run/server-runtime";
+import { type ActionFunctionArgs, json } from "@remix-run/server-runtime";
+import { tryCatch } from "@trigger.dev/core";
+import { type Project } from "@trigger.dev/database";
 import { z } from "zod";
 import { prisma } from "~/db.server";
 import { authenticateApiRequestWithPersonalAccessToken } from "~/services/personalAccessToken.server";
@@ -7,7 +9,9 @@ import { WorkerGroupService } from "~/v3/services/worker/workerGroupService.serv
 const RequestBodySchema = z.object({
   name: z.string().optional(),
   description: z.string().optional(),
-  makeDefaultForProjectId: z.string().optional(),
+  projectId: z.string().optional(),
+  makeDefaultForProject: z.boolean().default(false),
+  removeDefaultFromProject: z.boolean().default(false),
 });

 export async function action({ request }: ActionFunctionArgs) {
@@ -18,7 +22,7 @@ export async function action({ request }: ActionFunctionArgs) {
     return json({ error: "Invalid or Missing API key" }, { status: 401 });
   }

-  const user = await prisma.user.findUnique({
+  const user = await prisma.user.findFirst({
     where: {
       id: authenticationResult.userId,
     },
@@ -34,30 +38,207 @@ export async function action({ request }: ActionFunctionArgs) {

   try {
     const rawBody = await request.json();
-    const { name, description, makeDefaultForProjectId } = RequestBodySchema.parse(rawBody ?? {});
+    const { name, description, projectId, makeDefaultForProject, removeDefaultFromProject } =
+      RequestBodySchema.parse(rawBody ?? {});

-    const service = new WorkerGroupService();
-    const { workerGroup, token } = await service.createWorkerGroup({
-      name,
-      description,
+    if (removeDefaultFromProject) {
+      if (!projectId) {
+        return json(
+          {
+            error: "projectId is required to remove default worker group from project",
+          },
+          { status: 400 }
+        );
+      }
+
+      const updated = await removeDefaultWorkerGroupFromProject(projectId);
+
+      if (!updated.success) {
+        return json(
+          { error: `failed to remove default worker group from project: ${updated.error}` },
+          { status: 400 }
+        );
+      }
+
+      return json({
+        outcome: "removed default worker group from project",
+        project: updated.project,
+      });
+    }
+
+    const existingWorkerGroup = await prisma.workerInstanceGroup.findFirst({
+      where: {
+        // We only check managed worker groups
+        masterQueue: name,
+      },
     });

-    if (makeDefaultForProjectId) {
-      await prisma.project.update({
-        where: {
-          id: makeDefaultForProjectId,
+    if (!existingWorkerGroup) {
+      const { workerGroup, token } = await createWorkerGroup(name, description);
+
+      if (!makeDefaultForProject) {
+        return json({
+          outcome: "created new worker group",
+          token,
+          workerGroup,
+        });
+      }
+
+      if (!projectId) {
+        return json(
+          { error: "projectId is required to set worker group as default for project" },
+          { status: 400 }
+        );
+      }
+
+      const updated = await setWorkerGroupAsDefaultForProject(workerGroup.id, projectId);
+
+      if (!updated.success) {
+        return json({ error: updated.error }, { status: 400 });
+      }
+
+      return json({
+        outcome: "set new worker group as default for project",
+        token,
+        workerGroup,
+        project: updated.project,
+      });
+    }
+
+    if (!makeDefaultForProject) {
+      return json(
+        {
+          error: "worker group already exists",
+          workerGroup: existingWorkerGroup,
         },
-        data: {
-          defaultWorkerGroupId: workerGroup.id,
+        { status: 400 }
+      );
+    }
+
+    if (!projectId) {
+      return json(
+        { error: "projectId is required to set worker group as default for project" },
+        { status: 400 }
+      );
+    }
+
+    const updated = await setWorkerGroupAsDefaultForProject(existingWorkerGroup.id, projectId);
+
+    if (!updated.success) {
+      return json(
+        {
+          error: `failed to set worker group as default for project: ${updated.error}`,
+          workerGroup: existingWorkerGroup,
         },
-      });
+        { status: 400 }
+      );
     }

     return json({
-      token,
-      workerGroup,
+      outcome: "set existing worker group as default for project",
+      workerGroup: existingWorkerGroup,
+      project: updated.project,
     });
   } catch (error) {
-    return json({ error: error instanceof Error ? error.message : error }, { status: 400 });
+    return json(
+      {
+        outcome: "unknown error",
+        error: error instanceof Error ? error.message : error,
+      },
+      { status: 400 }
+    );
+  }
+}
+
+async function createWorkerGroup(name: string | undefined, description: string | undefined) {
+  const service = new WorkerGroupService();
+  return await service.createWorkerGroup({ name, description });
+}
+
+async function removeDefaultWorkerGroupFromProject(projectId: string) {
+  const project = await prisma.project.findFirst({
+    where: {
+      id: projectId,
+    },
+  });
+
+  if (!project) {
+    return {
+      success: false,
+      error: "project not found",
+    };
   }
+
+  const [error] = await tryCatch(
+    prisma.project.update({
+      where: {
+        id: projectId,
+      },
+      data: {
+        defaultWorkerGroupId: null,
+      },
+    })
+  );
+
+  if (error) {
+    return {
+      success: false,
+      error: error instanceof Error ? error.message : error,
+    };
+  }
+
+  return {
+    success: true,
+    project,
+  };
+}
+
+async function setWorkerGroupAsDefaultForProject(
+  workerGroupId: string,
+  projectId: string
+): Promise<
+  | {
+      success: false;
+      error: string;
+    }
+  | {
+      success: true;
+      project: Project;
+    }
+> {
+  const project = await prisma.project.findFirst({
+    where: {
+      id: projectId,
+    },
+  });
+
+  if (!project) {
+    return {
+      success: false,
+      error: "project not found",
+    };
+  }
+
+  const [error] = await tryCatch(
+    prisma.project.update({
+      where: {
+        id: projectId,
+      },
+      data: {
+        defaultWorkerGroupId: workerGroupId,
+      },
+    })
+  );
+
+  if (error) {
+    return {
+      success: false,
+      error: error instanceof Error ? error.message : error,
+    };
+  }
+
+  return {
+    success: true,
+    project,
+  };
 }

PATCH

echo "Patch applied successfully."

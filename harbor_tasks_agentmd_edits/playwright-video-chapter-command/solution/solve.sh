#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'browser_video_chapter' packages/playwright-core/src/tools/backend/video.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/docs/src/getting-started-cli.md b/docs/src/getting-started-cli.md
index 6f12199ef695c..8a1bb6e355e48 100644
--- a/docs/src/getting-started-cli.md
+++ b/docs/src/getting-started-cli.md
@@ -200,7 +200,8 @@ playwright-cli run-code <code>          # run Playwright code snippet
 playwright-cli tracing-start            # start trace recording
 playwright-cli tracing-stop             # stop trace recording
 playwright-cli video-start              # start video recording
-playwright-cli video-stop [filename]    # stop video recording
+playwright-cli video-chapter <title>    # add chapter marker to video
+playwright-cli video-stop --filename=f  # stop video recording
 ```

 ## Sessions
diff --git a/packages/playwright-core/src/tools/backend/video.ts b/packages/playwright-core/src/tools/backend/video.ts
index 432be49c258bc..b386b60c7f362 100644
--- a/packages/playwright-core/src/tools/backend/video.ts
+++ b/packages/playwright-core/src/tools/backend/video.ts
@@ -18,7 +18,7 @@ import path from 'path';
 import { z } from '../../zodBundle';
 import { defineTool } from './tool';

-const startVideo = defineTool({
+const videoStart = defineTool({
   capability: 'devtools',

   schema: {
@@ -40,7 +40,7 @@ const startVideo = defineTool({
   },
 });

-const stopVideo = defineTool({
+const videoStop = defineTool({
   capability: 'devtools',

   schema: {
@@ -73,7 +73,33 @@ const stopVideo = defineTool({
   },
 });

+const videoChapter = defineTool({
+  capability: 'devtools',
+
+  schema: {
+    name: 'browser_video_chapter',
+    title: 'Video chapter',
+    description: 'Add a chapter marker to the video recording. Shows a full-screen chapter card with blurred backdrop.',
+    inputSchema: z.object({
+      title: z.string().describe('Chapter title'),
+      description: z.string().optional().describe('Chapter description'),
+      duration: z.number().optional().describe('Duration in milliseconds to show the chapter card'),
+    }),
+    type: 'readOnly',
+  },
+
+  handle: async (context, params, response) => {
+    const tab = context.currentTabOrDie();
+    await tab.page.overlay.chapter(params.title, {
+      description: params.description,
+      duration: params.duration,
+    });
+    response.addTextResult(`Chapter '${params.title}' added.`);
+  },
+});
+
 export default [
-  startVideo,
-  stopVideo,
+  videoStart,
+  videoStop,
+  videoChapter,
 ];
diff --git a/packages/playwright-core/src/tools/cli-client/skill/SKILL.md b/packages/playwright-core/src/tools/cli-client/skill/SKILL.md
index cac4db32a2d55..0515a03a55cb5 100644
--- a/packages/playwright-core/src/tools/cli-client/skill/SKILL.md
+++ b/packages/playwright-core/src/tools/cli-client/skill/SKILL.md
@@ -156,6 +156,7 @@ playwright-cli run-code --filename=script.js
 playwright-cli tracing-start
 playwright-cli tracing-stop
 playwright-cli video-start
+playwright-cli video-chapter "Chapter Title" --description="Details" --duration=2000
 playwright-cli video-stop video.webm
 ```

diff --git a/packages/playwright-core/src/tools/cli-client/skill/references/video-recording.md b/packages/playwright-core/src/tools/cli-client/skill/references/video-recording.md
index 0116ece790e9d..de77603857f61 100644
--- a/packages/playwright-core/src/tools/cli-client/skill/references/video-recording.md
+++ b/packages/playwright-core/src/tools/cli-client/skill/references/video-recording.md
@@ -11,10 +11,16 @@ playwright-cli open
 # Start recording
 playwright-cli video-start

+# Add a chapter marker for section transitions
+playwright-cli video-chapter "Getting Started" --description="Opening the homepage" --duration=2000
+
 # Navigate and perform actions
 playwright-cli goto https://example.com
 playwright-cli snapshot
 playwright-cli click e1
+
+# Add another chapter
+playwright-cli video-chapter "Filling Form" --description="Entering test data" --duration=2000
 playwright-cli fill e2 "test input"

 # Stop and save
diff --git a/packages/playwright-core/src/tools/cli-daemon/commands.ts b/packages/playwright-core/src/tools/cli-daemon/commands.ts
index b9f3398c01c62..0d177522a78ea 100644
--- a/packages/playwright-core/src/tools/cli-daemon/commands.ts
+++ b/packages/playwright-core/src/tools/cli-daemon/commands.ts
@@ -813,6 +813,21 @@ const videoStop = declareCommand({
   toolParams: ({ filename }) => ({ filename }),
 });

+const videoChapter = declareCommand({
+  name: 'video-chapter',
+  description: 'Add a chapter marker to the video recording',
+  category: 'devtools',
+  args: z.object({
+    title: z.string().describe('Chapter title.'),
+  }),
+  options: z.object({
+    description: z.string().optional().describe('Chapter description.'),
+    duration: numberArg.optional().describe('Duration in milliseconds to show the chapter card.'),
+  }),
+  toolName: 'browser_video_chapter',
+  toolParams: ({ title, description, duration }) => ({ title, description, duration }),
+});
+
 const devtoolsShow = declareCommand({
   name: 'show',
   description: 'Show browser DevTools',
@@ -1027,6 +1042,7 @@ const commandsArray: AnyCommandSchema[] = [
   tracingStop,
   videoStart,
   videoStop,
+  videoChapter,
   devtoolsShow,
   pauseAt,
   resume,

PATCH

echo "Patch applied successfully."

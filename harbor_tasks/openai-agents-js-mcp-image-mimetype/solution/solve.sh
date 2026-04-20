#!/usr/bin/env bash
set -euo pipefail

REPO="/workspace/openai-agents-js"
cd "$REPO"

# Idempotency check — skip if already applied
if grep -q 'getImageInlineMediaType' packages/agents-core/src/runner/toolExecution.ts 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/.changeset/fix-mcp-image-mimetype.md b/.changeset/fix-mcp-image-mimetype.md
new file mode 100644
index 000000000..4da7e99b7
--- /dev/null
+++ b/.changeset/fix-mcp-image-mimetype.md
@@ -0,0 +1,6 @@
+---
+'@openai/agents-core': patch
+'@openai/agents-openai': patch
+---
+
+fix: #1070 preserve MCP image mimeType in tool outputs
diff --git a/packages/agents-core/src/runner/toolExecution.ts b/packages/agents-core/src/runner/toolExecution.ts
index 2e4e9621a..790511635 100644
--- a/packages/agents-core/src/runner/toolExecution.ts
+++ b/packages/agents-core/src/runner/toolExecution.ts
@@ -1445,18 +1445,15 @@ function normalizeStructuredToolOutput(

     let imageString: string | undefined;
     let imageFileId: string | undefined;
-    const fallbackImageMediaType = isNonEmptyString((value as any).mediaType)
-      ? (value as any).mediaType
-      : undefined;
+    const fallbackImageMediaType = getImageInlineMediaType(value);

     const imageField = value.image;
     if (typeof imageField === 'string' && imageField.length > 0) {
       imageString = imageField;
     } else if (isRecord(imageField)) {
       const imageObj = imageField as Record<string, any>;
-      const inlineMediaType = isNonEmptyString(imageObj.mediaType)
-        ? imageObj.mediaType
-        : fallbackImageMediaType;
+      const inlineMediaType =
+        getImageInlineMediaType(imageObj) ?? fallbackImageMediaType;
       if (isNonEmptyString(imageObj.url)) {
         imageString = imageObj.url;
       } else if (isNonEmptyString(imageObj.data)) {
@@ -1571,9 +1568,7 @@ function convertStructuredToolOutputToInputItem(
       result.image = output.image;
     } else if (isRecord(output.image)) {
       const imageObj = output.image as Record<string, any>;
-      const inlineMediaType = isNonEmptyString(imageObj.mediaType)
-        ? imageObj.mediaType
-        : undefined;
+      const inlineMediaType = getImageInlineMediaType(imageObj);
       if (isNonEmptyString(imageObj.url)) {
         result.image = imageObj.url;
       } else if (isNonEmptyString(imageObj.data)) {
@@ -1866,6 +1861,18 @@ function isNonEmptyString(value: unknown): value is string {
   return typeof value === 'string' && value.length > 0;
 }

+function getImageInlineMediaType(
+  value: Record<string, any>,
+): string | undefined {
+  if (isNonEmptyString(value.mediaType)) {
+    return value.mediaType;
+  }
+  if (isNonEmptyString((value as any).mimeType)) {
+    return (value as any).mimeType;
+  }
+  return undefined;
+}
+
 function toInlineImageString(
   data: string | Uint8Array,
   mediaType?: string,
diff --git a/packages/agents-core/test/runner/toolExecution.test.ts b/packages/agents-core/test/runner/toolExecution.test.ts
index 8180bc80f..0076d0e37 100644
--- a/packages/agents-core/test/runner/toolExecution.test.ts
+++ b/packages/agents-core/test/runner/toolExecution.test.ts
@@ -241,6 +241,22 @@ describe('getToolCallOutputItem', () => {
     ]);
   });

+  it('converts MCP image outputs with mimeType into data URLs', () => {
+    const base64 = Buffer.from('hi').toString('base64');
+    const result = getToolCallOutputItem(TEST_MODEL_FUNCTION_CALL, {
+      type: 'image',
+      data: base64,
+      mimeType: 'image/jpeg',
+    });
+
+    expect(result.output).toEqual([
+      {
+        type: 'input_image',
+        image: `data:image/jpeg;base64,${base64}`,
+      },
+    ]);
+  });
+
   it('converts file outputs with base64 data', () => {
     const result = getToolCallOutputItem(TEST_MODEL_FUNCTION_CALL, {
       type: 'file',
diff --git a/packages/agents-openai/src/openaiResponsesModel.ts b/packages/agents-openai/src/openaiResponsesModel.ts
index fd7c9613a..049b2a7bb 100644
--- a/packages/agents-openai/src/openaiResponsesModel.ts
+++ b/packages/agents-openai/src/openaiResponsesModel.ts
@@ -578,12 +578,16 @@ function convertLegacyToolOutputContent(
     const legacyImageUrl = (output as any).imageUrl;
     const legacyFileId = (output as any).fileId;
     const dataValue = (output as any).data;
+    const topLevelInlineMediaType = getImageInlineMediaType(
+      output as Record<string, any>,
+    );

     if (typeof output.image === 'string' && output.image.length > 0) {
       structured.image = output.image;
     } else if (isRecord(output.image)) {
       const imageObj = output.image as Record<string, any>;
-      const inlineMediaType = getImageInlineMediaType(imageObj);
+      const inlineMediaType =
+        getImageInlineMediaType(imageObj) ?? topLevelInlineMediaType;
       if (typeof imageObj.url === 'string' && imageObj.url.length > 0) {
         structured.image = imageObj.url;
       } else if (
@@ -624,7 +628,10 @@ function convertLegacyToolOutputContent(
       }

       if (base64Data) {
-        structured.image = base64Data;
+        structured.image = formatInlineData(
+          base64Data,
+          topLevelInlineMediaType,
+        );
       }
     }

@@ -944,6 +951,12 @@ function getImageInlineMediaType(
   if (typeof source.mediaType === 'string' && source.mediaType.length > 0) {
     return source.mediaType;
   }
+  if (
+    typeof (source as any).mimeType === 'string' &&
+    (source as any).mimeType.length > 0
+  ) {
+    return (source as any).mimeType;
+  }
   return undefined;
 }

@@ -951,6 +964,9 @@ function formatInlineData(
   data: string | Uint8Array,
   mediaType?: string,
 ): string {
+  if (typeof data === 'string' && data.startsWith('data:')) {
+    return data;
+  }
   const base64 =
     typeof data === 'string' ? data : encodeUint8ArrayToBase64(data);
   return mediaType ? `data:${mediaType};base64,${base64}` : base64;
diff --git a/packages/agents-openai/test/openaiResponsesModel.helpers.test.ts b/packages/agents-openai/test/openaiResponsesModel.helpers.test.ts
index 7f74ea6e5..687306dea 100644
--- a/packages/agents-openai/test/openaiResponsesModel.helpers.test.ts
+++ b/packages/agents-openai/test/openaiResponsesModel.helpers.test.ts
@@ -1185,6 +1185,129 @@ describe('getInputItems', () => {
     });
   });

+  it('converts ToolOutputImage mimeType aliases into data URLs', () => {
+    const base64 = Buffer.from('ai-image').toString('base64');
+    const items = getInputItems([
+      {
+        type: 'function_call_result',
+        callId: 'c6',
+        output: {
+          type: 'image',
+          image: {
+            data: base64,
+            mimeType: 'image/jpeg',
+          },
+        },
+      },
+      {
+        type: 'function_call_result',
+        callId: 'c7',
+        output: {
+          type: 'image',
+          data: base64,
+          mimeType: 'image/jpeg',
+        },
+      },
+    ] as any);
+
+    expect(items[0]).toMatchObject({
+      type: 'function_call_output',
+      call_id: 'c6',
+      output: [
+        {
+          type: 'input_image',
+          image_url: `data:image/jpeg;base64,${base64}`,
+        },
+      ],
+    });
+    expect(items[1]).toMatchObject({
+      type: 'function_call_output',
+      call_id: 'c7',
+      output: [
+        {
+          type: 'input_image',
+          image_url: `data:image/jpeg;base64,${base64}`,
+        },
+      ],
+    });
+  });
+
+  it('preserves existing data URLs when ToolOutputImage mimeType aliases are present', () => {
+    const base64 = Buffer.from('existing-data-url').toString('base64');
+    const dataUrl = `data:image/jpeg;base64,${base64}`;
+    const items = getInputItems([
+      {
+        type: 'function_call_result',
+        callId: 'c8',
+        output: {
+          type: 'image',
+          image: {
+            data: dataUrl,
+            mimeType: 'image/jpeg',
+          },
+        },
+      },
+      {
+        type: 'function_call_result',
+        callId: 'c9',
+        output: {
+          type: 'image',
+          data: dataUrl,
+          mimeType: 'image/jpeg',
+        },
+      },
+    ] as any);
+
+    expect(items[0]).toMatchObject({
+      type: 'function_call_output',
+      call_id: 'c8',
+      output: [
+        {
+          type: 'input_image',
+          image_url: dataUrl,
+        },
+      ],
+    });
+    expect(items[1]).toMatchObject({
+      type: 'function_call_output',
+      call_id: 'c9',
+      output: [
+        {
+          type: 'input_image',
+          image_url: dataUrl,
+        },
+      ],
+    });
+  });
+
+  it('falls back to top-level mimeType for nested image data', () => {
+    const base64 = Buffer.from('top-level-mimetype').toString('base64');
+    const items = getInputItems([
+      {
+        type: 'function_call_result',
+        callId: 'c10',
+        output: {
+          type: 'image',
+          image: {
+            data: base64,
+          },
+          mimeType: 'image/jpeg',
+        },
+      },
+    ] as any);
+
+    expect(items[0]).toMatchObject({
+      type: 'function_call_output',
+      call_id: 'c10',
+      output: [
+        {
+          type: 'input_image',
+          image_url: `data:image/jpeg;base64,${base64}`,
+        },
+      ],
+    });
+  });
+
   it('preserves filenames for inline input_file data', () => {
     const base64 = Buffer.from('file-payload').toString('base64');
     const items = getInputItems([
PATCH

# Rebuild after patching
echo "Rebuilding..."
cd /workspace/openai-agents-js
pnpm build 2>&1 | tail -5

# Add documentation note about the MCP image mimeType fix
cat >> AGENTS.md <<'DOCNOTE'

### MCP Image Output Convention

- When handling MCP tool outputs with image data, both `mediaType` and `mimeType` fields must be recognized for backward compatibility.
- Image data should always be converted to proper `data:<mime>;base64,...` URLs before passing to the model.
- Existing data URLs must not be double-wrapped.
DOCNOTE

echo "Patch applied and rebuilt successfully."

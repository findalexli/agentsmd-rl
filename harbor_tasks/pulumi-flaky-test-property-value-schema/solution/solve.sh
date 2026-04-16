#!/bin/bash
set -e

cd /workspace/pulumi

# Apply the gold patch for fixing flaky TestPropertyValueSchema/serialized
cat <<'PATCH' | git apply -
diff --git a/pkg/resource/stack/deployment_test.go b/pkg/resource/stack/deployment_test.go
index 849d94dd6480..66f7ada811da 100644
--- a/pkg/resource/stack/deployment_test.go
+++ b/pkg/resource/stack/deployment_test.go
@@ -910,6 +910,22 @@ func ArchiveObjectGenerator(maxDepth int) *rapid.Generator[map[string]any] {
 	return LiteralArchiveObjectGenerator(maxDepth)
 }

+// FloatObjectGenerator generates float object values representing NaN and Inf, matching the
+// wire format used by SerializePropertyValue.
+func FloatObjectGenerator() *rapid.Generator[map[string]any] {
+	return rapid.Custom(func(t *rapid.T) map[string]any {
+		hex := rapid.SampledFrom([]string{
+			"7ff8000000000001", // NaN
+			"7ff0000000000000", // +Inf
+			"fff0000000000000", // -Inf
+		}).Draw(t, "float hex")
+		return map[string]any{
+			resource.SigKey: floatSignature,
+			"value":         hex,
+		}
+	})
+}
+
 // ResourceReferenceObjectGenerator generates resource reference object values.
 func ResourceReferenceObjectGenerator() *rapid.Generator[any] {
 	return rapid.Custom(func(t *rapid.T) any {
@@ -971,6 +987,7 @@ func ObjectValueGenerator(maxDepth int) *rapid.Generator[any] {
 		NumberObjectGenerator().AsAny(),
 		StringObjectGenerator().AsAny(),
 		AssetObjectGenerator().AsAny(),
+		FloatObjectGenerator().AsAny(),
 		ResourceReferenceObjectGenerator(),
 	}
 	if maxDepth > 0 {
diff --git a/sdk/go/common/apitype/property-values.json b/sdk/go/common/apitype/property-values.json
index 17b9c0d75577..3e790f42e30b 100644
--- a/sdk/go/common/apitype/property-values.json
+++ b/sdk/go/common/apitype/property-values.json
@@ -226,6 +226,23 @@
                 }
             },
             "required": ["4dabf18193072939515e22adb298388d", "urn"]
+        },
+        {
+            "title": "Float property values",
+            "description": "Serialized representation of NaN and Inf float64 values, which cannot be represented directly in JSON.",
+            "type": "object",
+            "properties": {
+                "4dabf18193072939515e22adb298388d": {
+                    "description": "Float signature",
+                    "const": "8ad145fe-0d11-4827-bfd7-1abcbf086f5c"
+                },
+                "value": {
+                    "description": "The IEEE 754 representation of the float value, encoded as a 16-character hexadecimal string.",
+                    "type": "string",
+                    "pattern": "^[0-9a-f]{16}$"
+                }
+            },
+            "required": ["4dabf18193072939515e22adb298388d", "value"]
         }
     ]
 }
PATCH

# Verify the patch was applied by checking for distinctive content
if ! grep -q "Float property values" sdk/go/common/apitype/property-values.json; then
    echo "ERROR: Patch was not applied correctly"
    exit 1
fi

echo "Gold patch applied successfully"

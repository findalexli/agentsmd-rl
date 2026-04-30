#!/bin/bash
set -e

REPO_DIR="/workspace/selenium"
cd "$REPO_DIR"

# Idempotency check: if already applied, exit
if grep -q "ValueTextEquals" dotnet/src/webdriver/BiDi/Json/JsonExtensions.cs; then
    echo "Patch already applied, exiting."
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/dotnet/src/webdriver/BiDi/Json/JsonExtensions.cs b/dotnet/src/webdriver/BiDi/Json/JsonExtensions.cs
index 83165d26849b9..80f4cd94945fc 100644
--- a/dotnet/src/webdriver/BiDi/Json/JsonExtensions.cs
+++ b/dotnet/src/webdriver/BiDi/Json/JsonExtensions.cs
@@ -33,21 +33,20 @@ public static string GetDiscriminator(this ref Utf8JsonReader reader, string nam

         string? discriminator = null;

-        readerClone.Read();
+        readerClone.Read(); // move past StartObject to first PropertyName
         while (readerClone.TokenType == JsonTokenType.PropertyName)
         {
-            string? propertyName = readerClone.GetString();
-            readerClone.Read();
-
-            if (propertyName == name)
+            if (readerClone.ValueTextEquals(name))
             {
+                readerClone.Read(); // move to the property value
                 discriminator = readerClone.GetString();

                 break;
             }

-            readerClone.Skip();
-            readerClone.Read();
+            readerClone.Read(); // move to the property value
+            readerClone.Skip(); // skip the value (including nested objects/arrays)
+            readerClone.Read(); // move to the next PropertyName or EndObject
         }

         return discriminator ?? throw new JsonException($"Couldn't determine '{name}' discriminator.");
PATCH

echo "Patch applied successfully."

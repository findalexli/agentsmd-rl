#!/usr/bin/env bash
set -euo pipefail

cd /testbed

# Idempotency check: skip if already patched
if grep -q "Failed to load image" vllm/multimodal/media/image.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/vllm/multimodal/media/image.py b/vllm/multimodal/media/image.py
index ea4bf7b01527..ea816b760fea 100644
--- a/vllm/multimodal/media/image.py
+++ b/vllm/multimodal/media/image.py
@@ -68,17 +68,19 @@ def _convert_image_mode(
             return convert_image_mode(image, self.image_mode)

     def load_bytes(self, data: bytes) -> MediaWithBytes[Image.Image]:
-        image = Image.open(BytesIO(data))
-        return MediaWithBytes(self._convert_image_mode(image), data)
+        try:
+            image = Image.open(BytesIO(data))
+            image.load()
+            image = self._convert_image_mode(image)
+        except (OSError, Image.UnidentifiedImageError) as e:
+            raise ValueError(f"Failed to load image: {e}") from e
+        return MediaWithBytes(image, data)

     def load_base64(self, media_type: str, data: str) -> MediaWithBytes[Image.Image]:
         return self.load_bytes(pybase64.b64decode(data, validate=True))

     def load_file(self, filepath: Path) -> MediaWithBytes[Image.Image]:
-        with open(filepath, "rb") as f:
-            data = f.read()
-        image = Image.open(BytesIO(data))
-        return MediaWithBytes(self._convert_image_mode(image), data)
+        return self.load_bytes(filepath.read_bytes())

     def encode_base64(
         self,

PATCH

echo "Patch applied successfully."

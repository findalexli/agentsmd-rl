#!/usr/bin/env bash
set -euo pipefail
cd /workspace/AReaL

FILE="areal/infra/rpc/serialization.py"

# Idempotent: skip if already applied
grep -q 'SerializedPILImage' "$FILE" && exit 0

git apply - <<'PATCH'
diff --git a/areal/infra/rpc/serialization.py b/areal/infra/rpc/serialization.py
index a20053062..67cdc4823 100644
--- a/areal/infra/rpc/serialization.py
+++ b/areal/infra/rpc/serialization.py
@@ -26,11 +26,19 @@
 import torch
 from pydantic import BaseModel, Field

+try:
+    from PIL import Image
+    from PIL.Image import Image as ImageObject
+except ImportError:  # pragma: no cover - optional dependency for non-VLM setups
+    Image = None
+    ImageObject = None
+
 from areal.utils import logging

 TOKENIZER_ARCHIVE_INLINE_THRESHOLD = 512 * 1024
 TOKENIZER_ZSTD_THRESHOLD = 20 * 1024 * 1024
 TokenizerCompression = Literal["zip", "zstd"]
+ProcessorCompression = Literal["zip", "zstd"]

 logger = logging.getLogger("RPCSerialization")

@@ -207,6 +215,37 @@ def to_array(self) -> np.ndarray:
         return array.reshape(self.shape)


+class SerializedPILImage(BaseModel):
+    """Pydantic model for serialized PIL images."""
+
+    type: Literal["pil_image"] = Field(default="pil_image")
+    data: str
+    mode: str | None = None
+
+    @classmethod
+    def from_image(cls, image: "ImageObject") -> "SerializedPILImage":
+        with io.BytesIO() as buffer:
+            # Always use PNG to avoid format-specific save issues
+            image.save(buffer, format="PNG")
+            data_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
+        return cls(data=data_b64, mode=image.mode)
+
+    def to_image(self) -> "ImageObject":
+        if Image is None:  # pragma: no cover - depends on optional pillow dependency
+            raise RuntimeError(
+                "Pillow is required to deserialize PIL images but is not installed"
+            )
+
+        with io.BytesIO(base64.b64decode(self.data.encode("utf-8"))) as buffer:
+            image = Image.open(buffer)
+            image.load()
+
+        if self.mode is not None and image.mode != self.mode:
+            image = image.convert(self.mode)
+
+        return image
+
+
 class SerializedDataclass(BaseModel):
     """Pydantic model for serialized dataclass with metadata.

@@ -380,6 +419,115 @@ def _maybe_decompress(self, blob: bytes) -> bytes:
         raise ValueError(msg)


+class SerializedProcessor(BaseModel):
+    """Pydantic model for serialized Hugging Face processors.
+
+    Attributes
+    ----------
+    type : str
+        Type marker, always "processor"
+    name_or_path : str
+        Original ``name_or_path`` attribute captured from the processor
+    data : str
+        Base64-encoded ZIP (optionally Zstandard-compressed) archive of the processor files
+    compression : {"zip", "zstd"}
+        Compression algorithm applied to the archive payload
+    """
+
+    type: Literal["processor"] = Field(default="processor")
+    name_or_path: str
+    data: str
+    compression: ProcessorCompression = Field(default="zip")
+
+    @classmethod
+    def from_processor(cls, processor: Any) -> "SerializedProcessor":
+        """Create a serialized representation from a Hugging Face processor."""
+        name_or_path = getattr(processor, "name_or_path", None)
+        if name_or_path is None:
+            # Some processors store name_or_path on their inner tokenizer
+            tokenizer = getattr(processor, "tokenizer", None)
+            name_or_path = getattr(
+                tokenizer, "name_or_path", processor.__class__.__name__
+            )
+        blob = cls._archive_processor(processor)
+        blob, compression = cls._maybe_compress(blob)
+        data_b64 = base64.b64encode(blob).decode("utf-8")
+        return cls(name_or_path=name_or_path, data=data_b64, compression=compression)
+
+    def to_processor(self) -> Any:
+        """Reconstruct a Hugging Face processor from serialized data."""
+        blob = base64.b64decode(self.data.encode("utf-8"))
+        blob = self._maybe_decompress(blob)
+        from transformers import AutoProcessor
+
+        zip_buffer = io.BytesIO(blob)
+        with tempfile.TemporaryDirectory() as tmpdir:
+            with zipfile.ZipFile(zip_buffer) as zf:
+                zf.extractall(tmpdir)
+            processor = AutoProcessor.from_pretrained(tmpdir)
+
+        if hasattr(processor, "name_or_path"):
+            processor.name_or_path = self.name_or_path
+        return processor
+
+    @staticmethod
+    def _is_processor(obj: Any) -> bool:
+        try:
+            from transformers import ProcessorMixin
+        except ImportError:  # pragma: no cover - optional dependency
+            return False
+        return isinstance(obj, ProcessorMixin)
+
+    @staticmethod
+    def _archive_processor(processor: Any) -> bytes:
+        zip_buffer = io.BytesIO()
+        with tempfile.TemporaryDirectory() as tmpdir:
+            processor.save_pretrained(tmpdir)
+            total_size = sum(
+                os.path.getsize(os.path.join(root, file))
+                for root, _, files in os.walk(tmpdir)
+                for file in files
+            )
+            compression = (
+                zipfile.ZIP_STORED
+                if total_size < TOKENIZER_ARCHIVE_INLINE_THRESHOLD
+                else zipfile.ZIP_DEFLATED
+            )
+            compress_kwargs = (
+                {"compresslevel": 6} if compression == zipfile.ZIP_DEFLATED else {}
+            )
+            with zipfile.ZipFile(
+                zip_buffer, "w", compression=compression, **compress_kwargs
+            ) as zf:
+                for root, _, files in os.walk(tmpdir):
+                    for file in files:
+                        full_path = os.path.join(root, file)
+                        arcname = os.path.relpath(full_path, tmpdir)
+                        zf.write(full_path, arcname=arcname)
+        return zip_buffer.getvalue()
+
+    @staticmethod
+    def _maybe_compress(blob: bytes) -> tuple[bytes, ProcessorCompression]:
+        if (
+            len(blob) > TOKENIZER_ZSTD_THRESHOLD
+            and importlib.util.find_spec("zstandard") is not None
+        ):
+            import zstandard as zstd
+
+            return zstd.ZstdCompressor(level=3).compress(blob), "zstd"
+        return blob, "zip"
+
+    def _maybe_decompress(self, blob: bytes) -> bytes:
+        if self.compression == "zip":
+            return blob
+        if self.compression == "zstd":
+            import zstandard as zstd
+
+            return zstd.ZstdDecompressor().decompress(blob)
+        msg = f"Unsupported processor compression: {self.compression}"
+        raise ValueError(msg)
+
+
 def serialize_value(value: Any) -> Any:
     """Recursively serialize a value, converting tensors and dataclasses to serialized dicts.

@@ -388,6 +536,7 @@ def serialize_value(value: Any) -> Any:
     - numpy.ndarray -> SerializedNDArray dict
     - dataclass instances -> SerializedDataclass dict (preserves type information)
     - Hugging Face tokenizers -> SerializedTokenizer dict
+    - Hugging Face processors -> SerializedProcessor dict
     - dict -> recursively serialize values
     - list/tuple -> recursively serialize elements
     - primitives (int, float, str, bool, None) -> unchanged
@@ -414,6 +563,10 @@ def serialize_value(value: Any) -> Any:
     if isinstance(value, np.ndarray):
         return SerializedNDArray.from_array(value).model_dump()

+    # Handle PIL image payloads for VLM tasks
+    if ImageObject is not None and isinstance(value, ImageObject):
+        return SerializedPILImage.from_image(value).model_dump()
+
     # Handle dataclass instances (check before dict, as dataclasses can be dict-like)
     # Note: is_dataclass returns True for both classes and instances, so check it's not a type
     if is_dataclass(value) and not isinstance(value, type):
@@ -432,6 +585,11 @@ def serialize_value(value: Any) -> Any:
         tokenizer_payload = SerializedTokenizer.from_tokenizer(value)
         return tokenizer_payload.model_dump()

+    # Handle Hugging Face processors (e.g. Qwen2_5_VLProcessor)
+    if SerializedProcessor._is_processor(value):
+        processor_payload = SerializedProcessor.from_processor(value)
+        return processor_payload.model_dump()
+
     # Handle dict - recursively serialize values
     if isinstance(value, dict):
         return {key: serialize_value(val) for key, val in value.items()}
@@ -460,6 +618,7 @@ def deserialize_value(value: Any) -> Any:
     - SerializedNDArray dict -> numpy.ndarray
     - SerializedDataclass dict -> dataclass instance (reconstructed with original type)
     - SerializedTokenizer dict -> Hugging Face tokenizer
+    - SerializedProcessor dict -> Hugging Face processor
     - dict -> recursively deserialize values
     - list -> recursively deserialize elements
     - primitives -> unchanged
@@ -507,6 +666,16 @@ def deserialize_value(value: Any) -> Any:
                     f"Failed to deserialize tokenizer, treating as regular dict: {e}"
                 )

+        # Check for SerializedProcessor marker
+        if value.get("type") == "processor":
+            try:
+                serialized_processor = SerializedProcessor.model_validate(value)
+                return serialized_processor.to_processor()
+            except Exception as e:
+                logger.warning(
+                    f"Failed to deserialize processor, treating as regular dict: {e}"
+                )
+
         # Check for SerializedNDArray marker
         if value.get("type") == "ndarray":
             try:
@@ -517,6 +686,16 @@ def deserialize_value(value: Any) -> Any:
                     f"Failed to deserialize ndarray, treating as regular dict: {e}"
                 )

+        # Check for SerializedPILImage marker
+        if value.get("type") == "pil_image":
+            try:
+                serialized_image = SerializedPILImage.model_validate(value)
+                return serialized_image.to_image()
+            except Exception as e:
+                logger.warning(
+                    f"Failed to deserialize PIL image, treating as regular dict: {e}"
+                )
+
         # Check for SerializedTensor marker
         if value.get("type") == "tensor":
             try:
PATCH

#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if fix is already applied
if grep -q 'if is_vision_available' src/transformers/video_processing_utils.py; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/video_processing_utils.py b/src/transformers/video_processing_utils.py
index fc0cca89c0bb..2ce39d6c1cf3 100644
--- a/src/transformers/video_processing_utils.py
+++ b/src/transformers/video_processing_utils.py
@@ -28,8 +28,8 @@
 from .image_processing_utils import BatchFeature
 from .image_utils import (
     ChannelDimension,
-    PILImageResampling,
     SizeDict,
+    is_vision_available,
     validate_kwargs,
 )
 from .processing_utils import Unpack, VideosKwargs
@@ -67,6 +67,9 @@
 if is_torchvision_v2_available():
     import torchvision.transforms.v2.functional as tvF

+if is_vision_available():
+    from .image_utils import PILImageResampling
+

 logger = logging.get_logger(__name__)

PATCH

echo "Patch applied successfully."

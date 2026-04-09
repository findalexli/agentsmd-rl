#!/bin/bash
set -e

cd /workspace/hugo

# Apply the fix for getImageOps error message
cat <<'PATCH' | git apply -
diff --git a/resources/transform.go b/resources/transform.go
index bcacf5471e3..169c50895e9 100644
--- a/resources/transform.go
+++ b/resources/transform.go
@@ -395,12 +395,20 @@ func (r resourceAdapter) WithResourceMeta(mp resource.ResourceMetaProvider) reso
 func (r *resourceAdapter) getImageOps() images.ImageResourceOps {
 	img, ok := r.target.(images.ImageResourceOps)
 	if !ok {
-		if r.MediaType().SubType == "svg" {
-			panic("this method is only available for raster images. To determine if an image is SVG, you can do {{ if eq .MediaType.SubType \"svg\" }}{{ end }}")
-		}
-		panic("this method is only available for image resources")
+		instructions := "use reflect.IsImageResource, " +
+			"reflect.IsImageResourceProcessable, or " +
+			"reflect.IsImageResourceWithMeta to check if the resource " +
+			"supports this method before calling it"
+		msg := fmt.Sprintf(
+			"resource %q of media type %q does not support this method: %s",
+			r.Name(),
+			r.MediaType(),
+			instructions,
+		)
+		panic(msg)
 	}
 	r.init(false, false)
+
 	return img
 }
 PATCH

echo "Fix applied successfully"

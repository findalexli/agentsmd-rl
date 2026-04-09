#!/bin/bash
set -e

cd /workspace/hugo

# Apply the fix for taxonomy entries with empty keys or values
cat <<'PATCH' | git apply -
diff --git a/config/allconfig/alldecoders.go b/config/allconfig/alldecoders.go
index b7c55258dda..2fb0276d2f9 100644
--- a/config/allconfig/alldecoders.go
+++ b/config/allconfig/alldecoders.go
@@ -335,7 +335,14 @@ var allDecoderSetups = map[string]decodeWeight{
 		key: "taxonomies",
 		decode: func(d decodeWeight, p decodeConfig) error {
 			if p.p.IsSet(d.key) {
-				p.c.Taxonomies = hmaps.CleanConfigStringMapString(p.p.GetStringMapString(d.key))
+				m := hmaps.CleanConfigStringMapString(p.p.GetStringMapString(d.key))
+				// Remove invalid entries (e.g. non-taxonomy keys placed inside [taxonomies] in TOML).
+				for k, v := range m {
+					if k == "" || v == "" {
+						delete(m, k)
+					}
+				}
+				p.c.Taxonomies = m
 			}
 			return nil
 		},
PATCH

echo "Fix applied successfully"

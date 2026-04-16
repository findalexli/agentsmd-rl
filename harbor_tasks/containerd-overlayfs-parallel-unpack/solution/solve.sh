#!/bin/bash
set -e

cd /workspace/containerd

# Apply the fix for parallel unpack with overlayfs
cat <<'PATCH' | git apply -
diff --git a/core/unpack/unpacker.go b/core/unpack/unpacker.go
index f396903ac8d07..67f2dcb7c4587 100644
--- a/core/unpack/unpacker.go
+++ b/core/unpack/unpacker.go
@@ -530,6 +530,15 @@ func (u *Unpacker) unpack(
 			case <-fetchC[i-fetchOffset]:
 			}

+			// In case of parallel unpack, the parent snapshot isn't provided to the snapshotter.
+			// The overlayfs will return bind mounts for all layers, we need to convert them
+			// to overlay mounts for the applier to perform whiteout conversion correctly.
+			// TODO: this is a temporary workaround until #13053 lands.
+			// See: https://github.com/containerd/containerd/issues/13030
+			if i > 0 && parallel && unpack.SnapshotterKey == "overlayfs" {
+				mounts = bindToOverlay(mounts)
+			}
+
 			diff, err := a.Apply(ctx, desc, mounts, unpack.ApplyOpts...)
 			if err != nil {
 				cleanup.Do(ctx, abort)
@@ -753,3 +762,23 @@ func uniquePart() string {
 	rand.Read(b[:])
 	return fmt.Sprintf("%d-%s", t.Nanosecond(), base64.URLEncoding.EncodeToString(b[:]))
 }
+
+// TODO: this is a temporary workaround until #13053 lands.
+func bindToOverlay(mounts []mount.Mount) []mount.Mount {
+	if len(mounts) != 1 || mounts[0].Type != "bind" {
+		return mounts
+	}
+
+	m := mount.Mount{
+		Type:   "overlay",
+		Source: "overlay",
+	}
+	for _, o := range mounts[0].Options {
+		if o != "rbind" {
+			m.Options = append(m.Options, o)
+		}
+	}
+	m.Options = append(m.Options, "upperdir="+mounts[0].Source)
+
+	return []mount.Mount{m}
+}
diff --git a/core/unpack/unpacker_test.go b/core/unpack/unpacker_test.go
index 66da7b585c8c1..bdd08348f56f7 100644
--- a/core/unpack/unpacker_test.go
+++ b/core/unpack/unpacker_test.go
@@ -19,8 +19,10 @@ package unpack
 import (
 	"crypto/rand"
 	"fmt"
+	"reflect"
 	"testing"

+	"github.com/containerd/containerd/v2/core/mount"
 	"github.com/opencontainers/go-digest"
 	"github.com/opencontainers/image-spec/identity"
 )
@@ -91,3 +93,87 @@ func BenchmarkUnpackWithChainIDs(b *testing.B) {
 		})
 	}
 }
+
+func TestBindToOverlay(t *testing.T) {
+	testCases := []struct {
+		name   string
+		mounts []mount.Mount
+		expect []mount.Mount
+	}{
+		{
+			name: "single bind mount",
+			mounts: []mount.Mount{
+				{
+					Type:    "bind",
+					Source:  "/path/to/source",
+					Options: []string{"ro", "rbind"},
+				},
+			},
+			expect: []mount.Mount{
+				{
+					Type:   "overlay",
+					Source: "overlay",
+					Options: []string{
+						"ro",
+						"upperdir=/path/to/source",
+					},
+				},
+			},
+		},
+		{
+			name: "overlay mount",
+			mounts: []mount.Mount{
+				{
+					Type:   "overlay",
+					Source: "overlay",
+					Options: []string{
+						"lowerdir=/path/to/lower",
+						"upperdir=/path/to/upper",
+					},
+				},
+			},
+			expect: []mount.Mount{
+				{
+					Type:   "overlay",
+					Source: "overlay",
+					Options: []string{
+						"lowerdir=/path/to/lower",
+						"upperdir=/path/to/upper",
+					},
+				},
+			},
+		},
+		{
+			name: "multiple mounts",
+			mounts: []mount.Mount{
+				{
+					Type:   "bind",
+					Source: "/path/to/source1",
+				},
+				{
+					Type:   "bind",
+					Source: "/path/to/source2",
+				},
+			},
+			expect: []mount.Mount{
+				{
+					Type:   "bind",
+					Source: "/path/to/source1",
+				},
+				{
+					Type:   "bind",
+					Source: "/path/to/source2",
+				},
+			},
+		},
+	}
+
+	for _, tc := range testCases {
+		t.Run(tc.name, func(t *testing.T) {
+			result := bindToOverlay(tc.mounts)
+			if !reflect.DeepEqual(result, tc.expect) {
+				t.Errorf("unexpected result: got %v, want %v", result, tc.expect)
+			}
+		})
+	}
+}
PATCH

# Verify the patch was applied
grep -q "bindToOverlay" core/unpack/unpacker.go
echo "Fix applied successfully"

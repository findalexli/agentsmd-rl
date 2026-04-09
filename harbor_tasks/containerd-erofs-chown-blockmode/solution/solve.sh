#!/bin/bash
set -euxo pipefail

cd /workspace/containerd

# Idempotency check: skip if already patched
if grep -q "In block mode, host permissions are not relevant" plugins/snapshots/erofs/erofs.go; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/plugins/snapshots/erofs/erofs.go b/plugins/snapshots/erofs/erofs.go
index dfc32a8b1f317..ef9a2f87c209a 100644
--- a/plugins/snapshots/erofs/erofs.go
+++ b/plugins/snapshots/erofs/erofs.go
@@ -447,48 +447,53 @@ func (s *snapshotter) createSnapshot(ctx context.Context, kind snapshots.Kind, k
 			return fmt.Errorf("failed to get snapshot info: %w", err)
 		}

-		var (
-			mappedUID, mappedGID     = -1, -1
-			uidmapLabel, gidmapLabel string
-			needsRemap               = false
-		)
-		if v, ok := info.Labels[snapshots.LabelSnapshotUIDMapping]; ok {
-			uidmapLabel = v
-			needsRemap = true
-		}
-		if v, ok := info.Labels[snapshots.LabelSnapshotGIDMapping]; ok {
-			gidmapLabel = v
-			needsRemap = true
-		}
-
-		if needsRemap {
-			var idMap userns.IDMap
-			if err = idMap.Unmarshal(uidmapLabel, gidmapLabel); err != nil {
-				return fmt.Errorf("failed to unmarshal snapshot ID mapped labels: %w", err)
+		// In non-block mode, set the ownership of the upperdir so that
+		// user-namespace-remapped containers can write to it.
+		// In block mode the upperdir lives inside the block image,
+		// so host ownership is irrelevant.
+		if !s.blockMode {
+			var (
+				mappedUID, mappedGID     = -1, -1
+				uidmapLabel, gidmapLabel string
+				needsRemap               = false
+			)
+			if v, ok := info.Labels[snapshots.LabelSnapshotUIDMapping]; ok {
+				uidmapLabel = v
+				needsRemap = true
 			}
-			root, err := idMap.RootPair()
-			if err != nil {
-				return fmt.Errorf("failed to find root pair: %w", err)
+			if v, ok := info.Labels[snapshots.LabelSnapshotGIDMapping]; ok {
+				gidmapLabel = v
+				needsRemap = true
 			}
-			mappedUID, mappedGID = int(root.Uid), int(root.Gid)
-		}

-		// Fall back to copying ownership from parent if no ID mapping labels
-		if mappedUID == -1 || mappedGID == -1 {
-			if len(snap.ParentIDs) > 0 {
-				uid, gid, err := getParentOwnership(s.upperPath(snap.ParentIDs[0]))
+			if needsRemap {
+				var idMap userns.IDMap
+				if err = idMap.Unmarshal(uidmapLabel, gidmapLabel); err != nil {
+					return fmt.Errorf("failed to unmarshal snapshot ID mapped labels: %w", err)
+				}
+				root, err := idMap.RootPair()
 				if err != nil {
-					return fmt.Errorf("failed to get parent ownership: %w", err)
+					return fmt.Errorf("failed to find root pair: %w", err)
 				}
-				mappedUID = uid
-				mappedGID = gid
+				mappedUID, mappedGID = int(root.Uid), int(root.Gid)
 			}
-		}

-		// Apply the ownership if we have valid UID/GID
-		if mappedUID != -1 && mappedGID != -1 {
-			if err := os.Lchown(filepath.Join(td, "fs"), mappedUID, mappedGID); err != nil {
-				return fmt.Errorf("failed to chown: %w", err)
+			// Fall back to copying ownership from parent if no ID mapping labels
+			if mappedUID == -1 || mappedGID == -1 {
+				if len(snap.ParentIDs) > 0 {
+					uid, gid, err := getParentOwnership(s.upperPath(snap.ParentIDs[0]))
+					if err != nil {
+						return fmt.Errorf("failed to get parent ownership: %w", err)
+					}
+					mappedUID = uid
+					mappedGID = gid
+				}
+			}
+
+			if mappedUID != -1 && mappedGID != -1 {
+				if err := os.Lchown(filepath.Join(td, "fs"), mappedUID, mappedGID); err != nil {
+					return fmt.Errorf("failed to chown: %w", err)
+				}
 			}
 		}
 PATCH

echo "Patch applied successfully"

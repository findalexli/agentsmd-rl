#!/bin/bash
set -e

cd /workspace/pulumi

# Apply the fix: move lock acquisition after PreviewOnly check in Refresh function
patch -p1 << 'PATCH'
diff --git a/pkg/backend/diy/backend.go b/pkg/backend/diy/backend.go
index aedfc63a9a06..78fb46d90335 100644
--- a/pkg/backend/diy/backend.go
+++ b/pkg/backend/diy/backend.go
@@ -1119,12 +1119,6 @@ func (b *diyBackend) Import(ctx context.Context, stack backend.Stack,
 func (b *diyBackend) Refresh(ctx context.Context, stack backend.Stack,
 	op backend.UpdateOperation,
 ) (sdkDisplay.ResourceChanges, error) {
-	err := b.Lock(ctx, stack.Ref())
-	if err != nil {
-		return nil, err
-	}
-	defer b.Unlock(ctx, stack.Ref())
-
 	if op.Opts.PreviewOnly {
 		// We can skip PreviewThenPromptThenExecute, and just go straight to Execute.
 		opts := backend.ApplierOptions{
@@ -1138,6 +1132,12 @@ func (b *diyBackend) Refresh(ctx context.Context, stack backend.Stack,
 		return changes, err
 	}

+	err := b.Lock(ctx, stack.Ref())
+	if err != nil {
+		return nil, err
+	}
+	defer b.Unlock(ctx, stack.Ref())
+
 	return backend.PreviewThenPromptThenExecute(ctx, apitype.RefreshUpdate, stack, op, b.apply, nil, nil)
 }
PATCH

# Verify the patch was applied by checking for the distinctive line
grep -q "opts := backend.ApplierOptions{" pkg/backend/diy/backend.go && echo "Patch applied successfully"

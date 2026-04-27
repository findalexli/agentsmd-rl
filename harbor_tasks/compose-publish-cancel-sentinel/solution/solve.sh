#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compose

# Idempotency: skip if already fixed.
if grep -q "return api.ErrCanceled" pkg/compose/publish.go; then
    echo "Patch already applied; nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/pkg/compose/publish.go b/pkg/compose/publish.go
index e15eaec89d..30b6a6a49b 100644
--- a/pkg/compose/publish.go
+++ b/pkg/compose/publish.go
@@ -59,7 +59,7 @@ func (s *composeService) publish(ctx context.Context, project *types.Project, re
 		return err
 	}
 	if !accept {
-		return nil
+		return api.ErrCanceled
 	}
 	err = s.Push(ctx, project, api.PushOptions{IgnoreFailures: true, ImageMandatory: true})
 	if err != nil {
PATCH

echo "Patch applied successfully."

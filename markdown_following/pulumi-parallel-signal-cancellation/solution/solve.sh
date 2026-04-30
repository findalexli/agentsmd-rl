#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pulumi

if grep -q 'cancelCtx, cancelCancel := context.WithTimeout' \
    sdk/go/common/resource/plugin/host.go 2>/dev/null; then
    echo "patch already applied, nothing to do"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/changelog/pending/20260401--engine--parallelize-plugin-cancellation-in-signalcancellation.yaml b/changelog/pending/20260401--engine--parallelize-plugin-cancellation-in-signalcancellation.yaml
new file mode 100644
index 000000000000..5b5ebd371061
--- /dev/null
+++ b/changelog/pending/20260401--engine--parallelize-plugin-cancellation-in-signalcancellation.yaml
@@ -0,0 +1,4 @@
+changes:
+- type: fix
+  scope: engine
+  description: Parallelize plugin cancellation in SignalCancellation
diff --git a/sdk/go/common/resource/plugin/host.go b/sdk/go/common/resource/plugin/host.go
index 0bb2fba594b0..b537ea75c4fd 100644
--- a/sdk/go/common/resource/plugin/host.go
+++ b/sdk/go/common/resource/plugin/host.go
@@ -23,6 +23,7 @@ import (
 	"path/filepath"
 	"strings"
 	"sync"
+	"time"

 	"github.com/blang/semver"
 	"github.com/hashicorp/go-multierror"
@@ -665,28 +666,53 @@ func (host *defaultHost) GetProjectPlugins() []workspace.ProjectPlugin {
 func (host *defaultHost) SignalCancellation() error {
 	// NOTE: we're abusing loadPlugin in order to ensure proper synchronization.
 	_, err := host.loadPlugin(host.loadRequests, func() (any, error) {
-		var result error
+		cancelCtx, cancelCancel := context.WithTimeout(context.Background(), 30*time.Second)
+		defer cancelCancel()
+
+		// Cancel in two phases: first resource providers and analyzers, then language hosts. RunPlugin-based providers
+		// run inside a language host, so we cancel non-language host plugins first to give them a chance to shut down
+		// cleanly before cancelling the language host that spawned them.
+		var (
+			mu   sync.Mutex
+			errs []error
+		)
+
+		var wg sync.WaitGroup
 		for _, plug := range host.resourcePlugins {
-			if err := plug.Plugin.SignalCancellation(host.ctx.Request()); err != nil {
-				result = multierror.Append(result, fmt.Errorf(
-					"Error signaling cancellation to resource provider '%s': %w", plug.Name, err))
-			}
+			wg.Go(func() {
+				if err := plug.Plugin.SignalCancellation(cancelCtx); err != nil {
+					mu.Lock()
+					errs = append(errs, fmt.Errorf(
+						"error signaling cancellation to resource provider '%s': %w", plug.Name, err))
+					mu.Unlock()
+				}
+			})
 		}
-
 		for _, plug := range host.analyzerPlugins {
-			if err := plug.Plugin.Cancel(host.ctx.Request()); err != nil {
-				result = multierror.Append(result, fmt.Errorf(
-					"Error signaling cancellation to analyzer '%s': %w", plug.Name, err))
-			}
+			wg.Go(func() {
+				if err := plug.Plugin.Cancel(cancelCtx); err != nil {
+					mu.Lock()
+					errs = append(errs, fmt.Errorf(
+						"error signaling cancellation to analyzer '%s': %w", plug.Name, err))
+					mu.Unlock()
+				}
+			})
 		}
+		wg.Wait()

 		for _, plug := range host.languagePlugins {
-			if err := plug.Plugin.Cancel(); err != nil {
-				result = multierror.Append(result, fmt.Errorf(
-					"Error signaling cancellation to language runtime '%s': %w", plug.Name, err))
-			}
+			wg.Go(func() {
+				if err := plug.Plugin.Cancel(); err != nil {
+					mu.Lock()
+					errs = append(errs, fmt.Errorf(
+						"error signaling cancellation to language runtime '%s': %w", plug.Name, err))
+					mu.Unlock()
+				}
+			})
 		}
-		return nil, result
+		wg.Wait()
+
+		return nil, errors.Join(errs...)
 	})
 	return err
 }
PATCH

echo "gold patch applied"

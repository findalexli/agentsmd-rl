#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compose

# Idempotent: skip if already applied
if grep -q 'golangci-lint v2' CLAUDE.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
new file mode 100644
index 00000000000..613a13c011f
--- /dev/null
+++ b/CLAUDE.md
@@ -0,0 +1,27 @@
+# Project: Docker Compose
+
+## Build & Test
+
+- Build: `make build`
+- Test all: `make test`
+- Test unit: `go test ./pkg/...`
+- Test single: `go test ./pkg/compose/ -run TestFunctionName`
+- E2E tests: `go test -tags e2e ./pkg/e2e/ -run TestName`
+
+## Lint
+
+- Linter: golangci-lint v2 (config in `.golangci.yml`)
+- Run: `golangci-lint run --build-tags "e2e" ./...`
+- **After modifying any Go code, ALWAYS run the linter and fix all reported issues before considering the task complete.**
+- Lint is also run via Docker: `docker buildx bake lint` (uses version pinned in `Dockerfile`)
+
+## Code Style
+
+- Formatting is enforced by golangci-lint (gofumpt + gci)
+- Import order: stdlib, third-party, local module (enforced by gci)
+- Max line length: 200 chars
+- Max cyclomatic complexity: 16
+- No `io/ioutil`, `github.com/pkg/errors`, `gopkg.in/yaml.v2`, `golang.org/x/exp/maps`, `golang.org/x/exp/slices`
+- Use `github.com/containerd/errdefs` instead of `github.com/docker/docker/errdefs`
+- In tests: use `t.Context()` instead of `context.Background()` or `context.TODO()`
+- Prefer `fmt.Fprintf` over `WriteString(fmt.Sprintf(...))`

diff --git a/Dockerfile b/Dockerfile
index bb8001e9464..0e004e4bf9b 100644
--- a/Dockerfile
+++ b/Dockerfile
@@ -17,7 +17,7 @@

 ARG GO_VERSION=1.25.8
 ARG XX_VERSION=1.9.0
-ARG GOLANGCI_LINT_VERSION=v2.8.0
+ARG GOLANGCI_LINT_VERSION=v2.11.3
 ARG ADDLICENSE_VERSION=v1.0.0

 ARG BUILD_TAGS="e2e"

diff --git a/pkg/compose/publish.go b/pkg/compose/publish.go
index fb466607559..2aec424db93 100644
--- a/pkg/compose/publish.go
+++ b/pkg/compose/publish.go
@@ -332,7 +332,7 @@ func (s *composeService) preChecks(project *types.Project, options api.PublishOp
 		for _, val := range detectedSecrets {
 			b.WriteString(val.Type)
 			b.WriteRune('\n')
-			b.WriteString(fmt.Sprintf("%q: %s\n", val.Key, val.Value))
+			fmt.Fprintf(&b, "%q: %s\n", val.Key, val.Value)
 		}
 		b.WriteString("Are you ok to publish these sensitive data?")
 		confirm, err := s.prompt(b.String(), false)
@@ -362,7 +362,7 @@ func (s *composeService) checkEnvironmentVariables(project *types.Project, optio
 		var errorMsg strings.Builder
 		for _, errors := range errorList {
 			for _, err := range errors {
-				errorMsg.WriteString(fmt.Sprintf("%s\n", err))
+				fmt.Fprintf(&errorMsg, "%s\n", err)
 			}
 		}
 		return fmt.Errorf("%s%s", errorMsg.String(), errorMsgSuffix)
@@ -396,7 +396,7 @@ func (s *composeService) checkOnlyBuildSection(project *types.Project) (bool, er
 		var errMsg strings.Builder
 		errMsg.WriteString("your Compose stack cannot be published as it only contains a build section for service(s):\n")
 		for _, serviceInError := range errorList {
-			errMsg.WriteString(fmt.Sprintf("- %q\n", serviceInError))
+			fmt.Fprintf(&errMsg, "- %q\n", serviceInError)
 		}
 		return false, errors.New(errMsg.String())
 	}

diff --git a/pkg/e2e/compose_run_build_once_test.go b/pkg/e2e/compose_run_build_once_test.go
index f9726bb3b31..24fead8c04e 100644
--- a/pkg/e2e/compose_run_build_once_test.go
+++ b/pkg/e2e/compose_run_build_once_test.go
@@ -95,6 +95,6 @@ func countServiceBuilds(output, projectName, serviceName string) int {
 // Format: prefix-<8 random hex chars> (e.g., "build-once-3f4a9b2c")
 func randomProjectName(prefix string) string {
 	b := make([]byte, 4) // 4 bytes = 8 hex chars
-	rand.Read(b)         //nolint:errcheck
+	rand.Read(b)
 	return fmt.Sprintf("%s-%s", prefix, hex.EncodeToString(b))
 }

PATCH

echo "Patch applied successfully."

#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compose

# Idempotency: if the gold patch is already applied, do nothing.
if grep -qE 'func \(s \*composeService\) RuntimeAPIVersion\(' pkg/compose/compose.go; then
    echo "Gold patch already applied; nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/pkg/compose/build_bake.go b/pkg/compose/build_bake.go
index 8e7151830e..dc691cca9f 100644
--- a/pkg/compose/build_bake.go
+++ b/pkg/compose/build_bake.go
@@ -568,7 +568,7 @@ func dockerFilePath(ctxName string, dockerfile string) string {
 	return dockerfile
 }
 
-func (s composeService) dryRunBake(cfg bakeConfig) map[string]string {
+func (s *composeService) dryRunBake(cfg bakeConfig) map[string]string {
 	bakeResponse := map[string]string{}
 	for name, target := range cfg.Targets {
 		dryRunUUID := fmt.Sprintf("dryRun-%x", sha1.Sum([]byte(name)))
@@ -581,7 +581,7 @@ func (s composeService) dryRunBake(cfg bakeConfig) map[string]string {
 	return bakeResponse
 }
 
-func (s composeService) displayDryRunBuildEvent(name, dryRunUUID, tag string) {
+func (s *composeService) displayDryRunBuildEvent(name, dryRunUUID, tag string) {
 	s.events.On(api.Resource{
 		ID:     name + " ==>",
 		Status: api.Done,
diff --git a/pkg/compose/compose.go b/pkg/compose/compose.go
index 4eddfe4677..33ed81af9b 100644
--- a/pkg/compose/compose.go
+++ b/pkg/compose/compose.go
@@ -215,6 +215,8 @@ type composeService struct {
 	clock          clockwork.Clock
 	maxConcurrency int
 	dryRun         bool
+
+	runtimeAPIVersion runtimeVersionCache
 }
 
 // Close releases any connections/resources held by the underlying clients.
@@ -491,22 +493,39 @@ func (s *composeService) isSwarmEnabled(ctx context.Context) (bool, error) {
 	return swarmEnabled.val, swarmEnabled.err
 }
 
+// runtimeVersionCache caches a version string after a successful lookup.
+// Errors (including context cancellation) are not cached so that
+// subsequent calls can retry with a fresh context.
 type runtimeVersionCache struct {
-	once sync.Once
-	val  string
-	err  error
+	mu  sync.Mutex
+	val string
 }
 
-var runtimeVersion runtimeVersionCache
+// RuntimeAPIVersion returns the negotiated API version that will be used for
+// requests to the Docker daemon. It triggers version negotiation via Ping so
+// that version-gated request shaping matches the version subsequent API calls
+// will actually use.
+//
+// After negotiation, Compose should never rely on features or request attributes
+// not defined by this API version, even if the daemon's raw version is higher.
+func (s *composeService) RuntimeAPIVersion(ctx context.Context) (string, error) {
+	s.runtimeAPIVersion.mu.Lock()
+	defer s.runtimeAPIVersion.mu.Unlock()
+	if s.runtimeAPIVersion.val != "" {
+		return s.runtimeAPIVersion.val, nil
+	}
 
-func (s *composeService) RuntimeVersion(ctx context.Context) (string, error) {
-	// TODO(thaJeztah): this should use Client.ClientVersion), which has the negotiated version.
-	runtimeVersion.once.Do(func() {
-		version, err := s.apiClient().ServerVersion(ctx, client.ServerVersionOptions{})
-		if err != nil {
-			runtimeVersion.err = err
-		}
-		runtimeVersion.val = version.APIVersion
-	})
-	return runtimeVersion.val, runtimeVersion.err
+	cli := s.apiClient()
+	_, err := cli.Ping(ctx, client.PingOptions{NegotiateAPIVersion: true})
+	if err != nil {
+		return "", err
+	}
+
+	version := cli.ClientVersion()
+	if version == "" {
+		return "", fmt.Errorf("docker client returned empty version after successful API negotiation")
+	}
+
+	s.runtimeAPIVersion.val = version
+	return s.runtimeAPIVersion.val, nil
 }
diff --git a/pkg/compose/convergence_test.go b/pkg/compose/convergence_test.go
index 901f43ccea..27d312c0cb 100644
--- a/pkg/compose/convergence_test.go
+++ b/pkg/compose/convergence_test.go
@@ -411,11 +411,10 @@ func TestCreateMobyContainer(t *testing.T) {
 	apiClient.EXPECT().DaemonHost().Return("").AnyTimes()
 	apiClient.EXPECT().ImageInspect(anyCancellableContext(), gomock.Any()).Return(client.ImageInspectResult{}, nil).AnyTimes()
 
-	// force `RuntimeVersion` to fetch fresh version
-	runtimeVersion = runtimeVersionCache{}
-	apiClient.EXPECT().ServerVersion(gomock.Any(), gomock.Any()).Return(client.ServerVersionResult{
+	apiClient.EXPECT().Ping(gomock.Any(), client.PingOptions{NegotiateAPIVersion: true}).Return(client.PingResult{
 		APIVersion: "1.44",
 	}, nil).AnyTimes()
+	apiClient.EXPECT().ClientVersion().Return("1.44").AnyTimes()
 
 	service := types.ServiceConfig{
 		Name: "test",
@@ -498,3 +497,65 @@ func TestCreateMobyContainer(t *testing.T) {
 	assert.DeepEqual(t, want, got, cmpopts.EquateComparable(netip.Addr{}), cmpopts.EquateEmpty())
 	assert.NilError(t, err)
 }
+
+func TestRuntimeAPIVersionCachesNegotiation(t *testing.T) {
+	mockCtrl := gomock.NewController(t)
+	defer mockCtrl.Finish()
+
+	apiClient := mocks.NewMockAPIClient(mockCtrl)
+	cli := mocks.NewMockCli(mockCtrl)
+	tested := &composeService{dockerCli: cli}
+
+	cli.EXPECT().Client().Return(apiClient).AnyTimes()
+
+	// Ping reports the server's max API version (1.44), but after negotiation
+	// the client may settle on a lower version (1.43) — e.g. when the client
+	// SDK caps at an older version. RuntimeAPIVersion must return the negotiated
+	// ClientVersion, not the server's raw APIVersion.
+	apiClient.EXPECT().Ping(gomock.Any(), client.PingOptions{NegotiateAPIVersion: true}).Return(client.PingResult{
+		APIVersion: "1.44",
+	}, nil).Times(1)
+	apiClient.EXPECT().ClientVersion().Return("1.43").Times(1)
+
+	version, err := tested.RuntimeAPIVersion(t.Context())
+	assert.NilError(t, err)
+	assert.Equal(t, version, "1.43")
+
+	version, err = tested.RuntimeAPIVersion(t.Context())
+	assert.NilError(t, err)
+	assert.Equal(t, version, "1.43")
+}
+
+func TestRuntimeAPIVersionRetriesOnTransientError(t *testing.T) {
+	mockCtrl := gomock.NewController(t)
+	defer mockCtrl.Finish()
+
+	apiClient := mocks.NewMockAPIClient(mockCtrl)
+	cli := mocks.NewMockCli(mockCtrl)
+	tested := &composeService{dockerCli: cli}
+
+	cli.EXPECT().Client().Return(apiClient).AnyTimes()
+
+	// First call: Ping fails with a transient error
+	firstCall := apiClient.EXPECT().Ping(gomock.Any(), client.PingOptions{NegotiateAPIVersion: true}).
+		Return(client.PingResult{}, context.DeadlineExceeded).Times(1)
+
+	// Second call: Ping succeeds after the transient failure
+	apiClient.EXPECT().Ping(gomock.Any(), client.PingOptions{NegotiateAPIVersion: true}).
+		Return(client.PingResult{APIVersion: "1.44"}, nil).Times(1).After(firstCall)
+	apiClient.EXPECT().ClientVersion().Return("1.44").Times(1)
+
+	// First call should return the transient error
+	_, err := tested.RuntimeAPIVersion(t.Context())
+	assert.ErrorIs(t, err, context.DeadlineExceeded)
+
+	// Second call should succeed — error was not cached
+	version, err := tested.RuntimeAPIVersion(t.Context())
+	assert.NilError(t, err)
+	assert.Equal(t, version, "1.44")
+
+	// Third call should return the cached value without calling Ping again
+	version, err = tested.RuntimeAPIVersion(t.Context())
+	assert.NilError(t, err)
+	assert.Equal(t, version, "1.44")
+}
diff --git a/pkg/compose/create.go b/pkg/compose/create.go
index 23cba9f5d1..78db3d0fd8 100644
--- a/pkg/compose/create.go
+++ b/pkg/compose/create.go
@@ -252,7 +252,7 @@ func (s *composeService) getCreateConfigs(ctx context.Context,
 	if err != nil {
 		return createConfigs{}, err
 	}
-	apiVersion, err := s.RuntimeVersion(ctx)
+	apiVersion, err := s.RuntimeAPIVersion(ctx)
 	if err != nil {
 		return createConfigs{}, err
 	}
@@ -897,7 +897,9 @@ func (s *composeService) buildContainerVolumes(
 				}
 			}
 		case mount.TypeImage:
-			version, err := s.RuntimeVersion(ctx)
+			// The daemon validates image mounts against the negotiated API version
+			// from the request path, not the server's own max version.
+			version, err := s.RuntimeAPIVersion(ctx)
 			if err != nil {
 				return nil, nil, err
 			}
diff --git a/pkg/compose/hook.go b/pkg/compose/hook.go
index 54e55652cc..8acc24011f 100644
--- a/pkg/compose/hook.go
+++ b/pkg/compose/hook.go
@@ -31,7 +31,7 @@ import (
 	"github.com/docker/compose/v5/pkg/utils"
 )
 
-func (s composeService) runHook(ctx context.Context, ctr container.Summary, service types.ServiceConfig, hook types.ServiceHook, listener api.ContainerEventListener) error {
+func (s *composeService) runHook(ctx context.Context, ctr container.Summary, service types.ServiceConfig, hook types.ServiceHook, listener api.ContainerEventListener) error {
 	wOut := utils.GetWriter(func(line string) {
 		listener(api.ContainerEvent{
 			Type:    api.HookEventLog,
@@ -96,7 +96,7 @@ func (s composeService) runHook(ctx context.Context, ctr container.Summary, serv
 	return nil
 }
 
-func (s composeService) runWaitExec(ctx context.Context, execID string, service types.ServiceConfig, listener api.ContainerEventListener) error {
+func (s *composeService) runWaitExec(ctx context.Context, execID string, service types.ServiceConfig, listener api.ContainerEventListener) error {
 	_, err := s.apiClient().ExecStart(ctx, execID, client.ExecStartOptions{
 		Detach: listener == nil,
 		TTY:    service.Tty,
diff --git a/pkg/compose/images.go b/pkg/compose/images.go
index 155405213c..d97f181220 100644
--- a/pkg/compose/images.go
+++ b/pkg/compose/images.go
@@ -56,7 +56,9 @@ func (s *composeService) Images(ctx context.Context, projectName string, options
 		containers = allContainers.Items
 	}
 
-	version, err := s.RuntimeVersion(ctx)
+	// The daemon validates the platform field in ImageInspect against the
+	// negotiated API version from the request path, not the server's own max version.
+	version, err := s.RuntimeAPIVersion(ctx)
 	if err != nil {
 		return nil, err
 	}
diff --git a/pkg/compose/images_test.go b/pkg/compose/images_test.go
index 25be1ac952..9a7d2c12e2 100644
--- a/pkg/compose/images_test.go
+++ b/pkg/compose/images_test.go
@@ -41,7 +41,8 @@ func TestImages(t *testing.T) {
 
 	args := projectFilter(strings.ToLower(testProject))
 	listOpts := client.ContainerListOptions{All: true, Filters: args}
-	api.EXPECT().ServerVersion(gomock.Any(), gomock.Any()).Return(client.ServerVersionResult{APIVersion: "1.96"}, nil).AnyTimes()
+	api.EXPECT().Ping(gomock.Any(), client.PingOptions{NegotiateAPIVersion: true}).Return(client.PingResult{APIVersion: "1.96"}, nil).AnyTimes()
+	api.EXPECT().ClientVersion().Return("1.96").AnyTimes()
 	timeStr1 := "2025-06-06T06:06:06.000000000Z"
 	created1, _ := time.Parse(time.RFC3339Nano, timeStr1)
 	timeStr2 := "2025-03-03T03:03:03.000000000Z"
PATCH

# Sanity: verify the patch landed by looking for the distinctive new function.
grep -q 'func (s \*composeService) RuntimeAPIVersion(' pkg/compose/compose.go
echo "Gold patch applied."

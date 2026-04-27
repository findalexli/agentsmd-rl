#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compose

# Idempotency check — distinctive line from the patch.
if grep -q 'apiVersion144 = "1.44"' pkg/compose/api_versions.go 2>/dev/null; then
    echo "Patch already applied; skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/pkg/compose/api_versions.go b/pkg/compose/api_versions.go
index bccb4ad277..d39aef8aac 100644
--- a/pkg/compose/api_versions.go
+++ b/pkg/compose/api_versions.go
@@ -19,6 +19,16 @@ package compose
 // Docker Engine API version constants.
 // These versions correspond to specific Docker Engine releases and their features.
 const (
+	// apiVersion144 represents Docker Engine API version 1.44 (Engine v25.0).
+	//
+	// New features in this version:
+	//  - ContainerCreate API accepts multiple EndpointsConfig entries
+	//
+	// Before this version:
+	//  - Only a single EndpointsConfig entry was accepted in ContainerCreate
+	//  - Extra networks must be connected individually after container creation via NetworkConnect
+	apiVersion144 = "1.44"
+
 	// apiVersion148 represents Docker Engine API version 1.48 (Engine v28.0).
 	//
 	// New features in this version:
diff --git a/pkg/compose/convergence.go b/pkg/compose/convergence.go
index b480b6be9d..973699e894 100644
--- a/pkg/compose/convergence.go
+++ b/pkg/compose/convergence.go
@@ -33,6 +33,7 @@ import (
 	"github.com/moby/moby/api/types/container"
 	mmount "github.com/moby/moby/api/types/mount"
 	"github.com/moby/moby/client"
+	"github.com/moby/moby/client/pkg/versions"
 	specs "github.com/opencontainers/image-spec/specs-go/v1"
 	"github.com/sirupsen/logrus"
 	"go.opentelemetry.io/otel/attribute"
@@ -732,6 +733,37 @@ func (s *composeService) createMobyContainer(ctx context.Context, project *types
 			Text:   warning,
 		})
 	}
+	// Starting API version 1.44, the ContainerCreate API call takes multiple networks
+	// so we include all configurations there and can skip the one-by-one calls here.
+	// For older API versions (e.g. Docker 20.10/API 1.41, Synology DSM 7.1/7.2),
+	// extra networks must be connected individually after creation via NetworkConnect.
+	apiVersion, err := s.RuntimeAPIVersion(ctx)
+	if err != nil {
+		return created, err
+	}
+	if versions.LessThan(apiVersion, apiVersion144) {
+		serviceNetworks := service.NetworksByPriority()
+		for _, networkKey := range serviceNetworks {
+			mobyNetworkName := project.Networks[networkKey].Name
+			if string(cfgs.Host.NetworkMode) == mobyNetworkName {
+				// primary network already configured as part of ContainerCreate
+				continue
+			}
+			epSettings, err := createEndpointSettings(project, service, number, networkKey, cfgs.Links, opts.UseNetworkAliases)
+			if err != nil {
+				_, _ = s.apiClient().ContainerRemove(ctx, response.ID, client.ContainerRemoveOptions{Force: true})
+				return created, err
+			}
+			if _, err := s.apiClient().NetworkConnect(ctx, mobyNetworkName, client.NetworkConnectOptions{
+				Container:      response.ID,
+				EndpointConfig: epSettings,
+			}); err != nil {
+				_, _ = s.apiClient().ContainerRemove(ctx, response.ID, client.ContainerRemoveOptions{Force: true})
+				return created, err
+			}
+		}
+	}
+
 	res, err := s.apiClient().ContainerInspect(ctx, response.ID, client.ContainerInspectOptions{})
 	if err != nil {
 		return created, err
diff --git a/pkg/compose/create.go b/pkg/compose/create.go
index 78db3d0fd8..cc0b4afbce 100644
--- a/pkg/compose/create.go
+++ b/pkg/compose/create.go
@@ -563,13 +563,17 @@ func defaultNetworkSettings(project *types.Project,
 	// so we can pass all the extra networks we want the container to be connected to
 	// in the network configuration instead of connecting the container to each extra
 	// network individually after creation.
-	for _, networkKey := range serviceNetworks {
-		epSettings, err := createEndpointSettings(project, service, serviceIndex, networkKey, links, useNetworkAliases)
-		if err != nil {
-			return "", nil, err
+	// For older API versions, extra networks are connected via NetworkConnect after
+	// container creation (see createMobyContainer in convergence.go).
+	if !versions.LessThan(version, apiVersion144) {
+		for _, networkKey := range serviceNetworks {
+			epSettings, err := createEndpointSettings(project, service, serviceIndex, networkKey, links, useNetworkAliases)
+			if err != nil {
+				return "", nil, err
+			}
+			mobyNetworkName := project.Networks[networkKey].Name
+			endpointsConfig[mobyNetworkName] = epSettings
 		}
-		mobyNetworkName := project.Networks[networkKey].Name
-		endpointsConfig[mobyNetworkName] = epSettings
 	}

 	networkConfig := &network.NetworkingConfig{
PATCH

echo "Patch applied successfully."

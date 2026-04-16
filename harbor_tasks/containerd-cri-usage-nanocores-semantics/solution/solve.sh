#!/bin/bash
set -e

cd /workspace/containerd

# Apply the gold patch for containerd/containerd#13138
# This patch changes getUsageNanoCores to return *uint64 instead of uint64
# to mirror cAdvisor's CpuInst behavior - leave field unset when there's
# not enough data to compute an instantaneous rate.

cat <<'PATCH' | git apply -
diff --git a/internal/cri/server/container_stats_list.go b/internal/cri/server/container_stats_list.go
index 9896eb75eb12a..adcd02a672323 100644
--- a/internal/cri/server/container_stats_list.go
+++ b/internal/cri/server/container_stats_list.go
@@ -156,14 +156,18 @@ func (c *criService) toContainerStats(
 		}

 		if cs.stats.Cpu != nil && cs.stats.Cpu.UsageCoreNanoSeconds != nil {
-			// UsageNanoCores is a calculated value and should be computed for all OSes
+			// UsageNanoCores is a calculated value and should be computed for all OSes.
+			// Leave it unset when there is not enough data to compute an instantaneous
+			// rate yet, which mirrors cAdvisor's CpuInst behavior.
 			nanoUsage, err := c.getUsageNanoCores(cntr.Metadata.ID, false, cs.stats.Cpu.UsageCoreNanoSeconds.Value, time.Unix(0, cs.stats.Cpu.Timestamp))
 			if err != nil {
 				// If an error occurred when getting nano cores usage, skip the container
 				log.G(ctx).WithError(err).Warnf("failed to get usage nano cores for container %q", cntr.ID)
 				continue
 			}
-			cs.stats.Cpu.UsageNanoCores = &runtime.UInt64Value{Value: nanoUsage}
+			if nanoUsage != nil {
+				cs.stats.Cpu.UsageNanoCores = &runtime.UInt64Value{Value: *nanoUsage}
+			}
 		}
 		css = append(css, cs)
 	}
@@ -178,13 +182,13 @@ func (c *criService) toCRIContainerStats(css []containerStats) *runtime.ListCont
 	return containerStats
 }

-func (c *criService) getUsageNanoCores(containerID string, isSandbox bool, currentUsageCoreNanoSeconds uint64, currentTimestamp time.Time) (uint64, error) {
+func (c *criService) getUsageNanoCores(containerID string, isSandbox bool, currentUsageCoreNanoSeconds uint64, currentTimestamp time.Time) (*uint64, error) {
 	// First, try to get pre-calculated UsageNanoCores from the background stats collector.
 	// This ensures we have valid data even on the first query (as the collector runs
 	// continuously in the background, similar to cAdvisor's housekeeping).
 	if c.statsCollector != nil {
 		if usageNanoCores, ok := c.statsCollector.GetUsageNanoCores(containerID); ok {
-			return usageNanoCores, nil
+			return &usageNanoCores, nil
 		}
 	}

@@ -195,13 +199,13 @@ func (c *criService) getUsageNanoCores(containerID string, isSandbox bool, curre
 	if isSandbox {
 		sandbox, err := c.sandboxStore.Get(containerID)
 		if err != nil {
-			return 0, fmt.Errorf("failed to get sandbox container: %s: %w", containerID, err)
+			return nil, fmt.Errorf("failed to get sandbox container: %s: %w", containerID, err)
 		}
 		oldStats = sandbox.Stats
 	} else {
 		container, err := c.containerStore.Get(containerID)
 		if err != nil {
-			return 0, fmt.Errorf("failed to get container ID: %s: %w", containerID, err)
+			return nil, fmt.Errorf("failed to get container ID: %s: %w", containerID, err)
 		}
 		oldStats = container.Stats
 	}
@@ -214,27 +218,27 @@ func (c *criService) getUsageNanoCores(containerID string, isSandbox bool, curre
 		if isSandbox {
 			err := c.sandboxStore.UpdateContainerStats(containerID, newStats)
 			if err != nil {
-				return 0, fmt.Errorf("failed to update sandbox stats container ID: %s: %w", containerID, err)
+				return nil, fmt.Errorf("failed to update sandbox stats container ID: %s: %w", containerID, err)
 			}
 		} else {
 			err := c.containerStore.UpdateContainerStats(containerID, newStats)
 			if err != nil {
-				return 0, fmt.Errorf("failed to update container stats ID: %s: %w", containerID, err)
+				return nil, fmt.Errorf("failed to update container stats ID: %s: %w", containerID, err)
 			}
 		}
-		return 0, nil
+		return nil, nil
 	}

 	nanoSeconds := currentTimestamp.UnixNano() - oldStats.Timestamp.UnixNano()

 	// zero or negative interval
 	if nanoSeconds <= 0 {
-		return 0, nil
+		return nil, nil
 	}

 	// can't go backwards, this value might come in as 0 if the container was just removed
 	if currentUsageCoreNanoSeconds < oldStats.UsageCoreNanoSeconds {
-		return 0, nil
+		return nil, nil
 	}

 	newUsageNanoCores := uint64(float64(currentUsageCoreNanoSeconds-oldStats.UsageCoreNanoSeconds) /
@@ -247,16 +251,16 @@ func (c *criService) getUsageNanoCores(containerID string, isSandbox bool, curre
 	if isSandbox {
 		err := c.sandboxStore.UpdateContainerStats(containerID, newStats)
 		if err != nil {
-			return 0, fmt.Errorf("failed to update sandbox container stats: %s: %w", containerID, err)
+			return nil, fmt.Errorf("failed to update sandbox container stats: %s: %w", containerID, err)
 		}
 	} else {
 		err := c.containerStore.UpdateContainerStats(containerID, newStats)
 		if err != nil {
-			return 0, fmt.Errorf("failed to update container stats ID: %s: %w", containerID, err)
+			return nil, fmt.Errorf("failed to update container stats ID: %s: %w", containerID, err)
 		}
 	}

-	return newUsageNanoCores, nil
+	return &newUsageNanoCores, nil
 }

 func (c *criService) normalizeContainerStatsFilter(filter *runtime.ContainerStatsFilter) {
diff --git a/internal/cri/server/container_stats_list_test.go b/internal/cri/server/container_stats_list_test.go
index c5b884351811e..f22beedb2c453 100644
--- a/internal/cri/server/container_stats_list_test.go
+++ b/internal/cri/server/container_stats_list_test.go
@@ -49,24 +49,24 @@ func TestContainerMetricsCPUNanoCoreUsage(t *testing.T) {
 		desc                        string
 		firstCPUValue               uint64
 		secondCPUValue              uint64
-		expectedNanoCoreUsageFirst  uint64
-		expectedNanoCoreUsageSecond uint64
+		expectedNanoCoreUsageFirst  *uint64
+		expectedNanoCoreUsageSecond *uint64
 	}{
 		{
 			id:                          "id1",
-			desc:                        "metrics",
+			desc:                        "normal increase",
 			firstCPUValue:               50,
 			secondCPUValue:              500,
-			expectedNanoCoreUsageFirst:  0,
-			expectedNanoCoreUsageSecond: 45,
+			expectedNanoCoreUsageFirst:  nil,
+			expectedNanoCoreUsageSecond: uint64Ptr(45),
 		},
 		{
 			id:                          "id2",
-			desc:                        "metrics",
+			desc:                        "counter goes backwards",
 			firstCPUValue:               234235,
 			secondCPUValue:              0,
-			expectedNanoCoreUsageFirst:  0,
-			expectedNanoCoreUsageSecond: 0,
+			expectedNanoCoreUsageFirst:  nil,
+			expectedNanoCoreUsageSecond: nil,
 		},
 	} {
 		t.Run(test.desc, func(t *testing.T) {
@@ -98,6 +98,8 @@ func TestContainerMetricsCPUNanoCoreUsage(t *testing.T) {
 	}
 }

+func uint64Ptr(v uint64) *uint64 { return &v }
+
 func TestGetWorkingSet(t *testing.T) {
 	for _, test := range []struct {
 		desc     string
diff --git a/internal/cri/server/sandbox_stats_linux.go b/internal/cri/server/sandbox_stats_linux.go
index 2954ddc757243..9af32327bc839 100644
--- a/internal/cri/server/sandbox_stats_linux.go
+++ b/internal/cri/server/sandbox_stats_linux.go
@@ -68,7 +68,9 @@ func (c *criService) podSandboxStats(
 		if err != nil {
 			return nil, fmt.Errorf("failed to get usage nano cores: %w", err)
 		}
-		cpuStats.UsageNanoCores = &runtime.UInt64Value{Value: nanoUsage}
+		if nanoUsage != nil {
+			cpuStats.UsageNanoCores = &runtime.UInt64Value{Value: *nanoUsage}
+		}
 	}
 	podSandboxStats.Linux.Cpu = cpuStats

diff --git a/internal/cri/server/stats_collector.go b/internal/cri/server/stats_collector.go
index c92facbb04296..76658535b21b8 100644
--- a/internal/cri/server/stats_collector.go
+++ b/internal/cri/server/stats_collector.go
@@ -271,7 +271,7 @@ func (c *StatsCollector) addSample(id string, timestamp time.Time, usageCoreNano
 	store.Add(timestamp, usageCoreNanoSeconds)
 }

-// GetUsageNanoCores returns the latest calculated UsageNanoCores for the given
+// GetUsageNanoCores returns the latest instantaneous UsageNanoCores rate for the given
 // container/sandbox ID. Returns 0 and false if no data is available or if
 // there aren't enough samples to calculate the rate.
 func (c *StatsCollector) GetUsageNanoCores(id string) (uint64, bool) {
PATCH

echo "Patch applied successfully"

# Verify distinctive line is present (idempotency check)
if ! grep -q "Leave it unset when there is not enough data to compute an instantaneous" internal/cri/server/container_stats_list.go; then
    echo "ERROR: Patch was not applied correctly"
    exit 1
fi

echo "Solve complete - gold patch applied"

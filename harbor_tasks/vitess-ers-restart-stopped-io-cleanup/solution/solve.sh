#!/usr/bin/env bash
# Apply the gold source patch from PR vitessio/vitess#19805.
# This script is idempotent: a distinctive marker line proves the patch is in place.
set -euo pipefail

cd /workspace/vitess

MARKER='replicasToRestart is the list of replicas that need replication to be restarted'
if grep -q "$MARKER" go/vt/vtctl/reparentutil/emergency_reparenter.go; then
    echo "patch already applied; nothing to do"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/go/vt/vtctl/reparentutil/emergency_reparenter.go b/go/vt/vtctl/reparentutil/emergency_reparenter.go
index ea50313c1b9..01aed70c4e4 100644
--- a/go/vt/vtctl/reparentutil/emergency_reparenter.go
+++ b/go/vt/vtctl/reparentutil/emergency_reparenter.go
@@ -150,6 +150,12 @@ func (erp *EmergencyReparenter) reparentShardLocked(ctx context.Context, ev *eve
 
 	var (
 		stoppedReplicationSnapshot *replicationSnapshot
+
+		// replicasToRestart is the list of replicas that need replication to be restarted
+		// in the case of an error after their IO threads have been stopped, but before
+		// the ERS restarts them as part of a successful reparent.
+		replicasToRestart []*topodatapb.Tablet
+
 		shardInfo                  *topo.ShardInfo
 		prevPrimary                *topodatapb.Tablet
 		tabletMap                  map[string]*topo.TabletInfo
@@ -162,6 +168,32 @@ func (erp *EmergencyReparenter) reparentShardLocked(ctx context.Context, ev *eve
 		isGTIDBased                bool
 	)
 
+	defer func() {
+		// If we succeeded, or there are no replicas that need replication restarted,
+		// we can return early.
+		if err == nil || len(replicasToRestart) == 0 {
+			return
+		}
+
+		// We create a new context with a fresh timeout so that the parent context does not cancel early while
+		// we attempt to restart replication on the stopped replicas.
+		ctx, cancel := context.WithTimeout(context.WithoutCancel(ctx), topo.RemoteOperationTimeout)
+		defer cancel()
+
+		// Make sure we still have the shard lock.
+		if lockErr := topo.CheckShardLocked(ctx, keyspace, shard); lockErr != nil {
+			erp.logger.Warningf("skipping replication restart cleanup because the shard lock was lost for %s/%s: %v", keyspace, shard, lockErr)
+			return
+		}
+
+		cleanupErr := erp.restartReplicationOnStoppedReplicas(ctx, prevPrimary, replicasToRestart, opts.durability)
+		if cleanupErr == nil {
+			return
+		}
+
+		err = fmt.Errorf("%w, and restart replication cleanup failed: %v", err, cleanupErr)
+	}()
+
 	shardInfo, err = erp.ts.GetShard(ctx, keyspace, shard)
 	if err != nil {
 		return err
@@ -206,6 +238,16 @@ func (erp *EmergencyReparenter) reparentShardLocked(ctx context.Context, ev *eve
 
 	// Stop replication on all the tablets and build their status map
 	stoppedReplicationSnapshot, err = stopReplicationAndBuildStatusMaps(ctx, erp.tmc, ev, tabletMap, shardInfo.PrimaryAlias, topo.RemoteOperationTimeout, opts.IgnoreReplicas, opts.NewPrimaryAlias, opts.durability, opts.WaitAllTablets, erp.logger)
+
+	// If stoppedReplicationSnapshot is not nil, it means we have stopped replication on at
+	// least one replica. We'll keep track of the replicas that had their IO threads stopped
+	// so we can restart them later in case of an error that causes us to return early and
+	// leaves replication stopped. We do this before checking the error so that we ensure we
+	// handle partial failures (where we've stopped some replicas but failed on others) correctly.
+	if stoppedReplicationSnapshot != nil {
+		replicasToRestart = stoppedReplicationSnapshot.replicasWithStoppedIO(tabletMap)
+	}
+
 	if err != nil {
 		return vterrors.Wrapf(err, "failed to stop replication and build status maps: %v", err)
 	}
@@ -276,6 +318,10 @@ func (erp *EmergencyReparenter) reparentShardLocked(ctx context.Context, ev *eve
 		return vterrors.Wrap(err, lostTopologyLockMsg)
 	}
 
+	// Relay logs have been successfully applied and we're ready to start repointing replicas,
+	// so we no longer need to restart replication manually in the event of an error.
+	replicasToRestart = nil
+
 	// initialize the newPrimary with the intermediate source, override this value if it is not the ideal candidate
 	newPrimary := intermediateSource
 	if !isIdeal {
@@ -327,6 +373,46 @@ func (erp *EmergencyReparenter) reparentShardLocked(ctx context.Context, ev *eve
 	return err
 }
 
+// restartReplicationOnStoppedReplicas restarts replication on replicas whose IO threads were
+// stopped by ERS before the operation aborted.
+func (erp *EmergencyReparenter) restartReplicationOnStoppedReplicas(
+	ctx context.Context,
+	prevPrimary *topodatapb.Tablet,
+	replicas []*topodatapb.Tablet,
+	durability policy.Durabler,
+) error {
+	erp.logger.Infof("restarting replication on %d replicas whose IO threads were stopped by ERS", len(replicas))
+
+	rec := concurrency.AllErrorRecorder{}
+	wg := sync.WaitGroup{}
+
+	// Start replication on each stopped replica concurrently.
+	for _, replica := range replicas {
+		alias := topoproto.TabletAliasString(replica.Alias)
+
+		semiSync := false
+		if prevPrimary != nil {
+			semiSync = policy.IsReplicaSemiSync(durability, prevPrimary, replica)
+		}
+
+		wg.Go(func() {
+			erp.logger.Infof("restarting replication on %q after failed ERS", alias)
+			if err := erp.tmc.StartReplication(ctx, replica, semiSync); err != nil {
+				err := vterrors.Wrapf(err, "failed to restart replication on %q after failed ERS", alias)
+				rec.RecordError(err)
+			}
+		})
+	}
+
+	wg.Wait()
+
+	if rec.HasErrors() {
+		return rec.Error()
+	}
+
+	return nil
+}
+
 func (erp *EmergencyReparenter) waitForAllRelayLogsToApply(
 	ctx context.Context,
 	validCandidates map[string]*RelayLogPositions,
diff --git a/go/vt/vtctl/reparentutil/replication.go b/go/vt/vtctl/reparentutil/replication.go
index a9a5e341eb5..4c3e085c24e 100644
--- a/go/vt/vtctl/reparentutil/replication.go
+++ b/go/vt/vtctl/reparentutil/replication.go
@@ -207,6 +207,40 @@ type replicationSnapshot struct {
 	tabletsBackupState map[string]bool
 }
 
+// replicasWithStoppedIO returns the reachable replicas whose IO threads ERS
+// stopped and should restart during cleanup.
+func (rs *replicationSnapshot) replicasWithStoppedIO(tabletMap map[string]*topo.TabletInfo) []*topodatapb.Tablet {
+	replicas := make([]*topodatapb.Tablet, 0, len(rs.statusMap))
+
+	for alias, stopStatus := range rs.statusMap {
+		ioThreadWasRunning, err := replicaIOThreadWasRunning(stopStatus)
+		if err != nil || !ioThreadWasRunning {
+			continue
+		}
+
+		tabletInfo := tabletMap[alias]
+		if tabletInfo == nil || tabletInfo.Tablet == nil {
+			continue
+		}
+
+		replicas = append(replicas, tabletInfo.Tablet)
+	}
+
+	return replicas
+}
+
+// replicaIOThreadWasRunning returns true if a StopReplicationStatus indicates
+// that ERS stopped a healthy IO thread that should restart during cleanup.
+func replicaIOThreadWasRunning(stopStatus *replicationdatapb.StopReplicationStatus) (bool, error) {
+	if stopStatus == nil || stopStatus.Before == nil {
+		return false, vterrors.Errorf(vtrpc.Code_INVALID_ARGUMENT, "could not determine Before state of StopReplicationStatus %v", stopStatus)
+	}
+
+	replStatus := replication.ProtoToReplicationStatus(stopStatus.Before)
+
+	return replStatus.IOHealthy(), nil
+}
+
 // tabletAliasError wraps an error with the tablet alias that produced it.
 type tabletAliasError struct {
 	alias *topodatapb.TabletAlias
@@ -391,7 +425,7 @@ func stopReplicationAndBuildStatusMaps(
 	// check that the tablets we were able to reach are sufficient for us to guarantee that no new write will be accepted by any tablet
 	revokeSuccessful := haveRevoked(durability, res.reachableTablets, allTablets)
 	if !revokeSuccessful {
-		return nil, vterrors.Wrapf(errRecorder.Error(), "could not reach sufficient tablets to guarantee safety: %v", errRecorder.Error())
+		return res, vterrors.Wrapf(errRecorder.Error(), "could not reach sufficient tablets to guarantee safety: %v", errRecorder.Error())
 	}
 
 	return res, nil
PATCH

echo "patch applied"

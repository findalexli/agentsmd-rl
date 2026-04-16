#!/bin/bash
set -e

cd /workspace/prometheus

# Apply the gold patch to fix ST (Start Timestamp) append in agent mode
# This fixes the bug where ST was not being written to samples in the WAL
patch -p1 <<'PATCH'
diff --git a/tsdb/agent/db_append_v2.go b/tsdb/agent/db_append_v2.go
index bb2601e1e39..b963608637d 100644
--- a/tsdb/agent/db_append_v2.go
+++ b/tsdb/agent/db_append_v2.go
@@ -72,7 +72,6 @@ func (a *appenderV2) Append(ref storage.SeriesRef, ls labels.Labels, st, t int64
 	lastTS := s.lastTs
 	s.Unlock()

-	// TODO(bwplotka): Handle ST natively (as per PROM-60).
 	if a.opts.EnableSTAsZeroSample && st != 0 {
 		a.bestEffortAppendSTZeroSample(s, ls, lastTS, st, t, h, fh)
 	}
@@ -86,6 +85,7 @@ func (a *appenderV2) Append(ref storage.SeriesRef, ls labels.Labels, st, t int64
 	case fh != nil:
 		isStale = value.IsStaleNaN(fh.Sum)
 		// NOTE: always modify pendingFloatHistograms and floatHistogramSeries together
+		// TODO(krajorama,ywwg,bwplotka): Pass ST when available in WAL.
 		a.pendingFloatHistograms = append(a.pendingFloatHistograms, record.RefFloatHistogramSample{
 			Ref: s.ref,
 			T:   t,
@@ -95,6 +95,7 @@ func (a *appenderV2) Append(ref storage.SeriesRef, ls labels.Labels, st, t int64
 	case h != nil:
 		isStale = value.IsStaleNaN(h.Sum)
 		// NOTE: always modify pendingHistograms and histogramSeries together
+		// TODO(krajorama,ywwg,bwplotka): Pass ST when available in WAL.
 		a.pendingHistograms = append(a.pendingHistograms, record.RefHistogramSample{
 			Ref: s.ref,
 			T:   t,
@@ -107,6 +108,7 @@ func (a *appenderV2) Append(ref storage.SeriesRef, ls labels.Labels, st, t int64
 		// NOTE: always modify pendingSamples and sampleSeries together.
 		a.pendingSamples = append(a.pendingSamples, record.RefSample{
 			Ref: s.ref,
+			ST:  st,
 			T:   t,
 			V:   v,
 		})
PATCH

# Idempotency check: verify the fix was applied
grep -q "ST:  st," tsdb/agent/db_append_v2.go || {
    echo "ERROR: Patch not applied correctly - ST field not found"
    exit 1
}

echo "Patch applied successfully"

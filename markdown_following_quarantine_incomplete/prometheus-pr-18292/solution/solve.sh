#!/bin/bash
set -e

cd /workspace/prometheus

# Check if already patched - use distinctive line from the patch
if grep -q "SetUnlessAlreadySet" tsdb/agent/series.go; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 << 'PATCH'
diff --git a/tsdb/agent/db.go b/tsdb/agent/db.go
index f7e83ae7dd7..ac93e82c4bb 100644
--- a/tsdb/agent/db.go
+++ b/tsdb/agent/db.go
@@ -553,12 +553,13 @@ func (db *DB) loadWAL(r *wlog.Reader, duplicateRefToValidRef map[chunks.HeadSeri
 				}

 				series := &memSeries{ref: entry.Ref, lset: entry.Labels}
-				series, created := db.series.GetOrSet(series.lset.Hash(), series)
+				series, created := db.series.SetUnlessAlreadySet(series.lset.Hash(), series)

 				if !created {
-					// We don't need to check if entry.Ref exists / if the value is not series.ref because GetOrSet
-					// enforces that the same labels will always get the same Ref. If we did not create a new ref
-					// the only possible ref it should ever be in the WAL is series.ref.
+					// We don't need to check if entry.Ref exists / if the value is not series.ref because
+					// SetUnlessAlreadySet is "first insertion wins": during single-threaded WAL replay the
+					// first ref written for a given label set is the canonical one. Any later WAL record for
+					// the same labels must carry that same ref, so series.ref is the only valid ref here.
 					duplicateRefToValidRef[entry.Ref] = series.ref

 					// We want to track the largest segment where we encountered the duplicate ref, so we can ensure
@@ -873,16 +874,9 @@ func (a *appender) SetOptions(opts *storage.AppendOptions) {
 }

 func (a *appender) Append(ref storage.SeriesRef, l labels.Labels, t int64, v float64) (storage.SeriesRef, error) {
-	// series references and chunk references are identical for agent mode.
-	headRef := chunks.HeadSeriesRef(ref)
-
-	series := a.series.GetByID(headRef)
-	if series == nil {
-		var err error
-		series, err = a.getOrCreate(l)
-		if err != nil {
-			return 0, err
-		}
+	series, err := a.getOrCreate(chunks.HeadSeriesRef(ref), l)
+	if err != nil {
+		return 0, err
 	}

 	series.Lock()
@@ -905,7 +899,14 @@ func (a *appender) Append(ref storage.SeriesRef, l labels.Labels, t int64, v flo
 	return storage.SeriesRef(series.ref), nil
 }

-func (a *appenderBase) getOrCreate(l labels.Labels) (series *memSeries, err error) {
+func (a *appenderBase) getOrCreate(ref chunks.HeadSeriesRef, l labels.Labels) (series *memSeries, err error) {
+	// Fastest path: caller already has a valid ref from a prior append.
+	if ref != 0 {
+		if series = a.series.GetByID(ref); series != nil {
+			return series, nil
+		}
+	}
+
 	// Ensure no empty or duplicate labels have gotten through. This mirrors the
 	// equivalent validation code in the TSDB's headAppender.
 	l = l.WithoutEmpty()
@@ -919,15 +920,27 @@ func (a *appenderBase) getOrCreate(l labels.Labels) (series *memSeries, err erro

 	hash := l.Hash()

-	series = a.series.GetByHash(hash, l)
-	if series != nil {
+	// Fast path: series already exists. This avoids burning a ref via
+	// nextRef.Inc() on every append for an already-known series.
+	if series = a.series.GetByHash(hash, l); series != nil {
 		return series, nil
 	}

-	ref := chunks.HeadSeriesRef(a.nextRef.Inc())
-	series = &memSeries{ref: ref, lset: l, lastTs: math.MinInt64}
-	a.series.Set(hash, series)
+	// Note this ref is wasted if a concurrent goroutine inserts the same series first.
+	newRef := chunks.HeadSeriesRef(a.nextRef.Inc())
+	var created bool
+	series, created = a.series.SetUnlessAlreadySet(hash, &memSeries{ref: newRef, lset: l, lastTs: math.MinInt64})
+	if !created {
+		// A concurrent goroutine inserted this series first; skip the WAL
+		// record and metric update.
+		return series, nil
+	}

+	// Known limitation: unlike the TSDB head, agent memSeries has no
+	// pendingCommit flag. Between this point and the first sample write that
+	// updates series.lastTs, GC may remove the series (lastTs == math.MinInt64
+	// satisfies mint > lastTs). The WAL record appended below would then
+	// reference a ref with no corresponding in-memory series.
 	a.pendingSeries = append(a.pendingSeries, record.RefSeries{
 		Ref:    series.ref,
 		Labels: l,
@@ -1008,16 +1021,9 @@ func (a *appender) AppendHistogram(ref storage.SeriesRef, l labels.Labels, t int
 		}
 	}

-	// series references and chunk references are identical for agent mode.
-	headRef := chunks.HeadSeriesRef(ref)
-
-	series := a.series.GetByID(headRef)
-	if series == nil {
-		var err error
-		series, err = a.getOrCreate(l)
-		if err != nil {
-			return 0, err
-		}
+	series, err := a.getOrCreate(chunks.HeadSeriesRef(ref), l)
+	if err != nil {
+		return 0, err
 	}

 	series.Lock()
@@ -1071,13 +1077,9 @@ func (a *appender) AppendHistogramSTZeroSample(ref storage.SeriesRef, l labels.L
 		return 0, storage.ErrSTNewerThanSample
 	}

-	series := a.series.GetByID(chunks.HeadSeriesRef(ref))
-	if series == nil {
-		var err error
-		series, err = a.getOrCreate(l)
-		if err != nil {
-			return 0, err
-		}
+	series, err := a.getOrCreate(chunks.HeadSeriesRef(ref), l)
+	if err != nil {
+		return 0, err
 	}

 	series.Lock()
@@ -1123,13 +1125,9 @@ func (a *appender) AppendSTZeroSample(ref storage.SeriesRef, l labels.Labels, t,
 		return 0, storage.ErrSTNewerThanSample
 	}

-	series := a.series.GetByID(chunks.HeadSeriesRef(ref))
-	if series == nil {
-		var err error
-		series, err = a.getOrCreate(l)
-		if err != nil {
-			return 0, err
-		}
+	series, err := a.getOrCreate(chunks.HeadSeriesRef(ref), l)
+	if err != nil {
+		return 0, err
 	}

 	series.Lock()
diff --git a/tsdb/agent/db_append_v2.go b/tsdb/agent/db_append_v2.go
index bb2601e1e39..787fc34c587 100644
--- a/tsdb/agent/db_append_v2.go
+++ b/tsdb/agent/db_append_v2.go
@@ -59,13 +59,9 @@ func (a *appenderV2) Append(ref storage.SeriesRef, ls labels.Labels, st, t int64
 	}

 	// series references and chunk references are identical for agent mode.
-	s := a.series.GetByID(chunks.HeadSeriesRef(ref))
-	if s == nil {
-		var err error
-		s, err = a.getOrCreate(ls)
-		if err != nil {
-			return 0, err
-		}
+	s, err := a.getOrCreate(chunks.HeadSeriesRef(ref), ls)
+	if err != nil {
+		return 0, err
 	}

 	s.Lock()
diff --git a/tsdb/agent/db_test.go b/tsdb/agent/db_test.go
index e6b8cadc228..1df0e26d46d 100644
--- a/tsdb/agent/db_test.go
+++ b/tsdb/agent/db_test.go
@@ -21,6 +21,7 @@ import (
 	"math"
 	"path/filepath"
 	"strconv"
+	"sync"
 	"testing"
 	"time"

@@ -103,6 +104,61 @@ func createTestAgentDB(t testing.TB, reg prometheus.Registerer, opts *Options) *
 	return db
 }

+// TestConcurrentAppendSameLabels verifies that concurrent appends for the same
+// label set produce exactly one series in memory and one series record in the WAL.
+func TestConcurrentAppendSameLabels(t *testing.T) {
+	opts := DefaultOptions()
+	opts.OutOfOrderTimeWindow = math.MaxInt64
+	db := createTestAgentDB(t, nil, opts)
+	lset := labels.FromStrings("__name__", "test_metric")
+
+	const n = 100
+	var wg sync.WaitGroup
+	start := make(chan struct{})
+
+	wg.Add(n)
+	for range n {
+		go func() {
+			defer wg.Done()
+			app := db.Appender(context.Background())
+			<-start
+			_, err := app.Append(0, lset, 1000, 1.0)
+			require.NoError(t, err)
+			require.NoError(t, app.Commit())
+		}()
+	}
+	close(start)
+	wg.Wait()
+
+	var total int
+	for i := range db.series.size {
+		db.series.locks[i].RLock()
+		total += len(db.series.series[i])
+		db.series.locks[i].RUnlock()
+	}
+	require.Equal(t, 1, total)
+	require.NoError(t, db.Close())
+
+	sr, err := wlog.NewSegmentsReader(db.wal.Dir())
+	require.NoError(t, err)
+	defer func() { require.NoError(t, sr.Close()) }()
+
+	r := wlog.NewReader(sr)
+	dec := record.NewDecoder(labels.NewSymbolTable(), promslog.NewNopLogger())
+	var walSeries int
+	for r.Next() {
+		rec := r.Record()
+		if dec.Type(rec) == record.Series {
+			var s []record.RefSeries
+			s, err = dec.Series(rec, s)
+			require.NoError(t, err)
+			walSeries += len(s)
+		}
+	}
+	require.NoError(t, r.Err())
+	require.Equal(t, 1, walSeries)
+}
+
 func TestUnsupportedFunctions(t *testing.T) {
 	s := createTestAgentDB(t, nil, DefaultOptions())
 	defer s.Close()
@@ -1453,20 +1509,56 @@ func readWALSamples(t *testing.T, walDir string) []walSample {
 }

 func BenchmarkGetOrCreate(b *testing.B) {
-	s := createTestAgentDB(b, nil, DefaultOptions())
-	defer s.Close()
-
 	// NOTE: This benchmarks appenderBase, so it does not matter if it's V1 or V2.
-	app := s.Appender(context.Background()).(*appender)
-	lbls := make([]labels.Labels, b.N)
+	const n = 1_000
+
+	b.Run("new", func(b *testing.B) {
+		s := createTestAgentDB(b, nil, DefaultOptions())
+		defer s.Close()
+		app := s.Appender(context.Background()).(*appender)
+
+		// Fixed-size label set. Before each pass through the set we GC all series
+		// (they are created with lastTs==math.MinInt64, so mint=math.MaxInt64
+		// evicts everything) so every timed getOrCreate call takes the creation
+		// path. This keeps the stripe-series table at a stable size regardless of
+		// b.N, preventing per-op cost from growing with the benchmark iteration
+		// count.
+		lbls := make([]labels.Labels, n)
+		for i, l := range labelsForTest("benchmark_new", n) {
+			lbls[i] = labels.New(l...)
+		}

-	for i, l := range labelsForTest("benchmark", b.N) {
-		lbls[i] = labels.New(l...)
-	}
+		b.ResetTimer()

-	b.ResetTimer()
+		for i := range b.N {
+			if i%n == 0 && i > 0 {
+				b.StopTimer()
+				_ = s.series.GC(math.MaxInt64)
+				b.StartTimer()
+			}
+			app.getOrCreate(0, lbls[i%n])
+		}
+	})

-	for _, l := range lbls {
-		app.getOrCreate(l)
-	}
+	b.Run("existing", func(b *testing.B) {
+		s := createTestAgentDB(b, nil, DefaultOptions())
+		defer s.Close()
+		app := s.Appender(context.Background()).(*appender)
+
+		lbls := make([]labels.Labels, n)
+		for i, l := range labelsForTest("benchmark_existing", n) {
+			lbls[i] = labels.New(l...)
+		}
+
+		// Pre-populate all series so every timed call finds an existing series.
+		for _, l := range lbls {
+			app.getOrCreate(0, l)
+		}
+
+		b.ResetTimer()
+
+		for i := range b.N {
+			app.getOrCreate(0, lbls[i%n])
+		}
+	})
 }
diff --git a/tsdb/agent/series.go b/tsdb/agent/series.go
index 0c9f8203df6..9aa3143459a 100644
--- a/tsdb/agent/series.go
+++ b/tsdb/agent/series.go
@@ -161,10 +161,9 @@ func newStripeSeries(stripeSize int) *stripeSeries {
 // GC garbage collects old series that have not received a sample after mint
 // and will fully delete them.
 func (s *stripeSeries) GC(mint int64) map[chunks.HeadSeriesRef]struct{} {
-	// NOTE(rfratto): GC will grab two locks, one for the hash and the other for
-	// series. It's not valid for any other function to grab both locks,
-	// otherwise a deadlock might occur when running GC in parallel with
-	// appending.
+	// gcMut serializes GC calls. Within a single GC pass, the check function
+	// holds hashLock and then acquires refLock — callers must never hold both
+	// simultaneously, which SetUnlessAlreadySet satisfies.
 	s.gcMut.Lock()
 	defer s.gcMut.Unlock()

@@ -234,39 +233,47 @@ func (s *stripeSeries) GetByHash(hash uint64, lset labels.Labels) *memSeries {
 	return s.hashes[hashLock].Get(hash, lset)
 }

-func (s *stripeSeries) Set(hash uint64, series *memSeries) {
-	var (
-		hashLock = s.hashLock(hash)
-		refLock  = s.refLock(series.ref)
-	)
-
-	// We can't hold both locks at once otherwise we might deadlock with a
-	// simultaneous call to GC.
-	//
-	// We update s.series first because GC expects anything in s.hashes to
-	// already exist in s.series.
-	s.locks[refLock].Lock()
-	s.series[refLock][series.ref] = series
-	s.locks[refLock].Unlock()
+// SetUnlessAlreadySet inserts series for the given hash if no series with the
+// same label set already exists. It returns the canonical series and whether
+// it was newly inserted.
+//
+// Insertion order is refs-before-hashes. GC only discovers series via hashes,
+// so anything it finds is guaranteed to already be present in refs. We never
+// hold hashLock and refLock simultaneously, preserving the no-deadlock
+// invariant that GC relies on (it holds hashLock while acquiring refLock).
+func (s *stripeSeries) SetUnlessAlreadySet(hash uint64, series *memSeries) (*memSeries, bool) {
+	hashLock := s.hashLock(hash)

+	// Fast path: series already exists.
 	s.locks[hashLock].Lock()
-	s.hashes[hashLock].Set(hash, series)
+	if prev := s.hashes[hashLock].Get(hash, series.lset); prev != nil {
+		s.locks[hashLock].Unlock()
+		return prev, false
+	}
 	s.locks[hashLock].Unlock()
-}

-// GetOrSet returns the existing series for the given label set, or sets it if it does not exist.
-// It returns the series and a boolean indicating whether it was newly created.
-func (s *stripeSeries) GetOrSet(hash uint64, series *memSeries) (*memSeries, bool) {
-	hashLock := s.hashLock(hash)
+	// Insert into refs first. GC discovers series through hashes, so a series
+	// that is only in refs is invisible to GC and will not be removed.
+	refLock := s.refLock(series.ref)
+	s.locks[refLock].Lock()
+	s.series[refLock][series.ref] = series
+	s.locks[refLock].Unlock()

+	// Re-acquire hashLock to insert into hashes. A concurrent goroutine may
+	// have inserted the same label set while we were inserting into refs, so
+	// check again before committing.
 	s.locks[hashLock].Lock()
 	if prev := s.hashes[hashLock].Get(hash, series.lset); prev != nil {
 		s.locks[hashLock].Unlock()
+		// We lost the race: clean up the ref we pre-inserted.
+		s.locks[refLock].Lock()
+		delete(s.series[refLock], series.ref)
+		s.locks[refLock].Unlock()
 		return prev, false
 	}
+	s.hashes[hashLock].Set(hash, series)
 	s.locks[hashLock].Unlock()

-	s.Set(hash, series)
 	return series, true
 }

diff --git a/tsdb/agent/series_test.go b/tsdb/agent/series_test.go
index f8b6431a3e5..a5a6f04f4b7 100644
--- a/tsdb/agent/series_test.go
+++ b/tsdb/agent/series_test.go
@@ -56,7 +56,7 @@ func TestNoDeadlock(t *testing.T) {
 					"id": strconv.Itoa(i),
 				}),
 			}
-			stripeSeries.Set(series.lset.Hash(), series)
+			stripeSeries.SetUnlessAlreadySet(series.lset.Hash(), series)
 		}(i)
 	}

@@ -97,16 +97,18 @@ func labelsWithHashCollision() (labels.Labels, labels.Labels) {
 func stripeSeriesWithCollidingSeries(*testing.T) (*stripeSeries, *memSeries, *memSeries) {
 	lbls1, lbls2 := labelsWithHashCollision()
 	ms1 := memSeries{
+		ref:  chunks.HeadSeriesRef(1),
 		lset: lbls1,
 	}
 	ms2 := memSeries{
+		ref:  chunks.HeadSeriesRef(2),
 		lset: lbls2,
 	}
 	hash := lbls1.Hash()
 	s := newStripeSeries(1)

-	s.Set(hash, &ms1)
-	s.Set(hash, &ms2)
+	s.SetUnlessAlreadySet(hash, &ms1)
+	s.SetUnlessAlreadySet(hash, &ms2)

 	return s, &ms1, &ms2
 }
@@ -122,20 +124,137 @@ func TestStripeSeries_Get(t *testing.T) {
 	require.Same(t, ms2, got)
 }

-func TestStripeSeries_GetOrSet(t *testing.T) {
+func TestStripeSeries_SetUnlessAlreadySet(t *testing.T) {
 	lbl := labels.FromStrings("__name__", "metric", "lbl", "HFnEaGl")

 	ss := newStripeSeries(1)

-	ms, created := ss.GetOrSet(lbl.Hash(), &memSeries{ref: chunks.HeadSeriesRef(1), lset: lbl})
+	ms, created := ss.SetUnlessAlreadySet(lbl.Hash(), &memSeries{ref: chunks.HeadSeriesRef(1), lset: lbl})
 	require.True(t, created)
 	require.Equal(t, lbl, ms.lset)

-	ms2, created := ss.GetOrSet(lbl.Hash(), &memSeries{ref: chunks.HeadSeriesRef(2), lset: lbl})
+	ms2, created := ss.SetUnlessAlreadySet(lbl.Hash(), &memSeries{ref: chunks.HeadSeriesRef(2), lset: lbl})
 	require.False(t, created)
 	require.Equal(t, ms, ms2)
 }

+// TestSetUnlessAlreadySetConcurrentSameLabels verifies that concurrent SetUnlessAlreadySet calls for
+// the same label set produce exactly one canonical series: all callers get the
+// same pointer, the winning ref is reachable via GetByID, and losing refs are
+// cleaned up before the call returns and are therefore unreachable.
+func TestSetUnlessAlreadySetConcurrentSameLabels(t *testing.T) {
+	// size=1 forces all goroutines into the same hash bucket.
+	ss := newStripeSeries(1)
+	lset := labels.FromStrings("__name__", "test_metric")
+	hash := lset.Hash()
+
+	const n = 100
+	var wg sync.WaitGroup
+	start := make(chan struct{})
+	results := make([]*memSeries, n)
+
+	wg.Add(n)
+	for i := range n {
+		go func(i int) {
+			defer wg.Done()
+			<-start
+			results[i], _ = ss.SetUnlessAlreadySet(hash, &memSeries{ref: chunks.HeadSeriesRef(i + 1), lset: lset})
+		}(i)
+	}
+	close(start)
+	wg.Wait()
+
+	canonical := results[0]
+	for _, r := range results[1:] {
+		require.Same(t, canonical, r)
+	}
+	require.Same(t, canonical, ss.GetByID(canonical.ref))
+	for i := range n {
+		if ref := chunks.HeadSeriesRef(i + 1); ref != canonical.ref {
+			require.Nil(t, ss.GetByID(ref))
+		}
+	}
+}
+
+// TestSetUnlessAlreadySetConcurrentGC verifies that concurrent SetUnlessAlreadySet and GC do not
+// deadlock, that surviving series remain reachable throughout, and that GC-eligible series are
+// actually removed.
+func TestSetUnlessAlreadySetConcurrentGC(t *testing.T) {
+	ss := newStripeSeries(512)
+
+	var (
+		mu        sync.Mutex
+		survivors []*memSeries
+		eligible  []*memSeries
+		wg        sync.WaitGroup
+		start     = make(chan struct{})
+	)
+
+	wg.Add(50)
+	for w := range 50 {
+		go func(w int) {
+			defer wg.Done()
+			<-start
+			for r := range 20 {
+				lset := labels.FromStrings("w", strconv.Itoa(w), "r", strconv.Itoa(r))
+				// Odd r: survivor (lastTs=math.MaxInt64).
+				// Even r: GC-eligible (lastTs=0, removed by GC(1)).
+				lastTs := int64(0)
+				if r%2 == 1 {
+					lastTs = math.MaxInt64
+				}
+				s := &memSeries{ref: chunks.HeadSeriesRef(w*20 + r + 1), lset: lset, lastTs: lastTs}
+				if got, ok := ss.SetUnlessAlreadySet(lset.Hash(), s); ok {
+					mu.Lock()
+					if lastTs == math.MaxInt64 {
+						survivors = append(survivors, got)
+					} else {
+						eligible = append(eligible, got)
+					}
+					mu.Unlock()
+				}
+			}
+		}(w)
+	}
+
+	done := make(chan struct{})
+	go func() {
+		for {
+			select {
+			case <-done:
+				return
+				default:
+				ss.GC(1) // removes series with lastTs < 1, i.e. lastTs==0
+			}
+		}
+	}()
+
+	finished := make(chan struct{})
+	go func() { wg.Wait(); close(finished) }()
+	close(start)
+	select {
+	case <-finished:
+		close(done)
+	case <-time.After(15 * time.Second):
+		close(done)
+		t.Fatal("deadlock")
+	}
+
+	// Survivors must still be reachable by both ID and hash despite concurrent GC.
+	for _, s := range survivors {
+		require.Same(t, s, ss.GetByID(s.ref))
+		require.Same(t, s, ss.GetByHash(s.lset.Hash(), s.lset))
+	}
+
+	// A final synchronous GC pass ensures all eligible series are fully removed,
+	// then verify they are unreachable via both lookup paths.
+	ss.GC(1)
+	for _, s := range eligible {
+		require.Nil(t, ss.GetByID(s.ref))
+		require.Nil(t, ss.GetByHash(s.lset.Hash(), s.lset))
+	}
+}
+
 func TestStripeSeries_gc(t *testing.T) {
 	s, ms1, ms2 := stripeSeriesWithCollidingSeries(t)
 	hash := ms1.lset.Hash()
PATCH

echo "Patch applied successfully"

// +build ignore

package main

import (
	"fmt"
	"math"
	"os"
	"sync"

	"github.com/prometheus/prometheus/model/labels"
	"github.com/prometheus/prometheus/tsdb/agent"
	"github.com/prometheus/prometheus/tsdb/chunks"
)

// This test verifies the race condition in stripeSeries is fixed.
// It should FAIL on base commit (f99f3bb) and PASS with the fix.
func main() {
	// Try to use SetUnlessAlreadySet - this method should exist after fix
	// If it doesn't exist, the fix is incomplete
	fmt.Println("Testing SetUnlessAlreadySet race safety...")

	// Use stripeSeries directly to test the race
	ss := agent.NewStripeSeries(1) // size=1 forces all into same bucket

	lset := labels.FromStrings("__name__", "test_metric")
	hash := lset.Hash()

	const n = 100
	var wg sync.WaitGroup
	start := make(chan struct{})
	results := make([]*agent.MemSeries, n)

	wg.Add(n)
	for i := 0; i < n; i++ {
		go func(i int) {
			defer wg.Done()
			<-start
			// Try to call SetUnlessAlreadySet - this is the method added by the fix
			// If the method doesn't exist, compilation will fail
			results[i], _ = ss.SetUnlessAlreadySet(hash, &agent.MemSeries{
				Ref:    chunks.HeadSeriesRef(i + 1),
				Lset:   lset,
				LastTs: math.MinInt64,
			})
		}(i)
	}
	close(start)
	wg.Wait()

	// All results should be the same series (first one wins)
	canonical := results[0]
	for i, r := range results[1:] {
		if r != canonical {
			fmt.Printf("FAIL: Result %d is different from canonical\n", i+1)
			fmt.Printf("  Expected: %p\n", canonical)
			fmt.Printf("  Got:      %p\n", r)
			os.Exit(1)
		}
	}

	// Check that only one series is in the series map
	total := 0
	for i := 0; i < ss.Size(); i++ {
		ss.Locks()[i].RLock()
		total += len(ss.Series()[i])
		ss.Locks()[i].RUnlock()
	}

	if total != 1 {
		fmt.Printf("FAIL: Expected 1 series in map, got %d\n", total)
		os.Exit(1)
	}

	fmt.Println("PASS: SetUnlessAlreadySet is race-safe")
	os.Exit(0)
}

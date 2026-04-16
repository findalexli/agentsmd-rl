"""Test outputs for prometheus agent ST append fix.

This validates that the Start Timestamp (ST) field is correctly persisted
when appending samples to the WAL in Prometheus agent mode with the
--enable-feature=st-storage flag enabled.
"""

import subprocess
import sys
import os
import textwrap
import pytest

REPO = "/workspace/prometheus"
AGENT_DIR = f"{REPO}/tsdb/agent"


def test_agent_st_append_compiles():
    """Agent code compiles without errors (pass_to_pass)."""
    r = subprocess.run(
        ["go", "build", "./tsdb/agent"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr}"


def test_st_field_actually_persisted():
    """ST field is correctly written to WAL samples (fail_to_pass).

    This test validates the core fix: when appending samples with a non-zero
    start timestamp (ST) in agent mode with EnableSTStorage=true, the ST
    value must be persisted to the WAL via record.RefSample.ST field.

    The bug was that the ST field was omitted when creating RefSample structs,
    causing all samples to have ST=0 regardless of the input.
    """
    # Write a Go test file that specifically tests ST persistence
    test_code = textwrap.dedent('''
        package agent

        import (
            "context"
            "testing"

            "github.com/prometheus/prometheus/model/labels"
            "github.com/prometheus/prometheus/storage"
            "github.com/prometheus/prometheus/tsdb/record"
            "github.com/prometheus/prometheus/tsdb/wlog"
            "github.com/stretchr/testify/require"
        )

        func TestSTFieldPersisted(t *testing.T) {
            opts := DefaultOptions()
            opts.EnableSTStorage = true
            s := createTestAgentDB(t, nil, opts)

            app := s.AppenderV2(context.Background())

            // Create a series with specific labels
            lset := labels.FromStrings("__name__", "test_metric", "instance", "localhost")

            // Append samples with specific ST values
            expectedSTs := []int64{1000, 2000, 3000, 4000, 5000}
            for i, st := range expectedSTs {
                _, err := app.Append(0, lset, st, int64(10000+i), float64(i), nil, nil, storage.AOptions{})
                require.NoError(t, err)
            }

            require.NoError(t, app.Commit())
            require.NoError(t, s.Close())

            // Read WAL and verify ST values were persisted
            sr, err := wlog.NewSegmentsReader(s.wal.Dir())
            require.NoError(t, err)
            defer sr.Close()

            r := wlog.NewReader(sr)
            dec := record.NewDecoder(labels.NewSymbolTable(), nil)

            var gotSTs []int64
            for r.Next() {
                rec := r.Record()
                switch dec.Type(rec) {
                case record.SamplesV2:
                    var samples []record.RefSample
                    samples, err = dec.Samples(rec, samples)
                    require.NoError(t, err)
                    for _, sample := range samples {
                        gotSTs = append(gotSTs, sample.ST)
                    }
                }
            }

            // Verify we got all the ST values we wrote
            require.Equal(t, expectedSTs, gotSTs, "ST values not correctly persisted to WAL")
        }
    ''')

    test_file = f"{AGENT_DIR}/st_verify_test.go"

    # Write the test file
    with open(test_file, 'w') as f:
        f.write(test_code)

    try:
        # Run the test
        r = subprocess.run(
            ["go", "test", "-v", "-run", "TestSTFieldPersisted", "./tsdb/agent/"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )

        output = r.stdout + r.stderr

        # Check if the test failed due to ST mismatch
        if "ST values not correctly persisted" in output or r.returncode != 0:
            pytest.fail(f"ST field not persisted correctly:\n{output[-1500:]}")

    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)


def test_st_persistence_with_varying_values():
    """Different ST values are correctly persisted (fail_to_pass).

    Tests that varying ST values (not just hardcoded ones) are correctly
    captured, ensuring the fix handles dynamic values properly.
    """
    test_code = textwrap.dedent('''
        package agent

        import (
            "context"
            "testing"

            "github.com/prometheus/prometheus/model/labels"
            "github.com/prometheus/prometheus/storage"
            "github.com/prometheus/prometheus/tsdb/record"
            "github.com/prometheus/prometheus/tsdb/wlog"
            "github.com/stretchr/testify/require"
        )

        func TestSTVaryingValues(t *testing.T) {
            opts := DefaultOptions()
            opts.EnableSTStorage = true
            s := createTestAgentDB(t, nil, opts)

            app := s.AppenderV2(context.Background())
            lset := labels.FromStrings("__name__", "test_varying")

            // Use varying ST values
            expectedSTs := []int64{1234, 2234, 3234, 4234, 5234}
            for i, st := range expectedSTs {
                _, err := app.Append(0, lset, st, int64(20000+i), float64(i*10), nil, nil, storage.AOptions{})
                require.NoError(t, err)
            }

            require.NoError(t, app.Commit())
            require.NoError(t, s.Close())

            // Read WAL
            sr, err := wlog.NewSegmentsReader(s.wal.Dir())
            require.NoError(t, err)
            defer sr.Close()

            r := wlog.NewReader(sr)
            dec := record.NewDecoder(labels.NewSymbolTable(), nil)

            var gotSTs []int64
            for r.Next() {
                rec := r.Record()
                if dec.Type(rec) == record.SamplesV2 {
                    var samples []record.RefSample
                    samples, err = dec.Samples(rec, samples)
                    require.NoError(t, err)
                    for _, sample := range samples {
                        gotSTs = append(gotSTs, sample.ST)
                    }
                }
            }

            require.Equal(t, expectedSTs, gotSTs, "Varying ST values not correctly persisted")
        }
    ''')

    test_file = f"{AGENT_DIR}/st_varying_test.go"

    with open(test_file, 'w') as f:
        f.write(test_code)

    try:
        r = subprocess.run(
            ["go", "test", "-v", "-run", "TestSTVaryingValues", "./tsdb/agent/"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )

        output = r.stdout + r.stderr

        if "Varying ST values not correctly persisted" in output or r.returncode != 0:
            pytest.fail(f"Varying ST values not persisted:\n{output[-1500:]}")

    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_go_vet_tsdb_agent():
    """Go vet passes on tsdb/agent package (pass_to_pass)."""
    r = subprocess.run(
        ["go", "vet", "./tsdb/agent/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"go vet failed:\n{r.stderr[-500:]}"


def test_go_fmt_tsdb_agent():
    """Go fmt passes on tsdb/agent package (pass_to_pass)."""
    r = subprocess.run(
        ["go", "fmt", "./tsdb/agent/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"go fmt failed:\n{r.stderr[-500:]}"


def test_append_v2_unit_tests_pass():
    """Upstream AppendV2 unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["go", "test", "-v", "-run", "TestCommit_AppendV2", "./tsdb/agent/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert r.returncode == 0, f"TestCommit_AppendV2 failed:\n{r.stdout[-2000:]}\n{r.stderr[-500:]}"


def test_rollback_append_v2():
    """Rollback AppendV2 unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["go", "test", "-v", "-run", "TestRollbackAppendV2", "./tsdb/agent/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"TestRollbackAppendV2 failed:\n{r.stderr[-500:]}"


def test_wal_replay_append_v2():
    """WAL replay AppendV2 unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["go", "test", "-v", "-run", "TestWALReplay_AppendV2", "./tsdb/agent/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"TestWALReplay_AppendV2 failed:\n{r.stderr[-500:]}"


def test_st_zero_injection_append_v2():
    """ST zero injection AppendV2 unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["go", "test", "-v", "-run", "TestDB_EnableSTZeroInjection_AppendV2", "./tsdb/agent/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"TestDB_EnableSTZeroInjection_AppendV2 failed:\n{r.stderr[-500:]}"


def test_invalid_series_append_v2():
    """Invalid series handling in AppendV2 works (pass_to_pass)."""
    r = subprocess.run(
        ["go", "test", "-v", "-run", "TestDB_InvalidSeries_AppendV2", "./tsdb/agent/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Invalid series test failed:\n{r.stderr}"


def test_all_agent_code_compiles():
    """Verify that all agent-related code compiles (pass_to_pass)."""
    r = subprocess.run(
        ["go", "build", "./tsdb/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert r.returncode == 0, f"TSDB build failed:\n{r.stderr}"

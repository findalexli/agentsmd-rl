"""Test outputs for moby-builder-progress-refactor task."""

import subprocess
import re
import ast
import os

REPO = "/workspace/moby"

# Files that had the oneOffProgress function
PULL_GO = f"{REPO}/daemon/internal/builder-next/adapters/containerimage/pull.go"
EXPORT_GO = f"{REPO}/daemon/internal/builder-next/exporter/mobyexporter/export.go"
WRITER_GO = f"{REPO}/daemon/internal/builder-next/exporter/mobyexporter/writer.go"
WORKER_GO = f"{REPO}/daemon/internal/builder-next/worker/worker.go"


def test_compilation():
    """Project compiles successfully (pass-to-pass)."""
    r = subprocess.run(
        ["go", "build", "./daemon/internal/builder-next/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr}"


def test_go_vet():
    """Go vet passes on builder-next packages (pass-to-pass)."""
    r = subprocess.run(
        ["go", "vet", "./daemon/internal/builder-next/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert r.returncode == 0, f"go vet failed:\n{r.stderr}"


def test_unit_worker():
    """Unit tests for worker package pass (pass-to-pass)."""
    r = subprocess.run(
        ["go", "test", "./daemon/internal/builder-next/worker/...", "-v"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert r.returncode == 0, f"Worker unit tests failed:\n{r.stderr[-500:]}"


def test_unit_mobyexporter():
    """Unit tests for mobyexporter package pass (pass-to-pass)."""
    r = subprocess.run(
        ["go", "test", "./daemon/internal/builder-next/exporter/mobyexporter/...", "-v"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert r.returncode == 0, f"Mobyexporter unit tests failed:\n{r.stderr[-500:]}"


def test_unit_containerimage():
    """Unit tests for containerimage adapter pass (pass-to-pass)."""
    r = subprocess.run(
        ["go", "test", "./daemon/internal/builder-next/adapters/containerimage/...", "-v"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert r.returncode == 0, f"Containerimage adapter unit tests failed:\n{r.stderr[-500:]}"


def test_pull_go_uses_progress_oneoff():
    """pull.go uses progress.OneOff instead of local oneOffProgress (fail-to-pass)."""
    with open(PULL_GO, 'r') as f:
        content = f.read()

    # Should use progress.OneOff
    assert 'progress.OneOff(ctx, "resolve "+p.src.Reference.String())' in content, \
        "pull.go should use progress.OneOff for resolve progress"

    # Should NOT have the local oneOffProgress function definition
    assert 'func oneOffProgress(ctx context.Context, id string) func(err error) error {' not in content, \
        "pull.go should not have local oneOffProgress function definition"

    # Should have the progress import
    assert '"github.com/moby/buildkit/util/progress"' in content, \
        "pull.go should import github.com/moby/buildkit/util/progress"


def test_export_go_uses_progress_oneoff():
    """export.go uses progress.OneOff instead of local oneOffProgress (fail-to-pass)."""
    with open(EXPORT_GO, 'r') as f:
        content = f.read()

    # Should use progress.OneOff for layers
    assert 'progress.OneOff(ctx, "exporting layers")' in content, \
        "export.go should use progress.OneOff for layers"

    # Should use progress.OneOff for writing image
    assert 'progress.OneOff(ctx, fmt.Sprintf("writing image %s", configDigest))' in content, \
        "export.go should use progress.OneOff for writing image"

    # Should use progress.OneOff for naming
    assert 'progress.OneOff(ctx, "naming to "+targetName.String())' in content, \
        "export.go should use progress.OneOff for naming"

    # Should have the progress import
    assert '"github.com/moby/buildkit/util/progress"' in content, \
        "export.go should import github.com/moby/buildkit/util/progress"


def test_writer_go_no_local_oneoffprogress():
    """writer.go has removed local oneOffProgress function (fail-to-pass)."""
    with open(WRITER_GO, 'r') as f:
        content = f.read()

    # Should NOT have the local oneOffProgress function definition
    assert 'func oneOffProgress(ctx context.Context, id string) func(err error) error {' not in content, \
        "writer.go should not have local oneOffProgress function definition"

    # Should NOT have the progress import (it's not needed in this file anymore)
    lines = content.split('\n')
    import_section = False
    in_import_block = False
    progress_import_found = False

    for line in lines:
        if 'import (' in line:
            in_import_block = True
        elif in_import_block and ')' in line:
            in_import_block = False
        elif in_import_block and '"github.com/moby/buildkit/util/progress"' in line:
            progress_import_found = True

    assert not progress_import_found, \
        "writer.go should not import github.com/moby/buildkit/util/progress (not needed)"


def test_worker_go_uses_progress_oneoff():
    """worker.go uses progress.OneOff instead of local oneOffProgress (fail-to-pass)."""
    with open(WORKER_GO, 'r') as f:
        content = f.read()

    # Should use progress.OneOff
    assert 'progress.OneOff(ld.pctx, fmt.Sprintf("pulling %s", ld.desc.Digest))' in content, \
        "worker.go should use progress.OneOff for pulling"

    # Should NOT have the local oneOffProgress function definition
    assert 'func oneOffProgress(ctx context.Context, id string) func(err error) error {' not in content, \
        "worker.go should not have local oneOffProgress function definition"

    # Should have the progress import
    assert '"github.com/moby/buildkit/util/progress"' in content, \
        "worker.go should import github.com/moby/buildkit/util/progress"


def test_no_duplicate_oneoffprogress_anywhere():
    """No local oneOffProgress function exists in any of the modified files (fail-to-pass)."""
    files = [PULL_GO, EXPORT_GO, WRITER_GO, WORKER_GO]

    for filepath in files:
        with open(filepath, 'r') as f:
            content = f.read()

        assert 'func oneOffProgress(ctx context.Context, id string) func(err error) error {' not in content, \
            f"{filepath} should not have local oneOffProgress function definition"


def test_correct_number_of_call_sites():
    """All call sites are correctly updated to use progress.OneOff (fail-to-pass)."""
    # Count all progress.OneOff calls in the modified files
    total_calls = 0
    files = [PULL_GO, EXPORT_GO, WORKER_GO]

    for filepath in files:
        with open(filepath, 'r') as f:
            content = f.read()
        calls = content.count('progress.OneOff(')
        total_calls += calls

    # Expected: 1 in pull.go + 3 in export.go + 1 in worker.go = 5 total
    assert total_calls == 5, \
        f"Expected 5 progress.OneOff calls, found {total_calls}"

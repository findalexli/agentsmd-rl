# Fix WorkspaceManager `_current_workspaces` size

## Problem

The `WorkspaceManager` class in `vllm/v1/worker/workspace.py` always allocates a fixed-size internal workspace list regardless of the `num_ubatches` parameter passed to its constructor. This means:

- When `num_ubatches` defaults to 1, the workspace list is oversized (wastes memory).
- When `num_ubatches` is greater than 2, accessing higher-indexed ubatch slots causes an `IndexError` at runtime.

The bug manifests when using DBO (Dual Batch Overlap) execution with a non-default number of micro-batches. The `_ensure_workspace_size` method iterates over `range(self._num_ubatches)` and indexes into `_current_workspaces`, which fails if the list is the wrong length.

## Expected Behavior

The `_current_workspaces` list should have exactly `num_ubatches` entries — one per micro-batch slot. When `num_ubatches` is `None` (the default), it should be treated as 1.

## Files to Look At

- `vllm/v1/worker/workspace.py` — `WorkspaceManager.__init__` initializes the workspace list

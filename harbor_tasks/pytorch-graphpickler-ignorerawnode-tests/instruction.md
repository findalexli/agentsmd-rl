# Missing test coverage for `ignore_raw_node` option in `GraphPickler.Options`

## Context

The `GraphPickler` class in `torch/fx/_graph_pickler.py` is used to serialize
`torch.fx.GraphModule` objects. A recent change added an `ignore_raw_node`
option to `GraphPickler.Options` that controls what happens when a raw
`torch.fx.Node` object is encountered in node metadata during pickling:

- **Default behavior** (`ignore_raw_node=False`): an `AssertionError` is
  raised with the message `"Unexpected raw Node during pickling"`.
- **Opt-in behavior** (`ignore_raw_node=True`): the raw `Node` is silently
  replaced with `None` during serialization, and it round-trips as `None`
  after deserialization.

## Problem

There are no unit tests covering either of these behaviors. The existing test
file `test/fx/test_graph_pickler.py` already tests many `GraphPickler`
features but has no tests that exercise the `ignore_raw_node` option.

## What needs to happen

Add test coverage in `test/fx/test_graph_pickler.py` for the
`ignore_raw_node` option. The tests should verify:

1. That pickling a `GraphModule` whose `node.meta` contains a raw
   `torch.fx.Node` reference raises `AssertionError` by default.
2. That with `Options(ignore_raw_node=True)`, pickling succeeds and the raw
   node reference deserializes as `None` after a round-trip.

The test should construct a simple traced graph module, inject a raw `Node`
reference into the metadata of one of its nodes, and exercise the
`GraphPickler.dumps()` / `GraphPickler.loads()` round-trip.

## Relevant files

- `torch/fx/_graph_pickler.py` — `GraphPickler`, `Options` class
- `test/fx/test_graph_pickler.py` — existing test suite

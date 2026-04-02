# Bug: SPLADE Pooler Unit Test Fails with AttributeError

## Summary

The unit test `test_splade_pooler_matches_reference_formula` in `tests/models/language/pooling/test_splade_sparse_pooler.py` is broken. Running it produces an `AttributeError` at runtime.

## Details

The test creates a lightweight mock of pooling metadata using `types.SimpleNamespace` to avoid heavy dependencies. However, a recent change to `SPLADESparsePooler.forward()` in `vllm/model_executor/models/bert.py` now calls a method on the pooling metadata object that the `SimpleNamespace` mock does not implement.

Look at what `SPLADESparsePooler.forward()` expects from the `pooling_metadata` parameter — specifically which methods it calls — and compare that to what the test's mock object provides. The test's metadata mock needs to be updated to satisfy the interface that the pooler's `forward()` method now requires.

## Relevant files

- `tests/models/language/pooling/test_splade_sparse_pooler.py` — the broken test
- `vllm/model_executor/models/bert.py` — `SPLADESparsePooler.forward()` implementation
- `vllm/v1/pool/metadata.py` — pooling metadata dataclass and its methods

## Reproduction

```bash
pytest tests/models/language/pooling/test_splade_sparse_pooler.py -xvs
```

This should fail with an `AttributeError` on the mock metadata object.

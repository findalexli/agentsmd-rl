# CreateCatalogItem returns plain PCollection instead of tagged outputs

## Problem

The `CreateCatalogItem` PTransform in the Recommendations AI connector claims to return separate output channels for successfully created catalog items and failures, but it actually returns a plain `PCollection`. When a user tries to access `result.created_catalog_items` or `result.failed_catalog_items` after applying the transform, they get an `AttributeError`.

The underlying `DoFn` already yields `TaggedOutput` for failures, but the `expand()` method does not wire up the tagged output routing. This means failed items are silently mixed into the main output (or dropped) instead of being properly separated.

## Expected Behavior

`CreateCatalogItem` should return an object with:
- `created_catalog_items` — a PCollection of successfully created items
- `failed_catalog_items` — a PCollection of items that failed to create

This matches the Dead Letter Queue pattern described in the Beam concepts documentation, and is consistent with how `_CreateCatalogItemFn.process()` already yields tagged outputs for failures.

## Files to Look At

- `sdks/python/apache_beam/ml/gcp/recommendations_ai.py` — the `CreateCatalogItem` PTransform and its `expand()` method

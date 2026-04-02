# Bug: interaction_id lost during serialization/deserialization of interactions

## Summary

When interactions are exported from the data proxy via the `/export_trajectories`
endpoint and then deserialized on the receiving side, the `interaction_id` is silently
dropped. This means downstream consumers cannot correlate deserialized interactions back
to their original session IDs.

## Where to look

- **`areal/experimental/openai/types.py`** — The `InteractionWithTokenLogpReward`
  dataclass has an `interaction_id` property that only reads from `completion.id` or
  `response.id`. But when interactions are reconstructed from serialized data (without
  a full `ChatCompletion` or `Response` object), there is no fallback — the property
  just returns `None`.

- **`areal/experimental/openai/proxy/server.py`** — The `serialize_interactions` function
  correctly includes `interaction_id` in the serialized payload. However,
  `deserialize_interactions` creates bare `InteractionWithTokenLogpReward` instances and
  never restores the `interaction_id` from the payload. It also has overly complex
  dual-path logic (shard metadata vs legacy list format) when the codebase already
  provides `serialize_value`/`deserialize_value` in `areal.infra.rpc.serialization` that
  handle tensor serialization generically.

- **`areal/experimental/inference_service/data_proxy/app.py`** — The `export_trajectories`
  endpoint currently passes `node_addr` through `serialize_interactions` for RTensor shard
  management. The `RTensor.remotize()` step should happen before serialization, at the
  data proxy layer, rather than being embedded inside the serialization helper.

## Expected behavior

1. After a serialize → deserialize roundtrip, `interaction.interaction_id` should return
   the original ID string, not `None`.
2. The serialization should use the existing `serialize_value`/`deserialize_value` from
   `areal.infra.rpc.serialization` instead of manually managing shard metadata vs legacy
   tensor list formats.
3. `RTensor.remotize()` should be called at the data proxy layer before serialization,
   keeping transport concerns out of the serialization helper.

## Reproduction

Create a bare `InteractionWithTokenLogpReward` (no completion or response), populate its
tensor cache and reward, serialize it, then deserialize — the `interaction_id` will be
`None` even though it was present in the serialized data.

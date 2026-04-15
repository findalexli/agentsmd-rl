# Bug: interaction_id lost during serialization/deserialization of interactions

## Summary

When interactions are exported from the data proxy via the `/export_trajectories`
endpoint and then deserialized on the receiving side, the `interaction_id` is silently
lost. This means downstream consumers cannot correlate deserialized interactions back
to their original session IDs.

## Expected behavior

1. **Roundtrip fidelity**: After a serialize → deserialize cycle, `interaction.interaction_id`
   should return the original ID string, not `None`.

2. **Tensor preservation**: Tensor data stored in the interaction's internal cache must
   survive the roundtrip intact (values must match within floating-point tolerance).

3. **Setter/getter on bare objects**: On `InteractionWithTokenLogpReward` objects that have
   neither `completion` nor `response` set, it must be possible to set `interaction_id`
   to any value (including empty string) and read it back. Each instance maintains
   independent state.

4. **Setter rejects completion/response**: On `InteractionWithTokenLogpReward` objects that
   have either `completion` or `response` set, attempting to set `interaction_id` must
   raise a `ValueError` whose message contains "complet" or "respon" (case-insensitive).

5. **Serialization utility**: The code should use the existing `serialize_value` /
   `deserialize_value` utility from `areal.infra.rpc.serialization` for tensor serialization
   rather than manual list conversion.

## Reproduction

Create a bare `InteractionWithTokenLogpReward` (no completion or response), populate its
tensor cache and reward, serialize it, then deserialize — the `interaction_id` will be
`None` even though it was present in the serialized data.
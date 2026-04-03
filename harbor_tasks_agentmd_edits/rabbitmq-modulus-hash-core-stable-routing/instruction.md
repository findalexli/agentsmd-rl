# Move `x-modulus-hash` exchange type to core and ensure stable routing

## Problem

The `x-modulus-hash` exchange type currently lives in the `rabbitmq_sharding` plugin (`deps/rabbitmq_sharding/src/rabbit_sharding_exchange_type_modulus_hash.erl`), but this exchange type is useful on its own without the sharding plugin. Users who want simple modulus-hash routing must enable the entire sharding plugin just for this one exchange type.

Additionally, the current implementation does not guarantee stable routing across node restarts. With Khepri (which uses bag ETS projection tables instead of Mnesia's ordered_set), the order of matched destinations can vary after a restart. This means a message with the same routing key may be routed to a different queue after a node restart, breaking use cases that depend on message ordering (e.g., Single Active Consumer patterns).

## Expected Behavior

1. The `x-modulus-hash` exchange type should be available as a built-in exchange in core RabbitMQ (`deps/rabbit/`), without requiring the sharding plugin
2. Routing must be stable: messages with the same routing key must always be routed to the same destination queue, as long as the set of bound queues does not change — even across node restarts
3. The sharding plugin should no longer register its own `x-modulus-hash` exchange type (to avoid duplicate registration conflicts)
4. The sharding plugin's documentation should be updated to reflect that `x-modulus-hash` is now a built-in exchange type with a stable routing guarantee

## Files to Look At

- `deps/rabbitmq_sharding/src/rabbit_sharding_exchange_type_modulus_hash.erl` — current exchange implementation in the sharding plugin
- `deps/rabbit/src/` — where core exchange types live (e.g., `rabbit_exchange_type_direct.erl`, `rabbit_exchange_type_fanout.erl`)
- `deps/rabbitmq_sharding/README.md` — plugin documentation that references the `x-modulus-hash` exchange type

## Hints

- Look at how existing core exchange types are structured (boot steps, behaviour callbacks)
- The fix for stable routing involves sorting the list of matched destinations before selecting one
- After moving the module, make sure to update the sharding plugin README to reflect that `x-modulus-hash` is now built-in and document the stable routing guarantee

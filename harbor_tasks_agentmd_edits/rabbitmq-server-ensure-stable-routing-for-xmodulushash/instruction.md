# Move x-modulus-hash exchange to core and ensure stable routing

## Problem

The `x-modulus-hash` exchange type currently lives in the `rabbitmq_sharding` plugin (`deps/rabbitmq_sharding/src/rabbit_sharding_exchange_type_modulus_hash.erl`), but it is useful on its own without the sharding plugin. Additionally, the current implementation does not guarantee stable routing: after a node restart, messages with the same routing key may be routed to a different destination queue than before the restart. This is because the destination list order is not deterministic.

## Expected Behavior

1. The `x-modulus-hash` exchange type should be moved to core RabbitMQ (`deps/rabbit/src/`) so it is available without enabling the sharding plugin
2. The routing must be stable: given the same set of bound queues, messages with the same routing key must always route to the same destination queue, even across node restarts
3. The sharding plugin's README (`deps/rabbitmq_sharding/README.md`) should be updated to reflect that this exchange type is now built-in to core RabbitMQ and to document the stable routing guarantee

## Files to Look At

- `deps/rabbitmq_sharding/src/rabbit_sharding_exchange_type_modulus_hash.erl` — the current exchange type implementation in the sharding plugin
- `deps/rabbit/src/` — where the exchange type should live as a core module
- `deps/rabbitmq_sharding/README.md` — documents the sharding plugin, including the exchange type
- `deps/rabbit/Makefile` — parallel CT test set definitions

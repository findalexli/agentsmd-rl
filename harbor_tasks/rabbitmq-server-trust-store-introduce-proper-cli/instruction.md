# Trust store: introduce proper CLI commands

## Problem

The `rabbitmq_trust_store` plugin currently has no proper CLI commands for its key operations. Users who want to list loaded trust store certificates or manually trigger a refresh must resort to `rabbitmqctl eval` with raw Erlang expressions:

```
rabbitmqctl eval 'io:format(rabbit_trust_store:list()).'
rabbitmqctl eval 'rabbit_trust_store:refresh().'
```

This is inconvenient, undiscoverable, and inconsistent with how other RabbitMQ plugin operations are exposed via `rabbitmqctl`.

## Expected Behavior

The trust store plugin should provide proper CLI commands:
- A command to list certificates currently loaded in the trust store, returning structured tabular output (name, serial, subject, issuer, validity)
- A command to trigger a manual refresh of the trust store certificates

These commands should follow the same patterns as other `rabbitmqctl` commands in the RabbitMQ codebase (implementing `CommandBehaviour`, providing `usage`, `description`, `run`, etc.).

After implementing the code changes, update the trust store plugin's documentation (`deps/rabbitmq_trust_store/README.md`) to reflect the new CLI commands, replacing the old `rabbitmqctl eval` instructions.

## Files to Look At

- `deps/rabbitmq_trust_store/src/rabbit_trust_store.erl` — the core trust store module; currently exports `list/0` which returns a formatted string, but a structured data function is needed for the table formatter
- `deps/rabbitmq_trust_store/src/` — where new CLI command modules should be added
- `deps/rabbitmq_trust_store/README.md` — documents how to use the trust store, including listing and refreshing certificates
- `deps/rabbitmq_cli/` — contains existing CLI commands for reference on the `CommandBehaviour` pattern

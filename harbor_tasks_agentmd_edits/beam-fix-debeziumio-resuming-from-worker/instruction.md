# Fix DebeziumIO Worker Restart Crash Loop

## Problem

When a Dataflow worker running a DebeziumIO pipeline crashes and restarts, the connector enters a crash loop. The restarted worker throws a `NullPointerException` because `KafkaSourceConsumerFn.startTime` is a static field that doesn't get re-initialized when a new DoFn instance is created after restart.

There is also a secondary bug: the poll loop inside `KafkaSourceConsumerFn.process()` never exits when the database keeps returning records, because it re-polls at the end of each iteration with no timeout boundary.

Additionally, the `DebeziumIO` javadoc still contains a warning that the connector is "currently experimental" and "does not preserve the offset on a worker crash or restart" — this should be cleaned up once the fix is in place.

## Expected Behavior

1. After a worker restart, the DebeziumIO connector should resume consuming from its last committed offset without crashing.
2. The poll loop should be bounded by a configurable timeout so it exits and yields control back to the framework.
3. The polling timeout should be configurable through the `DebeziumIO.Read` builder API.
4. The stale "experimental" warning in `DebeziumIO` javadoc should be removed.
5. After fixing the code, update the relevant documentation to reflect the API changes — the `README.md` in the debezium module documents internal constructor signatures that will no longer be accurate after the refactor.

## Files to Look At

- `sdks/java/io/debezium/src/main/java/org/apache/beam/io/debezium/KafkaSourceConsumerFn.java` — the splittable DoFn that manages CDC consumption; contains the `startTime` field and the poll loop
- `sdks/java/io/debezium/src/main/java/org/apache/beam/io/debezium/DebeziumIO.java` — the public API surface (`Read` transform builder); contains the experimental warning in javadoc
- `sdks/java/io/debezium/src/README.md` — documents KafkaSourceConsumerFn initialization and constructor signatures

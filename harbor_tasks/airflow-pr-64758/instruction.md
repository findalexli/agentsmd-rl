# Fix Timezone Conversion Overflow in Example DAGs

When running Airflow with a non-UTC default timezone (e.g., `Asia/Shanghai`), two example DAGs fail to load with an `OverflowError`:

```
OverflowError: date value out of range
```

The affected DAGs are:
- `airflow-core/src/airflow/example_dags/example_inlet_event_extra.py`
- `airflow-core/src/airflow/example_dags/example_outlet_event_extra.py`

The error occurs during DAG parsing when Airflow tries to convert the `start_date` to UTC. The traceback shows the issue happens in the timezone conversion logic.

Users who set `AIRFLOW__CORE__DEFAULT_TIMEZONE` to any timezone with a positive UTC offset (like `Asia/Shanghai`, `Asia/Tokyo`, or `Australia/Sydney`) cannot load these example DAGs.

Fix the DAG files so they work correctly regardless of the configured default timezone.

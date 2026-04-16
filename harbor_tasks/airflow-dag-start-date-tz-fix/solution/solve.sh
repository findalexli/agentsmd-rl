#!/bin/bash
set -e

cd /workspace/airflow

INLET_FILE="airflow-core/src/airflow/example_dags/example_inlet_event_extra.py"
OUTLET_FILE="airflow-core/src/airflow/example_dags/example_outlet_event_extra.py"

# Idempotency check: if fix already applied, exit early
if grep -q 'start_date=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)' "$INLET_FILE"; then
    echo "Fix already applied, skipping."
    exit 0
fi

# Apply the fix using sed
# Replace all occurrences of 'start_date=datetime.datetime.min' with the fixed version
sed -i 's/start_date=datetime\.datetime\.min/start_date=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)/g' "$INLET_FILE"
sed -i 's/start_date=datetime\.datetime\.min/start_date=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)/g' "$OUTLET_FILE"

echo "Gold patch applied successfully."

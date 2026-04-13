#!/bin/bash
set -e

cd /workspace/dagster

# Check if already patched (idempotency)
if grep -q "DbtEventIterator\[DbtDagsterEventType\]" python_modules/libraries/dagster-dbt/dagster_dbt/components/dbt_project/component.py 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Fix component.py - remove Iterator from collections.abc import and add new imports
sed -i 's/from collections.abc import Iterator, Mapping/from collections.abc import Mapping/' python_modules/libraries/dagster-dbt/dagster_dbt/components/dbt_project/component.py

# Fix component.py - add import for DbtEventIterator and DbtDagsterEventType
sed -i 's/from dagster_dbt.components.dbt_project.scaffolder import DbtProjectComponentScaffolder/from dagster_dbt.components.dbt_project.scaffolder import DbtProjectComponentScaffolder\nfrom dagster_dbt.core.dbt_event_iterator import DbtDagsterEventType, DbtEventIterator/' python_modules/libraries/dagster-dbt/dagster_dbt/components/dbt_project/component.py

# Fix component.py - change return type from Iterator to DbtEventIterator[DbtDagsterEventType]
sed -i 's/) -> Iterator:$/) -> DbtEventIterator[DbtDagsterEventType]:/' python_modules/libraries/dagster-dbt/dagster_dbt/components/dbt_project/component.py

# Fix dbt_event_iterator.py - fetch_row_counts return type
sed -i 's/) -> "DbtEventIterator\[Output | AssetMaterialization | AssetCheckResult | AssetObservation | AssetCheckEvaluation\]":/) -> "DbtEventIterator[DbtDagsterEventType]":/' python_modules/libraries/dagster-dbt/dagster_dbt/core/dbt_event_iterator.py

# Fix dbt_event_iterator.py - fetch_column_metadata return type
sed -i 's/) -> "DbtEventIterator\[Output | AssetMaterialization | AssetCheckResult | AssetObservation | AssetCheckEvaluation\]":/) -> "DbtEventIterator[DbtDagsterEventType]":/' python_modules/libraries/dagster-dbt/dagster_dbt/core/dbt_event_iterator.py

# Fix dbt_event_iterator.py - with_insights return type (note different order in original)
sed -i 's/) -> "DbtEventIterator\[Output | AssetMaterialization | AssetObservation | AssetCheckResult | AssetCheckEvaluation\]":/) -> "DbtEventIterator[DbtDagsterEventType]":/' python_modules/libraries/dagster-dbt/dagster_dbt/core/dbt_event_iterator.py

# Install ruff and format the modified files to ensure compliance
pip install ruff==0.15.0 -q
ruff format python_modules/libraries/dagster-dbt/dagster_dbt/components/dbt_project/component.py
ruff format python_modules/libraries/dagster-dbt/dagster_dbt/core/dbt_event_iterator.py

echo "Patch applied successfully"

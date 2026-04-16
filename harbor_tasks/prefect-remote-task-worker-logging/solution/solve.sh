#!/bin/bash
set -e

cd /workspace/prefect

# Add ensure_logging_setup function to configuration.py after load_logging_config function
cat >> /tmp/ensure_logging_setup.py << 'EOF'

def ensure_logging_setup() -> None:
    """
    Ensure Prefect logging is configured in this process, calling
    `setup_logging` only if it has not already been called.

    Use this in remote execution environments (e.g. Dask/Ray workers) where
    the normal SDK entry point (`import prefect`) may not have triggered
    logging configuration.
    """
    if not PROCESS_LOGGING_CONFIG:
        setup_logging()


EOF

# Find the line number where we need to insert (after load_logging_config function ends)
# We'll insert after line 65 (after load_logging_config function)
head -n 65 src/prefect/logging/configuration.py > /tmp/config_part1.py
tail -n +66 src/prefect/logging/configuration.py > /tmp/config_part2.py

cat /tmp/config_part1.py /tmp/ensure_logging_setup.py /tmp/config_part2.py > src/prefect/logging/configuration.py

# Now update context.py to import and use ensure_logging_setup
# First, add the import after MissingContextError import
sed -i 's/from prefect.exceptions import MissingContextError/from prefect.exceptions import MissingContextError\nfrom prefect.logging.configuration import ensure_logging_setup/' src/prefect/context.py

# Then, add the call in hydrated_context when serialized_context is present
# Find the line with "if serialized_context:" and add ensure_logging_setup() call after it
sed -i 's/        if serialized_context:/        if serialized_context:\n            ensure_logging_setup()/' src/prefect/context.py

# Run ruff format to fix any formatting issues
ruff format src/prefect/logging/configuration.py src/prefect/context.py

# Verify the patch was applied
export PYTHONPATH="/workspace/prefect/src:${PYTHONPATH}"
python -c "from prefect.logging.configuration import ensure_logging_setup; print('ensure_logging_setup imported successfully')"
python -c "import sys; sys.path.insert(0, '/workspace/prefect/src'); from prefect.context import hydrated_context; print('context.py imports work correctly')"

echo "Patch applied successfully"

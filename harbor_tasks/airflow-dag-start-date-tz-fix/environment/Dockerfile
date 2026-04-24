FROM python:3.12-slim

# Install git, patch, and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone airflow repo at base commit (shallow clone for speed)
# Using filter=blob:none to get a partial clone for faster checkout
RUN git clone --filter=blob:none --no-checkout https://github.com/apache/airflow.git /workspace/airflow && \
    cd /workspace/airflow && \
    git sparse-checkout init --cone && \
    git sparse-checkout set airflow-core/src/airflow/example_dags && \
    git checkout 5baee8a5a58e56afa7788c193753ad3cf804aa58

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# The PR only modifies two example DAG files - no additional deps needed
# The test will directly import and check the DAG definitions

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff

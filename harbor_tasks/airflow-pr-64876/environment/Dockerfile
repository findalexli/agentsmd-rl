FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    sqlite3 \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Create workspace and logs directories
WORKDIR /workspace
RUN mkdir -p /logs/verifier

# Clone the repository at the base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout 06101dc5daa2f4a3e4b6020b6e2f305566816e8a

# Install minimal dependencies needed for testing the migration
WORKDIR /workspace/airflow
RUN pip install --no-cache-dir \
    alembic>=1.13.0 \
    sqlalchemy>=2.0.0 \
    pytest>=8.0.0

# Set environment variables
ENV PYTHONPATH=/workspace/airflow/airflow-core/src
ENV AIRFLOW_HOME=/workspace/airflow_home
RUN mkdir -p $AIRFLOW_HOME

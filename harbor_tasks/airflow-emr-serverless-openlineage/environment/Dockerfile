# Apache Airflow EMR Serverless OpenLineage Task
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for Python package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Clone the Airflow repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow && \
    cd airflow && \
    git checkout d53a7ad5c7e6feaa930bd35c9142b12cd61f5394

WORKDIR /workspace/airflow

# Sync dependencies for the providers we need
RUN uv sync --project providers/amazon && \
    uv sync --project providers/openlineage && \
    uv sync --project providers/common/compat

# Create logs directory for verifier
RUN mkdir -p /logs/verifier \RUN mkdir -p /logs/verifier\RUN mkdir -p /logs/verifier echo "__version__ = \"3.2.0\"" >> /workspace/airflow/providers/amazon/src/airflow/__init__.py \RUN mkdir -p /logs/verifier\RUN mkdir -p /logs/verifier echo "__version__ = \"3.2.0\"" >> /workspace/airflow/providers/openlineage/src/airflow/__init__.py \RUN mkdir -p /logs/verifier\RUN mkdir -p /logs/verifier echo "__version__ = \"3.2.0\"" >> /workspace/airflow/providers/common/compat/src/airflow/__init__.py

# Set working directory
WORKDIR /workspace/airflow

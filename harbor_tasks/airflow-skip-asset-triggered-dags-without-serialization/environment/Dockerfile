FROM python:3.12-slim

# Install git, curl, build dependencies, and Kerberos libraries
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    libpq-dev \
    libkrb5-dev \
    krb5-config \
    libgssapi-krb5-2 \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Clone Airflow at the base commit
WORKDIR /workspace
ARG BASE_COMMIT=97deef5f615b17f618a2bf4c2e9e0f8c3ec15cde
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow && \
    cd airflow && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/airflow

# Sync dependencies for airflow-core project
RUN uv sync --project airflow-core

# Create verifier logs directory
RUN mkdir -p /logs/verifier

# Set environment for tests
ENV PYTHONPATH="/workspace/airflow/airflow-core/src:/workspace/airflow/devel-common/src:/workspace/airflow/task-sdk/src:/workspace/airflow/shared:$PYTHONPATH"

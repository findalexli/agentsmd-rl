# SPDX-License-Identifier: Apache-2.0
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Clone repository at base commit (before the fix)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout d53a7ad5c7e6feaa930bd35c9142b12cd61f5394

WORKDIR /workspace/airflow

# Install uv for dependency management
RUN pip install --no-cache-dir uv

# Install dependencies - only what's needed to test the spark.py utility module
RUN pip install --no-cache-dir \
    pytest \
    pytest-mock \
    openlineage-python>=1.41.0 \
    openlineage-integration-common>=1.41.0 \
    attrs>=22.2 \
    typing-extensions

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace/airflow

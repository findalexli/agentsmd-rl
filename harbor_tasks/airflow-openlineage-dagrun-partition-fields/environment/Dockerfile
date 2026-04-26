FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Clone the repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=40902de7e7d31225410db85e3707aaf494ab5e90
RUN git init /workspace/airflow && \
    cd /workspace/airflow && \
    git remote add origin https://github.com/apache/airflow.git && \
    git fetch --depth=1 origin 40902de7e7d31225410db85e3707aaf494ab5e90 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/airflow

# Sync the providers/openlineage project dependencies
RUN uv sync --project providers/openlineage

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory for the task
WORKDIR /workspace/airflow

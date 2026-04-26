FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone the airflow repo at base commit
WORKDIR /workspace
RUN git init /workspace/airflow && \
    cd /workspace/airflow && \
    git remote add origin https://github.com/apache/airflow.git && \
    git fetch --depth=1 origin b5dae4e72df868004b53006bb995256ef88d9c0b && \
    git checkout FETCH_HEAD

# Install the git provider dependencies
WORKDIR /workspace/airflow/providers/git
RUN pip install -e .

# Install pytest for test runner
RUN pip install pytest

# Ensure logs directory exists
RUN mkdir -p /logs/verifier

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages flake8 ruff 2>/dev/null || pip install --no-cache-dir flake8 ruff

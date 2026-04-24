FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone the repository at the base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout b5dae4e72df868004b53006bb995256ef88d9c0b

# Install pytest and GitPython (direct dependency of the git hook)
RUN pip install --no-cache-dir pytest pytest-mock GitPython

# Create log directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff

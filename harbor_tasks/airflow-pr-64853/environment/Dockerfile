# Dockerfile for airflow-gantt-date-parsing task
FROM node:22-slim

# Install git, python3 (for pytest harness), patch, and pnpm
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    python3-venv \
    ca-certificates \
    patch \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m pip install --break-system-packages pytest

# Install pnpm
RUN npm install -g pnpm@9

# Create workspace
WORKDIR /workspace

# Clone airflow repo at base commit (sparse checkout for UI only)
RUN git clone --filter=blob:none --no-checkout https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git sparse-checkout init --cone \
    && git sparse-checkout set airflow-core/src/airflow/ui \
    && git checkout 64ac0919840381ce708c5ce4bddd96f9b20ef4aa

# Install UI dependencies
WORKDIR /workspace/airflow/airflow-core/src/airflow/ui
RUN pnpm install --frozen-lockfile

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow

# Dockerfile for airflow-dagversion-select-filter benchmark task
FROM node:22-slim

# Install git and python3 (needed by pytest runner)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    python3-venv \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /workspace

# Clone the repo at base commit with blob filter for efficiency
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout 84010007d2e5553e2212ce4c63d4df063b8ebf4b

# Install UI dependencies
WORKDIR /workspace/airflow/airflow-core/src/airflow/ui
RUN pnpm install --frozen-lockfile

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow

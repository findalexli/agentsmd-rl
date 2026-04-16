# Dockerfile for airflow-dag-version-select-filter task
FROM node:22-slim

# Install git, python3 (for pytest runner), and other essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    python3-venv \
    ca-certificates \
    patch \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install pytest --break-system-packages

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Clone the airflow repository at the base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout fd1962fa027c8b937fc5d4b8ed0d43544bfa3d94

# Install UI dependencies
WORKDIR /workspace/airflow/airflow-core/src/airflow/ui
RUN pnpm install --frozen-lockfile

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow

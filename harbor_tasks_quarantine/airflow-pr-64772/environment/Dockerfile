# Dockerfile for airflow-external-link-security task
FROM node:22-slim

# Install git, python3 (needed by pytest runner), and other essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    python3-venv \
    ca-certificates \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone the repository at the base commit (before the fix)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout b2b3ce2607088ec5c11356ac5e271cb80fd8b6bb

# Install pnpm
RUN npm install -g pnpm

# Install UI dependencies
WORKDIR /workspace/airflow/airflow-core/src/airflow/ui
RUN pnpm install --frozen-lockfile

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow

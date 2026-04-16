# SPDX-License-Identifier: Apache-2.0
FROM node:22-slim

# Install Python (needed for pytest test harness), git, and patch
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv git ca-certificates patch \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Clone the repository with sparse checkout for UI only
WORKDIR /workspace
RUN git clone --filter=blob:none --sparse https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git sparse-checkout set airflow-core/src/airflow/ui contributing-docs \
    && git checkout bdc2747cc41b18af1fb42ab80159556a93d79ff3

# Install UI dependencies
WORKDIR /workspace/airflow/airflow-core/src/airflow/ui
RUN pnpm install --frozen-lockfile

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow

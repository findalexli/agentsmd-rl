# syntax=docker/dockerfile:1
FROM node:22-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest for the test runner
RUN pip3 install pytest --break-system-packages

# Install pnpm
RUN npm install -g pnpm

# Clone the repository at the base commit
ARG BASE_COMMIT=64ac0919840381ce708c5ce4bddd96f9b20ef4aa
RUN git clone --filter=blob:none https://github.com/apache/airflow.git /workspace/airflow && \
    cd /workspace/airflow && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/airflow

# Install UI dependencies using pnpm
RUN cd airflow-core/src/airflow/ui && pnpm install --frozen-lockfile

# Create logs directory
RUN mkdir -p /logs/verifier

# Keep container alive
CMD ["sleep", "infinity"]

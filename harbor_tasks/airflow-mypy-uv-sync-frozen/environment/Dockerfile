FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pyyaml==6.0.2

WORKDIR /workspace

RUN git clone --filter=blob:none --no-checkout https://github.com/apache/airflow.git airflow && \
    cd airflow && \
    git fetch --depth 1 origin 5560e7cf433d2a1a6b37865ad511301f76fb420e && \
    git sparse-checkout init --cone && \
    git sparse-checkout set scripts/ci/prek airflow-core/src/airflow contributing-docs task-sdk/src dev/breeze/src && \
    git checkout 5560e7cf433d2a1a6b37865ad511301f76fb420e && \
    git config user.email "task@harbor.local" && \
    git config user.name "Task Runner"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow

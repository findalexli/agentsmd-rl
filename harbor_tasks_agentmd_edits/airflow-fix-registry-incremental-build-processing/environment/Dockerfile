FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone at base commit (airflow is a huge monorepo)
RUN git init /workspace/airflow && \
    cd /workspace/airflow && \
    git remote add origin https://github.com/apache/airflow.git && \
    git fetch --depth=1 origin af239855e76fbf076fe226ee5fb044ab4965cef5 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/airflow

# Install deps needed by test_outputs.py (pydantic for merge_registry_data validation)
RUN pip install --no-cache-dir pydantic

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier

# Apache Airflow Breeze CI Command Fix Task
FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install git and dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /workspace

# Clone Airflow repo at base commit (shallow clone with only the needed files)
ARG BASE_COMMIT=15faf7eadfaa8e5ca9788b926c44563178d31ffb
RUN git clone --filter=blob:none --no-checkout https://github.com/apache/airflow.git /workspace/airflow \
    && cd /workspace/airflow \
    && git sparse-checkout init --cone \
    && git sparse-checkout set dev/breeze \
    && git checkout ${BASE_COMMIT}

# Install dev/breeze dependencies
WORKDIR /workspace/airflow/dev/breeze
RUN pip install -e . --no-deps && pip install click filelock black flit

# Ensure logs directory exists
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow

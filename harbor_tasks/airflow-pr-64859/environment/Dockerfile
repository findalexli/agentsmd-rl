FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone the repo with blob filter for faster clone
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow

WORKDIR /workspace/airflow

# Checkout the base commit (before the fix)
RUN git checkout fc315f3d77f4029c469ebc7d8be35983edcbfc27

# Install dependencies needed by the script and tests
RUN pip install --no-cache-dir \
    tomli>=2.0.1 \
    rich>=13.6.0 \
    packaging>=25 \
    pyyaml \
    pytest

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow

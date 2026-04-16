FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone airflow repository at the base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout 7a998637b743eeed20d82770dc0c0f2fbe12123b

# Install pytest and ruff for running tests
RUN pip install --no-cache-dir pytest ruff

# Create logs directory for verifier output
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow

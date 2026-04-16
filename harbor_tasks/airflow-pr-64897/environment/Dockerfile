FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone the repository at the base commit
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout 40902de7e7d31225410db85e3707aaf494ab5e90

WORKDIR /workspace/airflow

# Install the openlineage provider with minimal dependencies for testing
RUN pip install --no-cache-dir \
    pytest \
    attrs \
    openlineage-python>=1.0.0

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set PYTHONPATH to include the openlineage provider source
ENV PYTHONPATH=/workspace/airflow/providers/openlineage/src:$PYTHONPATH

FROM python:3.12-slim

# Install required dependencies for testing shell scripts
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    dpkg \
    ca-certificates \
    coreutils \
    shellcheck \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Clone the airflow repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git && \
    cd airflow && \
    git fetch --depth=2 origin c4a209ba0ec1749ce0d0ac561fb22feba5bad567 1b2893300d8b6c3ae656b8e7d9a44138b663d633 && \
    git checkout c4a209ba0ec1749ce0d0ac561fb22feba5bad567

WORKDIR /workspace/airflow

# Install pytest for test runner
RUN pip install --no-cache-dir pytest

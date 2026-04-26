FROM python:3.12-slim

# Install dependencies: git, helm, and other tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    gnupg \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install Helm
RUN curl -fsSL https://get.helm.sh/helm-v3.14.0-linux-amd64.tar.gz | tar xz -C /tmp \
    && mv /tmp/linux-amd64/helm /usr/local/bin/helm \
    && rm -rf /tmp/linux-amd64

# Install uv for Python package management
RUN pip install uv

# Clone Airflow repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=8dc4305675a6817f55d5ebcc88367859da21beca
RUN git init /workspace/airflow && \
    cd /workspace/airflow && \
    git remote add origin https://github.com/apache/airflow.git && \
    git fetch --depth=1 origin 8dc4305675a6817f55d5ebcc88367859da21beca && \
    git checkout FETCH_HEAD

WORKDIR /workspace/airflow

# Install helm-test dependencies
# The helm-tests use pytest and dependencies defined in the repo
RUN uv pip install --system pytest pyyaml jmespath jsonschema kubernetes behave

# Create verifier logs directory
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]

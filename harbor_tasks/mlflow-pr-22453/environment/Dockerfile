FROM python:3.12-slim

WORKDIR /workspace

# Install git and basic tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Clone the repo
RUN git clone --filter=blob:none --depth=1 https://github.com/mlflow/mlflow.git mlflow_repo
WORKDIR /workspace/mlflow_repo

# Checkout the base commit
RUN git fetch --filter=blob:none https://github.com/mlflow/mlflow.git 44600fe263c57bc94b663ff483f6583345e1b101 && \
    git checkout 44600fe263c57bc94b663ff483f6583345e1b101

# Install local mlflow (editable) with required extra
RUN pip install --no-cache-dir -e /workspace/mlflow_repo \
    pytest==8.3.4 \
    opentelemetry-api==1.29.0 \
    opentelemetry-sdk==1.29.0 \
    opentelemetry-proto==1.29.0 \
    pydantic==2.10.6 \
    protobuf==5.29.2

# Create log directory
RUN mkdir -p /logs/verifier

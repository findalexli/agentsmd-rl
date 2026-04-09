FROM python:3.12-slim

# Install git and required tools
RUN apt-get update && apt-get install -y \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

# Clone the dagster repository at the base commit (before the fix)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/dagster-io/dagster.git && \
    cd dagster && \
    git checkout bff96c1a777298c1bf027e7eb1cedb556ddbe2ee

# Copy solve.sh to the expected location in the container
COPY solve.sh /workspace/task/solve.sh

# Install the dagster-k8s package and test dependencies
WORKDIR /workspace/dagster
RUN pip install -e python_modules/libraries/dagster-k8s && \
    pip install pytest

# Create logs directory for test outputs
RUN mkdir -p /logs/verifier

WORKDIR /workspace/dagster

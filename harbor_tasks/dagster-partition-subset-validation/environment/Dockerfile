FROM python:3.12-slim

# Install git and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    make \
    curl \
    && rm -rf /var/lib/apt-get/lists/*

# Set up working directory
WORKDIR /workspace

# Clone the repository at base commit
# Using filter=blob:none for faster cloning
RUN git clone --filter=blob:none https://github.com/dagster-io/dagster.git dagster && \
    cd dagster && \
    git checkout 3fc2834d865a46aa88a3271159edf52c5a0f07f2

# Create logs directory for verifier and task structure for test.sh
RUN mkdir -p /logs/verifier /workspace/task && ln -s /tests /workspace/task/tests

# Install uv for package management (as per repo conventions)
RUN pip install uv

# Install dagster package dependencies
WORKDIR /workspace/dagster/python_modules/dagster
RUN uv pip install -e . --system

# Install pytest and testing dependencies
RUN uv pip install pytest --system

WORKDIR /workspace

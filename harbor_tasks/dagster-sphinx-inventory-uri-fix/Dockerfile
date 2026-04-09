FROM python:3.12-slim

# Install git and dependencies
RUN apt-get update && apt-get install -y git make && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone the repository at base commit
RUN git clone --filter=blob:none https://github.com/dagster-io/dagster.git dagster && \
    cd dagster && \
    git checkout b079ffcc0a70907d75cae2c276a1bed4d0b90139

# Install uv for package management (as per repo conventions)
RUN pip install uv -q

# Install dagster packages in correct order
RUN uv pip install --system -e /workspace/dagster/python_modules/dagster-pipes && \
    uv pip install --system -e /workspace/dagster/python_modules/libraries/dagster-shared && \
    uv pip install --system -e /workspace/dagster/python_modules/dagster

# Install sphinx, docutils, and testing tools
RUN uv pip install --system sphinx docutils pytest "ruff==0.15.0"

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory to the repo
WORKDIR /workspace/dagster

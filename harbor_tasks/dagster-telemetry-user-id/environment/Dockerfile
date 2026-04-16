FROM python:3.12-slim

WORKDIR /workspace

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

# Clone dagster repo at base commit (using shallow clone for speed)
ARG BASE_COMMIT=1bccaaca43c35a850e824e65a70655ab9f0136b8
RUN git clone --filter=blob:none --depth=100 https://github.com/dagster-io/dagster.git /workspace/dagster \
    && cd /workspace/dagster \
    && git checkout ${BASE_COMMIT}

# Set working directory to dagster repo
WORKDIR /workspace/dagster

# Install uv and dependencies for testing
RUN pip install uv pytest pyyaml ruff

# Pre-install dagster packages in editable mode for faster testing
RUN cd /workspace/dagster/python_modules/libraries/dagster-shared && uv pip install -e . --system
RUN cd /workspace/dagster/python_modules/dagster && uv pip install -e . --system

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["/bin/bash"]

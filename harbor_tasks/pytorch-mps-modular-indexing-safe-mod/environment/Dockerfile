FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone PyTorch at the base commit (before the fix)
RUN git init /workspace/pytorch && \
    cd /workspace/pytorch && \
    git remote add origin https://github.com/pytorch/pytorch.git && \
    git fetch --depth=1 origin 483b55d84c74b92b3c2c67be4b9b7c7359ec2bbc && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/pytorch

# Install minimal Python deps needed for codegen testing
# We only need sympy for the MetalExprPrinter tests
# ruff is needed for linting checks
RUN pip install --no-cache-dir sympy filelock typing-extensions pyyaml ruff

# Set PYTHONPATH so torch internals can be imported for codegen testing
ENV PYTHONPATH="/workspace/pytorch"

# Configure git
RUN git config --global user.email "test@test.com" \
    && git config --global user.name "Test User"
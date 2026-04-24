FROM python:3.12-slim

WORKDIR /workspace

# Install git and dependencies needed for cloning
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone the pulumi repository at the base commit
ARG BASE_COMMIT=e0c59e5dd6bb3b55d16113be96e338bce3172cf5
RUN git clone --filter=blob:none https://github.com/pulumi/pulumi.git /workspace/pulumi && \
    cd /workspace/pulumi && \
    git checkout ${BASE_COMMIT}

# Install Python SDK dependencies (if any)
WORKDIR /workspace/pulumi/sdk/python
RUN pip install -e . --quiet || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/pulumi

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages mypy ruff 2>/dev/null || pip install --no-cache-dir mypy ruff

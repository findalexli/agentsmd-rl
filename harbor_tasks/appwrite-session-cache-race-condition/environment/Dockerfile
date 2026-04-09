FROM phpswoole/swoole:php8.3-cli

# Install Python for pytest runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment for pytest
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel

# Pre-install pytest (test runner uses this)
RUN pip install pytest pyyaml

# Set working directory
WORKDIR /workspace

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Clone Appwrite repo at base commit (will be overridden by task)
# Using filter=blob:none for faster clone
RUN git clone --filter=blob:none https://github.com/appwrite/appwrite.git /workspace/appwrite

WORKDIR /workspace/appwrite

# Default: checkout base commit (task will override if needed)
ARG BASE_COMMIT=7eef845556510ebd068298e3b3c0578230ac2875
RUN git checkout ${BASE_COMMIT} || true

# Note: Full Appwrite requires Redis, MariaDB, etc.
# This Dockerfile sets up the PHP environment for code inspection tests.
# For actual race condition verification, full stack would be needed,
# but we verify via code structure analysis and pattern validation.

WORKDIR /workspace

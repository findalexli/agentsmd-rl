FROM python:3.12-slim

# Install git (needed for the patches system this task modifies)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Clone electron repository at base commit
ARG BASE_COMMIT=abfc0ade63a0f43f3458496b365ab04f68754b84
RUN git clone --filter=blob:none https://github.com/electron/electron.git /workspace/electron \
    && cd /workspace/electron \
    && git checkout ${BASE_COMMIT}

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Create /workspace/task directory and symlink tests
RUN mkdir -p /workspace/task && ln -s /tests /workspace/task/tests

WORKDIR /workspace

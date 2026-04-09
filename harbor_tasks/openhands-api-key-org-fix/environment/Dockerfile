FROM python:3.12-slim

# Install git and other necessary tools
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create workspace directory
WORKDIR /workspace

# Clone the OpenHands repository at base commit
# Using --filter=blob:none to get a shallow clone with tree history
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git

# Checkout the base commit (before the fix)
WORKDIR /workspace/OpenHands
RUN git checkout 06cd53d752b022a7ae3676ab17c029f1f810c892

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Create directory structure for test compatibility
RUN mkdir -p /workspace/task && ln -s /tests /workspace/task/tests

# Set working directory for the task
WORKDIR /workspace

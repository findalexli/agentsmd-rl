FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Create a dummy workspace for template validation
RUN mkdir -p /workspace/dummy-repo && \
    cd /workspace/dummy-repo && \
    git init && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/dummy-repo

# Create a simple Python file for testing
RUN echo 'def add(a, b):\n    return a + b\n\ndef broken_add(a, b):\n    return a  # Bug: ignores b\n' > /workspace/dummy-repo/math_ops.py && \
    git add . && \
    git commit -m "Initial commit"

# Verifier output directory
RUN mkdir -p /logs/verifier

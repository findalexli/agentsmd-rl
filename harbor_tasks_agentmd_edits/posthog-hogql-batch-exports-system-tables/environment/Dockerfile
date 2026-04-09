FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/PostHog/posthog.git /workspace/posthog && \
    cd /workspace/posthog && \
    git checkout 05600e36c426ef5128519dc60c7ec1d416da8bc0 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/posthog

ENV PYTHONPATH="/workspace/posthog"

# Install minimal deps needed by test_outputs.py
RUN pip install --no-cache-dir pytest parameterized pytest-json-ctrf

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier

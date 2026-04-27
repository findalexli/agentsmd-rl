FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        grep \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        PyYAML==6.0.2

WORKDIR /workspace

RUN git init /workspace/posthog && \
    cd /workspace/posthog && \
    git remote add origin https://github.com/PostHog/posthog.git && \
    git fetch --depth=1 origin f8208b0d7194bdfdccb95cc8d0060978734bb981 && \
    git checkout FETCH_HEAD && \
    git config user.email "task@example.com" && \
    git config user.name "Task"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/posthog

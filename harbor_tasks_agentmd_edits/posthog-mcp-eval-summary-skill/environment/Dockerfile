FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential && \
    rm -rf /var/lib/apt/lists/*

# Clone PostHog monorepo at base commit
RUN git clone --filter=blob:none https://github.com/PostHog/posthog.git /workspace/posthog && \
    cd /workspace/posthog && \
    git checkout 69f47d880ee65fd3e9a769a12a7d80997dea555e && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/posthog

# Install minimal deps for test runner (pyyaml for YAML parsing)
RUN pip install --no-cache-dir pyyaml

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier

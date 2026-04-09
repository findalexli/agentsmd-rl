FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (treeless clone for large monorepo)
RUN git clone --filter=blob:none https://github.com/PostHog/posthog.git /workspace/posthog && \
    cd /workspace/posthog && \
    git checkout bfcaca7712c5a0c3b4b24d2d3f76e79fefc62d87 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/posthog

# Install deps needed by test_outputs.py (Jinja2 for template validation, PyYAML for frontmatter)
RUN pip install --no-cache-dir jinja2 pyyaml

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier

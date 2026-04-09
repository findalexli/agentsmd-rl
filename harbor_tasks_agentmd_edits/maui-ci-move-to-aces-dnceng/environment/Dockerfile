FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/dotnet/maui.git /workspace/maui && \
    cd /workspace/maui && \
    git checkout bfe8e58dcab8b030d6d87edf30fbe3f53827795d && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/maui

# Install PyYAML for YAML parsing in tests
RUN pip install --no-cache-dir pyyaml

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier

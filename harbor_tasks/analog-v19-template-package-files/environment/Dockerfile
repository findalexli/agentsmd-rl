FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install Python for pytest test runner
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip && \
    rm -rf /var/lib/apt/lists/* && \
    ln -sf /usr/bin/python3 /usr/bin/python

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/analogjs/analog.git /workspace/analog && \
    cd /workspace/analog && \
    git checkout 3f475f278250ab3c2b5da22f03d9e2b7ccbf6000 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/analog

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier

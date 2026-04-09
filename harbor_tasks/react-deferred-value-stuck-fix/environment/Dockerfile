FROM node:20-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git python3 python3-pip python3-venv ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Clone React at base commit (shallow clone for speed)
RUN git clone --depth=500 --single-branch https://github.com/facebook/react.git /workspace/react && \
    cd /workspace/react && \
    git checkout ed69815cebae33b0326cc69faa90f813bb924f3b && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/react

# Install dependencies (needed for running yarn test)
RUN yarn install --network-timeout 600000 2>&1 | tail -5

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier

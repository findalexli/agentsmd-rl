FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates nodejs gnupg && \
    rm -rf /var/lib/apt/lists/*

# Install Helm (for CI pass_to_pass helm unit tests)
RUN curl -fsSL https://get.helm.sh/helm-v3.11.1-linux-amd64.tar.gz -o /tmp/helm.tgz && \
    tar -xzf /tmp/helm.tgz -C /usr/local/bin linux-amd64/helm --strip-components=1 && \
    rm /tmp/helm.tgz && \
    helm version

# Enable corepack for pnpm
RUN corepack enable pnpm

RUN pip install --no-cache-dir pytest pytest-json-ctrf

RUN git init /workspace/litellm && \
    cd /workspace/litellm && \
    git remote add origin https://github.com/BerriAI/litellm.git && \
    git fetch --depth=1 origin a38993b871a32090caea0941427a8bc5489a5c02 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/litellm

RUN mkdir -p /logs/verifier

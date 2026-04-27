FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        nodejs \
        npm \
    && rm -rf /var/lib/apt/lists/* \
    && node --version

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace

# Fetch the Ghost source tree at the exact base commit (parent of the merge).
# Use the GitHub tarball: avoids cloning the full history (~500MB+) while
# keeping every file the agent might need to read or edit.
ARG BASE_COMMIT=dc2ae810f4d630fb0367d996f2e782f81db88034
RUN curl -sSL "https://github.com/TryGhost/Ghost/archive/${BASE_COMMIT}.tar.gz" \
        -o /tmp/ghost.tar.gz && \
    tar -xzf /tmp/ghost.tar.gz -C /workspace && \
    mv "/workspace/Ghost-${BASE_COMMIT}" /workspace/Ghost && \
    rm /tmp/ghost.tar.gz

WORKDIR /workspace/Ghost

RUN mkdir -p /logs/verifier

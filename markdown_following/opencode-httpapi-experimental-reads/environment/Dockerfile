FROM oven/bun:1.3.13-debian

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        ripgrep \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# pytest pinned for reproducible reward computation
RUN pip3 install --break-system-packages \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace

# Pin to the parent of the merge commit for PR anomalyco/opencode#24365
ARG REPO_URL=https://github.com/anomalyco/opencode.git
ARG BASE_COMMIT=f5dce6d960ea44d3a77cfe868b8209b44a866edb

RUN git clone --filter=blob:none ${REPO_URL} opencode \
    && cd opencode \
    && git fetch --depth=1 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/opencode

# Install workspace deps. This is a large monorepo; allow time.
# --frozen-lockfile keeps versions deterministic.
RUN bun install --frozen-lockfile

RUN mkdir -p /logs/verifier

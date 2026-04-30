FROM node:22.14.0-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        curl \
        build-essential \
        python3-dev \
        libsecret-1-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.5

RUN corepack enable && corepack prepare yarn@4.8.1 --activate

WORKDIR /workspace

# Shallow clone backstage at the base commit
RUN git init /workspace/backstage && \
    cd /workspace/backstage && \
    git remote add origin https://github.com/backstage/backstage.git && \
    git fetch --depth=1 origin 98d9a75dc2966be209bfea336a482a2266c3267d && \
    git checkout FETCH_HEAD && \
    git config user.email "task@local" && \
    git config user.name "task"

WORKDIR /workspace/backstage

# Install dependencies. Backstage uses yarn-berry workspaces.
# This downloads all workspace deps; large but unavoidable for monorepo.
ENV YARN_ENABLE_TELEMETRY=0
RUN yarn install --immutable

RUN mkdir -p /logs/verifier

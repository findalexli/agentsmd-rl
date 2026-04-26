FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

RUN git init /workspace/electric && \
    cd /workspace/electric && \
    git remote add origin https://github.com/electric-sql/electric.git && \
    git fetch --depth=1 origin 617b429f0f8b9b78bed42b897092e065cf993e35 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/electric

RUN mkdir -p /logs/verifier

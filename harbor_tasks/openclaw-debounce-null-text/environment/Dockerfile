FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

RUN git init /workspace/openclaw && \
    cd /workspace/openclaw && \
    git remote add origin https://github.com/openclaw/openclaw.git && \
    git fetch --depth=1 origin 756df2e9554da097679e6c4d3c75deff025098b9 && \
    git checkout FETCH_HEAD

# Install minimal deps (agent fills in specifics)



RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/openclaw
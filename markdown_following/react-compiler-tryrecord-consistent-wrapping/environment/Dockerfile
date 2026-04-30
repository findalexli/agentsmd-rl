FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone React repo at base commit
WORKDIR /workspace
RUN git init /workspace/react && \
    cd /workspace/react && \
    git remote add origin https://github.com/facebook/react.git && \
    git fetch --depth=1 origin cebe42e24521ce02bf427fd482009d01e1466277 && \
    git checkout FETCH_HEAD && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git config user.email "agent@test" && \
    git config user.name "Agent" && \
    git commit -m "snapshot"

WORKDIR /workspace/react

RUN mkdir -p /logs/verifier

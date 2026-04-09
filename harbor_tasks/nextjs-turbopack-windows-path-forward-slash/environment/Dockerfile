FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone Next.js at the base commit (before the fix)
RUN git init /workspace/next.js && \
    cd /workspace/next.js && \
    git remote add origin https://github.com/vercel/next.js.git && \
    git fetch --depth=1 origin a21f3f4008a7d4c1778649d533de76b62dffabaa && \
    git checkout FETCH_HEAD

RUN cd /workspace/next.js && \
    git config user.name "Agent" && \
    git config user.email "agent@test.com"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/next.js

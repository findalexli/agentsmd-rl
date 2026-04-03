FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone efcore at base commit (large repo — depth=1)
RUN git init /workspace/efcore && \
    cd /workspace/efcore && \
    git remote add origin https://github.com/dotnet/efcore.git && \
    git fetch --depth=1 origin dd9da572feeb9851a0c4a6579b05163c48574c29 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/efcore

# No build deps needed — tests check file contents only (C# repo, no .NET SDK)
RUN mkdir -p /logs/verifier

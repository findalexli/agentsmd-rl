FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (monorepo — use blob filter)
RUN git clone --filter=blob:none https://github.com/dotnet/maui.git /workspace/maui && \
    cd /workspace/maui && \
    git checkout 1789d47932dd78983d7c68101f154f372f60e151 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/maui

RUN mkdir -p /logs/verifier

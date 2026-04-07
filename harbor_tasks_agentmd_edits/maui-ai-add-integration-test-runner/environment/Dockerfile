FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates tmux && \
    rm -rf /var/lib/apt/lists/*

# dotnet/maui is huge — shallow clone at base commit
RUN git init /workspace/maui && \
    cd /workspace/maui && \
    git remote add origin https://github.com/dotnet/maui.git && \
    git fetch --depth=1 origin 71e5c2f595d7cc104adc18753a646e9c557c10da && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/maui

# No extra deps needed — tests read file contents and parse XML
RUN mkdir -p /logs/verifier

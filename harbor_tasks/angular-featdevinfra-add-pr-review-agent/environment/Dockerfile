FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates jq tmux && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone angular at base commit (pre-PR)
RUN git init /workspace/angular && \
    cd /workspace/angular && \
    git remote add origin https://github.com/angular/angular.git && \
    git fetch --depth=1 origin 5e21431ba34d82c189dc4a7536f49dcfbc5bda4d && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/angular

RUN mkdir -p /logs/verifier

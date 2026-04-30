FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone — huge monorepo, only need file content for tests
RUN git init /workspace/cypress && \
    cd /workspace/cypress && \
    git remote add origin https://github.com/cypress-io/cypress.git && \
    git fetch --depth=1 origin d9cf1844842203937859811c814845fb42d7683a && \
    git checkout d9cf1844842203937859811c814845fb42d7683a && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/cypress

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier

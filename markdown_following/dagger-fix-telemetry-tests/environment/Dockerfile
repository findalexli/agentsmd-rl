FROM golang:1.24-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux \
        python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

RUN git init /workspace/dagger && \
    cd /workspace/dagger && \
    git remote add origin https://github.com/dagger/dagger.git && \
    git fetch --depth=1 origin 02b858d8f7368cb107374df899af3a90ffff9bbd && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/dagger

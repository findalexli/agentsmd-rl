FROM rust:slim-bookworm

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential python3 tmux pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

RUN mkdir -p /logs/verifier

WORKDIR /workspace
RUN git init . && \
    git remote add origin https://github.com/astral-sh/uv.git && \
    git fetch --depth=1 origin 87950df2cce7a219a617a1efc4807d8075986e5b && \
    git checkout FETCH_HEAD

# rustc is available from the base image for standalone compilation tests

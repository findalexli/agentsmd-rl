FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow — large Rust monorepo)
RUN git init /workspace/quickwit && \
    cd /workspace/quickwit && \
    git remote add origin https://github.com/quickwit-oss/quickwit.git && \
    git fetch --depth=1 origin eca4f763214604006262fc6a29dcf59c754813e3 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/quickwit

# Install minimal deps needed by test_outputs.py
RUN pip install --no-cache-dir tomli

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
